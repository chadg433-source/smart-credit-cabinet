from sqlalchemy.orm import Session
from app.models import Application, ApplicationStatusHistory
from app.services.state_machine import assert_transition


def transition_application(app: Application, new_status: str, comment: str, db: Session) -> None:
    old_status: str = str(app.status)
    assert_transition(old_status, new_status)
    app.status = new_status
    history = ApplicationStatusHistory(
        application_id=app.id,
        old_status=old_status,
        new_status=new_status,
        comment=comment
    )

    db.add(history)