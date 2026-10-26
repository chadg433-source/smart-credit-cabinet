from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.api.record_change import commit_changes
from app.api.application_service import transition_application
from app.database import get_db
from app.models import (
    Application,
    ApplicationStatusHistory,
    Business, CreditProduct
)
from app.schemas import ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.services.application_processing import process_application_service
from app.services.state_machine import Status


router = APIRouter(prefix="/applications", tags=["Applications"])


def to_application_response(app: Application) -> ApplicationResponse:
    return ApplicationResponse(
        id=app.id,
        business_id=app.business_id,
        credit_product_id=app.credit_product_id,
        requested_amount=app.requested_amount,
        requested_term_months=app.requested_term_months,
        purpose=app.purpose,
        status=app.status,
        product_name=app.product.name,
        created_at=app.created_at,
    )


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
    commit_changes(db, new_app)
    return to_application_response(new_app)

@router.get("/", response_model=list[ApplicationResponse])
def get_applications(db: Session = Depends(get_db)):
    applications = (
        db.query(Application)
        .options(joinedload(Application.product))
        .all()
    )

    return [
        {
            "id": app.id,
            "business_id": app.business_id,
            "credit_product_id": app.credit_product_id,
            "requested_amount": app.requested_amount,
            "requested_term_months": app.requested_term_months,
            "purpose": app.purpose,
            "status": app.status,
            "created_at": app.created_at,
            "product_name": app.product.name,
        }
        for app in applications
    ]

@router.get("/bank/queue")
def get_bank_queue(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    results = (
        db.query(Application, Business.name)
        .join(Business, Application.business_id == Business.id)
        .order_by(Application.created_at.desc())
        .offset(skip)
        .limit(limit)
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
@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: UUID,
    app_in: ApplicationUpdate,
    db: Session = Depends(get_db),
):
    app = (
        db.query(Application)
        .options(joinedload(Application.product))
        .filter(Application.id == application_id)
        .first()
    )

    if app is None:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    if app.status != Status.NEED_MORE_INFO.value:
        raise HTTPException(
            status_code=400,
            detail="Редактировать можно только заявку, требующую дополнительной информации",
        )

    product = (
        db.query(CreditProduct)
        .filter(CreditProduct.id == app.credit_product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=400,
            detail="Кредитный продукт не найден",
        )

    if not (
        product.min_amount
        <= app_in.requested_amount
        <= product.max_amount
    ):
        raise HTTPException(
            status_code=400,
            detail="Сумма кредита выходит за допустимые пределы продукта",
        )

    if not (
        product.min_term_months
        <= app_in.requested_term_months
        <= product.max_term_months
    ):
        raise HTTPException(
            status_code=400,
            detail="Срок кредита выходит за допустимые пределы продукта",
        )

    app.requested_amount = app_in.requested_amount
    app.requested_term_months = app_in.requested_term_months
    app.purpose = app_in.purpose.strip()

    if not app.purpose:
        raise HTTPException(
            status_code=400,
            detail="Укажите цель кредита",
        )

    try:
        commit_changes(db, app)
    except Exception:
        db.rollback()
        raise

    return to_application_response(app)

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
        if app.status == Status.NEED_MORE_INFO.value:
            transition_application(
                app,
                Status.VALIDATION.value,
                "Повторная проверка после догрузки данных",
                db,
            )

        elif app.status == Status.DRAFT.value:
            transition_application(
                app,
                Status.SUBMITTED.value,
                "Заявка отправлена на проверку",
                db

            )
        else:
            raise HTTPException(400,  detail=f"Нельзя отправить заявку в статусе {app.status}")

        commit_changes(db, app)

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    try:
        app = process_application_service(app, db)
        return to_application_response(app)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception:
        db.rollback()
        raise



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

    if app is None:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена",
        )

    try:
        return to_application_response(
            process_application_service(app, db)
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception:
        db.rollback()
        raise

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

        commit_changes(db, app)

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    return to_application_response(app)


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

        commit_changes(db, app)

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    return to_application_response(app)


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

    return to_application_response(app)
