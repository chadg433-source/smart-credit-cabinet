from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ApplicationCreate, ApplicationResponse
from app.models import Application, ApplicationStatusHistory, Business, CreditProduct, ScoringResult, CreditDecision
from app.services.external_checks import run_external_checks
from app.services.scoring import calculate_scoring
from app.services.state_machine import assert_transition, Status
from decimal import Decimal
router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/", response_model=ApplicationResponse)
def create_application(app_in: ApplicationCreate, db: Session = Depends(get_db)):
    new_app = Application(
        business_id=app_in.business_id,
        credit_product_id=app_in.credit_product_id,
        requested_amount=app_in.requested_amount,
        requested_term_months=app_in.requested_term_months,
        purpose=app_in.purpose,
        status= "DRAFT"
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app


@router.get("/", response_model=list[ApplicationResponse])
def get_applications(db: Session = Depends(get_db)):
    return db.query(Application).all()

@router.post("/{application_id}/submit", response_model=ApplicationResponse)
def submit_application(application_id: UUID, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Заявка не найдена")


    try:
        assert_transition(app.status, Status.SUBMITTED.value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    checks_result = run_external_checks(str(app.business_id))

    if not checks_result["is_all_passed"]:
        old_status = app.status
        app.status = Status.NEED_MORE_INFO.value
        history = ApplicationStatusHistory(
            application_id=app.id,
            old_status=old_status,
            new_status=app.status,
            comment= "Требуется дополнительная проверка"

        )
        db.add(history)
        db.commit()
        db.refresh(app)
        return app

    old_status = app.status
    app.status = Status.SUBMITTED.value
    history = ApplicationStatusHistory(
        application_id=app.id,
        old_status=old_status,
        new_status=app.status,
        comment="Заявка отправлена на проверку"
    )
    db.add(history)
    db.commit()
    db.refresh(app)
    return app


@router.post("/{application_id}/process", response_model=ApplicationResponse)
def process_application(application_id: UUID, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    if app.status not in [Status.NEED_MORE_INFO.value, Status.SUBMITTED.value]:
        raise HTTPException(status_code=400, detail=f"Заявка в статусе {app.status}, нельзя обработать")

    business = db.query(Business).filter(Business.id == app.business_id).first()
    product = db.query(CreditProduct).filter(CreditProduct.id == app.credit_product_id).first()
    scoring_data = calculate_scoring(business, product, app.requested_amount)
    if not business or not product:
        raise HTTPException(status_code=500, detail="Ошибка данных: бизнес или продукт не найден")
    scoring_result = ScoringResult(
        application_id=app.id,
        total_score=scoring_data["total_score"],
        financial_stability_score=scoring_data["total_score"],
        payment_capacity_score=scoring_data["total_score"],
        business_age_score=scoring_data["total_score"],
        external_checks_score=scoring_data["total_score"],
        input_snapshot= "{}"
    )
    db.add(scoring_result)

    decision_result = CreditDecision(
        application_id=app.id,
        decision=scoring_data["decision"],
        reason=scoring_data["reason"],
        offered_amount=scoring_data["offered_amount"],
        offered_term_months=app.requested_term_months,
        offered_rate=product.annual_rate if product else Decimal("15.00")
    )
    db.add(decision_result)

    old_status = app.status
    app.status = scoring_data["decision"]

    history = ApplicationStatusHistory(
        application_id=app.id,
        old_status=old_status,
        new_status=app.status,
        comment=f"Автоматическое решение: {scoring_data['reason']}"

    )
    db.add(history)
    db.commit()
    db.refresh(app)
    return app

@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: UUID, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return app

@router.get("/bank/queue")
def get_bank_queue(db: Session = Depends(get_db)):
    results = db.query(Application, Business.name).join(
        Business, Application.business_id == Business.id
    ).order_by(Application.created_at.desc()).all()

    return [
        {
            "id": str(app.id),
            "business_name": business_name,
            "requested_amount": float(app.requested_amount),
            "requested_term_months": app.requested_term_months,
            "status": app.status,
            "can_be_processed": app.status in ["SUBMITTED", "NEED_MORE_INFO"],
            "created_at": app.created_at.isoformat() if app.created_at else None
        }
        for app, business_name in results
    ]


# вот по этой приколюхе рисовать полоску с этапами в кабинете клиента
@router.get("/{application_id}/history")
def get_application_history(application_id: UUID, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    history = db.query(ApplicationStatusHistory).filter(
        ApplicationStatusHistory.application_id == application_id
    ).order_by(ApplicationStatusHistory.changed_at.asc()).all()

    return [
        {
            "old_status": h.old_status,
            "new_status": h.new_status,
            "comment": h.comment,
            "created_at": h.changed_at.isoformat() if h.changed_at else None
        }
        for h in history
    ]