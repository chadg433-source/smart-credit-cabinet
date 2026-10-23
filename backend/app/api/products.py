from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CreditProduct

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
def get_products(db: Session = Depends(get_db)):
    products = db.query(CreditProduct).filter(CreditProduct.is_active == True).all()
    # тут защита от пустой бдшки
    if not products:
        raise HTTPException(
            status_code=404,
            detail="Кредиты временно недоступны. Пожалуйста, обратитесь в банк."
        )

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "min_amount": float(p.min_amount),
            "max_amount": float(p.max_amount),
            "min_term_months": p.min_term_months,
            "max_term_months": p.max_term_months,
            "annual_rate": float(p.annual_rate)
        }
        for p in products
    ]