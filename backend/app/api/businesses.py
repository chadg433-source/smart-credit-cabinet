from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Business
from app.config import settings

router = APIRouter(prefix="/businesses", tags=["Businesses"])


@router.get("/")
def get_businesses(db: Session = Depends(get_db)):
    businesses = (
        db.query(Business)
        .filter(Business.entrepreneur_id == settings.demo_user_id)
        .all()
    )

    return [
        {
            "id": str(b.id),
            "name": b.name,
            "tax_id": b.tax_id,
            "business_type": b.business_type,
            "monthly_revenue": float(b.monthly_revenue),
            "monthly_expenses": float(b.monthly_expenses),
            "existing_monthly_loan_payments": float(
                b.existing_monthly_loan_payments
            ),
        }
        for b in businesses
    ]
