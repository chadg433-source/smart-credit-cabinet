import pathlib
import sys

# чтобы `import app...` работал при запуске pytest из любой папки
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.services import llm  # noqa: E402


def make_facts(**overrides):
    base = dict(
        decision="APPROVED_WITH_CONDITIONS",
        reason="Средняя платежеспособность. Сумма снижена.",
        requested_amount=1_000_000.0,
        offered_amount=700_000.0,
        term_months=36,
        annual_rate=15.0,
        monthly_revenue=850_000.0,
        monthly_expenses=500_000.0,
        monthly_loan_payments=50_000.0,
    )
    base.update(overrides)
    return llm.build_facts(**base)


def setup_function():
    llm._cache.clear()
    llm._status_cache.update({"at": 0.0, "value": None})


def _ready(monkeypatch):
    monkeypatch.setattr(llm, "llm_status", lambda: {"available": True, "status": "ready"})


def test_build_facts_computes_numbers_in_code():
    facts = make_facts()
    assert facts["monthly_profit"] == 350_000.0
    assert facts["loan_payments_share_percent"] == 6
    assert facts["decision"] == "одобрено на других условиях"


def test_build_facts_zero_revenue_does_not_crash():
    facts = make_facts(monthly_revenue=0.0, monthly_expenses=0.0)
    assert facts["loan_payments_share_percent"] == 0


def test_fallback_when_llm_down(monkeypatch):
    _ready(monkeypatch)

    def boom(messages):
        raise ConnectionError("LLM недоступна")

    monkeypatch.setattr(llm, "_call_llm", boom)
    res = llm.explain_decision("k1", make_facts())
    assert res["source"] == "fallback"
    assert res["model"] is None
    assert "Сумма снижена" in res["text"]


def test_fallback_when_llm_returns_empty(monkeypatch):
    _ready(monkeypatch)
    monkeypatch.setattr(llm, "_call_llm", lambda m: "<think>думаю</think>   ")
    res = llm.explain_decision("k2", make_facts())
    assert res["source"] == "fallback"


def test_llm_ok_strips_think_and_caches(monkeypatch):
    _ready(monkeypatch)
    calls = []

    def fake(messages):
        calls.append(messages)
        return "<think>рассуждение</think>Банк предложил меньшую сумму."

    monkeypatch.setattr(llm, "_call_llm", fake)
    first = llm.explain_decision("k3", make_facts())
    second = llm.explain_decision("k3", make_facts())
    assert first["text"] == "Банк предложил меньшую сумму."
    assert first["source"] == "llm"
    assert first == second
    assert len(calls) == 1  # второй вызов взят из кэша


def test_prompt_contains_only_prepared_facts():
    prompt = llm.build_user_prompt(make_facts())
    assert "700 000 руб." in prompt
    assert "6% выручки" in prompt


def test_fallback_text_has_no_double_dots(monkeypatch):
    _ready(monkeypatch)
    monkeypatch.setattr(llm, "_call_llm", lambda m: (_ for _ in ()).throw(RuntimeError("x")))
    text = llm.explain_decision("k4", make_facts())["text"]
    assert ".." not in text
    assert "700 000 руб." in text


def test_llm_not_ready_skips_model_call(monkeypatch):
    monkeypatch.setattr(llm, "llm_status", lambda: {"available": False, "status": "loading"})

    def must_not_be_called(messages):
        raise AssertionError("модель не должна вызываться, пока она не готова")

    monkeypatch.setattr(llm, "_call_llm", must_not_be_called)
    res = llm.explain_decision("k5", make_facts())
    assert res["source"] == "fallback"


def test_status_unavailable_when_nothing_listens(monkeypatch):
    # порт 9 (discard) почти всегда закрыт: соединение отклоняется сразу
    monkeypatch.setattr(llm.settings, "llm_url", "http://127.0.0.1:9")
    assert llm.llm_status() == {"available": False, "status": "unavailable"}
