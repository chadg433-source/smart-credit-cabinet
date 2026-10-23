"""Объяснение кредитного решения простым языком с помощью локальной LLM (Ollama).

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


def _call_ollama(messages: list[dict]) -> str:
    payload = {
        "model": settings.llm_model,
        "stream": False,
        "think": False,  # у моделей с режимом рассуждений отключаем его ради скорости
        "options": {"temperature": 0.2, "num_predict": 250},
        "messages": messages,
    }
    req = urllib.request.Request(
        f"{settings.llm_base_url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=settings.llm_timeout_seconds) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["message"]["content"]


def explain_decision(cache_key: str, facts: dict) -> dict:
    if cache_key in _cache:
        return _cache[cache_key]
    try:
        raw = _call_ollama(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(facts)},
            ]
        )
        # на случай старых версий Ollama / моделей, которые всё равно рассуждают вслух
        text = re.sub(r"<think>.*?</think>", "", raw, flags=re.S).strip()
        if not text:
            raise ValueError("пустой ответ модели")
        result = {"text": text, "source": "llm", "model": settings.llm_model}
        _cache[cache_key] = result
        return result
    except Exception as e:  # любая проблема с LLM не должна ломать сценарий
        log.warning("LLM недоступна, используется шаблонный текст: %s", e)
        return {"text": fallback_text(facts), "source": "fallback", "model": None}
