"""Объяснение кредитного решения простым языком с помощью локальной LLM.

Работает с любым сервером, у которого есть OpenAI-совместимый API
(`/v1/chat/completions`) и `/health`: llama.cpp, vLLM, внутренний сервис банка.
Адрес задаётся переменной окружения LLM_URL.

Принципы:
- LLM НЕ принимает решений и не меняет статус заявки. Она только пересказывает
  уже принятое решение.
- Все числа считаются кодом, в промпт попадают только готовые значения из БД.
  Свободный текст пользователя (например, purpose) в промпт не передаётся.
- Если модель недоступна, тормозит или вернула пустой ответ, возвращается
  шаблонный текст. Основной сценарий от LLM не зависит.
- Используется только стандартная библиотека Python: новые зависимости
  в pyproject.toml / uv.lock не нужны.
"""
import json
import logging
import re
import time
import urllib.error
import urllib.request

from app.config import settings

log = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Ты помощник кредитного кабинета для малого бизнеса. "
    "Объясни предпринимателю решение банка по заявке простым языком, без жаргона. "
    "Используй ТОЛЬКО цифры из данных ниже, ничего не считай и не придумывай. "
    "Ответ: 3-4 коротких предложения на русском: что решил банк, почему, "
    "что можно сделать дальше. "
    "Ты не принимаешь решений и ничего не обещаешь."
)

DECISION_LABELS = {
    "APPROVED": "одобрено",
    "APPROVED_WITH_CONDITIONS": "одобрено на других условиях",
    "REJECTED": "отказ",
}

# Кэш в памяти: ключ - id решения. Повторный клик не ждёт генерацию заново.
# Сбрасывается при перезапуске бэкенда, для MVP этого достаточно.
_cache: dict[str, dict] = {}


def build_facts(
    *,
    decision: str,
    reason: str,
    requested_amount: float,
    offered_amount: float,
    term_months: int,
    annual_rate: float,
    monthly_revenue: float,
    monthly_expenses: float,
    monthly_loan_payments: float,
) -> dict:
    """Собирает факты для объяснения. Все расчёты делает код, а не модель."""
    loan_share = (
        round(monthly_loan_payments / monthly_revenue * 100) if monthly_revenue else 0
    )
    return {
        "decision": DECISION_LABELS.get(decision, decision),
        "reason": reason,
        "requested_amount": requested_amount,
        "offered_amount": offered_amount,
        "term_months": term_months,
        "annual_rate": annual_rate,
        "monthly_revenue": monthly_revenue,
        "monthly_profit": monthly_revenue - monthly_expenses,
        "loan_payments_share_percent": loan_share,
    }


def _fmt_rub(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ") + " руб."


def build_user_prompt(facts: dict) -> str:
    return "\n".join(
        [
            f"Решение банка: {facts['decision']}",
            f"Причина (из скоринга): {facts['reason']}",
            f"Запрошенная сумма: {_fmt_rub(facts['requested_amount'])}",
            f"Предложенная сумма: {_fmt_rub(facts['offered_amount'])}",
            f"Срок: {facts['term_months']} мес.",
            f"Ставка: {facts['annual_rate']}% годовых",
            f"Выручка в месяц: {_fmt_rub(facts['monthly_revenue'])}",
            f"Прибыль в месяц: {_fmt_rub(facts['monthly_profit'])}",
            f"Платежи по текущим кредитам: {facts['loan_payments_share_percent']}% выручки",
        ]
    )


def fallback_text(facts: dict) -> str:
    """Шаблонный текст на случай, если LLM недоступна."""
    reason = facts["reason"].strip().rstrip(".")
    text = f"Решение по заявке: {facts['decision']}. {reason}."
    if facts["offered_amount"] and facts["offered_amount"] != facts["requested_amount"]:
        text += f" Предложенная сумма: {_fmt_rub(facts['offered_amount'])}"
    return text


def _call_llm(messages: list[dict]) -> str:
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 250,
        "stream": False,
    }
    req = urllib.request.Request(
        f"{settings.llm_url.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=settings.llm_timeout_seconds) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


# Статус LLM кэшируется на несколько секунд, чтобы фронтенд мог опрашивать его часто.
_STATUS_TTL_SECONDS = 5.0
_status_cache: dict = {"at": 0.0, "value": None}


def _probe_llm() -> dict:
    try:
        with urllib.request.urlopen(
            f"{settings.llm_url.rstrip('/')}/health", timeout=2
        ) as resp:
            if resp.status == 200:
                return {"available": True, "status": "ready"}
            return {"available": False, "status": "unavailable"}
    except urllib.error.HTTPError as e:
        # llama.cpp отвечает 503, пока модель загружается в память
        if e.code == 503:
            return {"available": False, "status": "loading"}
        return {"available": False, "status": "unavailable"}
    except Exception:
        return {"available": False, "status": "unavailable"}


def llm_status() -> dict:
    """{"available": bool, "status": "ready" | "loading" | "unavailable"}. Никогда не бросает исключений."""
    now = time.monotonic()
    if _status_cache["value"] is None or now - _status_cache["at"] > _STATUS_TTL_SECONDS:
        _status_cache["value"] = _probe_llm()
        _status_cache["at"] = now
    return _status_cache["value"]


def explain_decision(cache_key: str, facts: dict) -> dict:
    if cache_key in _cache:
        return _cache[cache_key]
    if not llm_status()["available"]:
        # модель не запущена или ещё грузится: не ждём таймаут, сразу шаблонный текст
        return {"text": fallback_text(facts), "source": "fallback", "model": None}
    try:
        raw = _call_llm(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(facts)},
            ]
        )
        # на случай моделей, которые рассуждают вслух в тегах <think>
        text = re.sub(r"<think>.*?</think>", "", raw, flags=re.S).strip()
        if not text:
            raise ValueError("пустой ответ модели")
        result = {"text": text, "source": "llm", "model": settings.llm_model}
        _cache[cache_key] = result
        return result
    except Exception as e:  # любая проблема с LLM не должна ломать сценарий
        log.warning("LLM недоступна, используется шаблонный текст: %s", e)
        return {"text": fallback_text(facts), "source": "fallback", "model": None}
