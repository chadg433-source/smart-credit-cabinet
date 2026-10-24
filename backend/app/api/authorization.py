from datetime import datetime, timedelta, timezone
import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_entrepreneur
from app.database import get_db
from app.models import Entrepreneur
from app.schemas import TokenResponse, EntrepreneurResponse
from app.config import settings

router = APIRouter(prefix="/auth",tags=["auth"])

@router.post("/demo-login", response_model=TokenResponse)
def authorization(db: Session = Depends(get_db)):
    entrepreneur = db.query(Entrepreneur).where(Entrepreneur.id == settings.demo_user_id).first()
    if entrepreneur is None:
        raise HTTPException(status_code=404, detail="Не найден данный пользователь")

    access_token = jwt.encode(payload={"sub": str(entrepreneur.id),
                                       "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
                              key=settings.jwt_secret_key,
                              algorithm="HS256")

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=EntrepreneurResponse)
def get_me(me: Entrepreneur = Depends(get_current_entrepreneur)):
    return me