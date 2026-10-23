from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ApplicationCreate, ApplicationResponse
from app.models import Application, ApplicationStatusHistory
from app.services.external_checks import run_external_checks
from app.services.state_machine import assert_transition, Status

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
