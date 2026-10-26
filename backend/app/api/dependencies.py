from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Entrepreneur

security = HTTPBearer()

def get_current_entrepreneur(credentials: HTTPAuthorizationCredentials = Depends(security),
                             db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    try:
        sub = UUID(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Некорректный идентификатор предпринимателя в токене")

    entrepreneur = db.query(Entrepreneur).where(Entrepreneur.id == sub).first()
    if entrepreneur is None:
        raise HTTPException(401, detail="Предприниматель не найден")
    return entrepreneur