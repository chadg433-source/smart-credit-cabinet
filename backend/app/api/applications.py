from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ApplicationCreate, ApplicationResponse
from app.models import Application

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