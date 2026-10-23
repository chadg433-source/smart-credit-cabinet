from enum import Enum

class Status(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VALIDATION = "VALIDATION"
    EXTERNAL_CHECKS = "EXTERNAL_CHECKS"
    SCORING = "SCORING"
    DECISION_PENDING = "DECISION_PENDING"
    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    REJECTED = "REJECTED"
    NEED_MORE_INFO = "NEED_MORE_INFO"
    DOCUMENTS = "DOCUMENTS"
    DISBURSED = "DISBURSED"

TRANSITIONS: dict[Status, set[Status]] = {
    Status.DRAFT: {Status.SUBMITTED},
    Status.SUBMITTED: {Status.VALIDATION},
    Status.VALIDATION: {Status.EXTERNAL_CHECKS, Status.NEED_MORE_INFO},
    Status.EXTERNAL_CHECKS: {Status.SCORING, Status.NEED_MORE_INFO},
    Status.SCORING: {Status.DECISION_PENDING},
    Status.DECISION_PENDING: {
        Status.APPROVED,
        Status.APPROVED_WITH_CONDITIONS,
        Status.REJECTED,
        Status.NEED_MORE_INFO,
    },
    Status.NEED_MORE_INFO: {Status.VALIDATION},
    Status.APPROVED: {Status.DOCUMENTS},
    Status.APPROVED_WITH_CONDITIONS: {Status.DOCUMENTS, Status.REJECTED},
    Status.DOCUMENTS: {Status.DISBURSED},
}

def can_transition(current: str, target: str) -> bool:
    try:
        current_enum = Status(current)
        target_enum = Status(target)
    except ValueError:
        return False
    return target_enum in TRANSITIONS.get(current_enum, set())

def assert_transition(current: str, target: str) -> None:
    if not can_transition(current, target):
        raise ValueError(f"Недопустимый переход статуса: {current} -> {target}")