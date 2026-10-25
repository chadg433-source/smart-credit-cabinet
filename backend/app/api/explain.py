from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, Business, CreditDecision
from app.services.llm import build_facts, explain_decision, llm_status

router = APIRouter(tags=["LLM"])


class ExplainResponse(BaseModel):
    text: str
    source: str  # "llm" - ответ модели, "fallback" - шаблонный текст
    model: str | None = None


class LlmStatusResponse(BaseModel):
    available: bool
    status: str  # "ready" | "loading" | "unavailable"


@router.get("/llm/status", response_model=LlmStatusResponse)
def get_llm_status():
    """Доступна ли LLM. Фронтенд по этому полю включает или отключает кнопку ИИ.
    Не зависит от /health и никогда не падает, даже если LLM выключена."""
    return llm_status()


@router.post("/applications/{application_id}/explain", response_model=ExplainResponse)
def explain_application(application_id: UUID, db: Session = Depends(get_db)):
    """Объясняет решение по заявке простым языком. Данные только читает."""
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    decision = (
        db.query(CreditDecision)
        .filter(CreditDecision.application_id == application_id)
        .order_by(CreditDecision.created_at.desc())
        .first()
    )
    if not decision:
        raise HTTPException(status_code=409, detail="Решение по заявке ещё не принято")

    business = db.query(Business).filter(Business.id == app.business_id).first()
    if not business:
        raise HTTPException(status_code=500, detail="Ошибка данных: бизнес не найден")

    facts = build_facts(
        app_status=str(app.status),
        decision=decision.decision,
        reason=decision.reason,
        requested_amount=float(app.requested_amount),
        offered_amount=float(decision.offered_amount or 0),
        term_months=app.requested_term_months,
        annual_rate=float(decision.offered_rate or 0),
        monthly_revenue=float(business.monthly_revenue),
        monthly_expenses=float(business.monthly_expenses),
        monthly_loan_payments=float(business.existing_monthly_loan_payments),
    )
    return explain_decision(str(decision.id), facts)
