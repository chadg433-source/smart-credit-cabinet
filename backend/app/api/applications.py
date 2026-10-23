from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.application_service import transition_application
from app.database import get_db
from app.models import (
    Application,
    ApplicationStatusHistory,
    Business,
    CreditDecision,
    CreditProduct,
    ScoringResult,
)
from app.schemas import ApplicationCreate, ApplicationResponse
from app.services.external_checks import run_external_checks
from app.services.scoring import calculate_scoring
from app.services.state_machine import Status


router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/", response_model=ApplicationResponse)
def create_application(
    app_in: ApplicationCreate,
    db: Session = Depends(get_db),
):
    new_app = Application(
        business_id=app_in.business_id,
        credit_product_id=app_in.credit_product_id,
        requested_amount=app_in.requested_amount,
        requested_term_months=app_in.requested_term_months,
        purpose=app_in.purpose,
        status=Status.DRAFT.value,
    )

    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return new_app


@router.get("/", response_model=list[ApplicationResponse])
def get_applications(db: Session = Depends(get_db)):
    return db.query(Application).all()


# Статические маршруты располагаем перед маршрутами с application_id.


@router.get("/bank/queue")
def get_bank_queue(db: Session = Depends(get_db)):
    results = (
        db.query(Application, Business.name)
        .join(Business, Application.business_id == Business.id)
        .order_by(Application.created_at.desc())
        .all()
    )

    return [
        {
            "id": str(app.id),
            "business_name": business_name,
            "requested_amount": float(app.requested_amount),
            "requested_term_months": app.requested_term_months,
            "status": app.status,
            "can_be_processed": app.status
            in [
                Status.SUBMITTED.value,
                Status.NEED_MORE_INFO.value,
            ],
            "created_at": (
                app.created_at.isoformat() if app.created_at else None
            ),
        }
        for app, business_name in results
    ]


@router.post("/{application_id}/submit", response_model=ApplicationResponse)
def submit_application(
    application_id: UUID,
    db: Session = Depends(get_db),
):
    app = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not app:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    try:
        transition_application(
            app,
            Status.SUBMITTED.value,
            "Заявка отправлена на проверку",
            db,
        )

        db.commit()
        db.refresh(app)

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    return app


@router.post("/{application_id}/process", response_model=ApplicationResponse)
def process_application(
    application_id: UUID,
    db: Session = Depends(get_db),
):
    app = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not app:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    if app.status not in [
        Status.SUBMITTED.value,
        Status.NEED_MORE_INFO.value,
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Заявка в статусе {app.status}, нельзя обработать",
        )

    try:
        transition_application(
            app,
            Status.VALIDATION.value,
            "Проверка данных заявки",
            db,
        )

        business = (
            db.query(Business)
            .filter(Business.id == app.business_id)
            .first()
        )

        if not business:
            raise HTTPException(
                status_code=404,
                detail="Компания, связанная с заявкой, не найдена",
            )

        product = (
            db.query(CreditProduct)
            .filter(CreditProduct.id == app.credit_product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Кредитный продукт не найден",
            )

        transition_application(
            app,
            Status.EXTERNAL_CHECKS.value,
            "Запущены внешние проверки",
            db,
        )

        checks_result = run_external_checks(str(app.business_id))

        if not checks_result["is_all_passed"]:
            transition_application(
                app,
                Status.NEED_MORE_INFO.value,
                "Внешние проверки не пройдены",
                db,
            )

            db.commit()
            db.refresh(app)
            return app

        transition_application(
            app,
            Status.SCORING.value,
            "Вычисление скоринга",
            db,
        )

        scoring_data = calculate_scoring(
            business,
            product,
            app.requested_amount,
        )

        transition_application(
            app,
            Status.DECISION_PENDING.value,
            "Скоринг завершён, подготовлено решение",
            db,
        )

        scoring_result = ScoringResult(
            application_id=app.id,
            total_score=scoring_data["total_score"],
            financial_stability_score=scoring_data["total_score"],
            payment_capacity_score=scoring_data["total_score"],
            business_age_score=scoring_data["total_score"],
            external_checks_score=scoring_data["total_score"],
            input_snapshot="{}",
        )
        db.add(scoring_result)

        decision = scoring_data["decision"]

        allowed_decisions = {
            Status.APPROVED.value,
            Status.APPROVED_WITH_CONDITIONS.value,
            Status.REJECTED.value,
            Status.NEED_MORE_INFO.value,
        }

        if decision not in allowed_decisions:
            raise ValueError(
                f"Скоринг вернул неизвестное решение: {decision}"
            )

        decision_result = CreditDecision(
            application_id=app.id,
            decision=decision,
            reason=scoring_data["reason"],
            offered_amount=scoring_data["offered_amount"],
            offered_term_months=app.requested_term_months,
            offered_rate=product.annual_rate,
        )
        db.add(decision_result)

        transition_application(
            app,
            decision,
            scoring_data["reason"],
            db,
        )

        db.commit()
        db.refresh(app)

    except HTTPException:
        db.rollback()
        raise

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    return app


@router.get("/{application_id}/history")
def get_application_history(
    application_id: UUID,
    db: Session = Depends(get_db),
):
    app = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not app:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    history = (
        db.query(ApplicationStatusHistory)
        .filter(ApplicationStatusHistory.application_id == application_id)
        .order_by(ApplicationStatusHistory.changed_at.asc())
        .all()
    )

    return [
        {
            "old_status": item.old_status,
            "new_status": item.new_status,
            "comment": item.comment,
            "created_at": (
                item.changed_at.isoformat()
                if item.changed_at
                else None
            ),
        }
        for item in history
    ]


@router.post("/{application_id}/documents", response_model=ApplicationResponse)
def sign_documents(
    application_id: UUID,
    db: Session = Depends(get_db),
):
    app = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not app:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    if app.status not in [
        Status.APPROVED.value,
        Status.APPROVED_WITH_CONDITIONS.value,
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Нельзя подписать документы в статусе {app.status}",
        )

    try:
        transition_application(
            app,
            Status.DOCUMENTS.value,
            "Клиент подписал кредитные документы",
            db,
        )

        db.commit()
        db.refresh(app)

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    return app


@router.post("/{application_id}/disburse", response_model=ApplicationResponse)
def disburse_application(
    application_id: UUID,
    db: Session = Depends(get_db),
):
    app = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not app:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    if app.status != Status.DOCUMENTS.value:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Нельзя выдать кредит в статусе {app.status}. "
                "Сначала подпишите документы."
            ),
        )

    try:
        transition_application(
            app,
            Status.DISBURSED.value,
            "Денежные средства переведены на счёт компании",
            db,
        )

        db.commit()
        db.refresh(app)

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    return app


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
):
    app = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not app:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    return app
