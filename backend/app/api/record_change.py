from sqlalchemy.orm import Session
from typing import TypeVar
from app.database import Base

T = TypeVar('T', bound=Base)
def commit_changes(db: Session, obj: T) -> None:
    db.commit()
    db.refresh(obj)