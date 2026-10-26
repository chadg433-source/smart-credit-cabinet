from sqlalchemy.orm import Session
from app.api.application_service import transition_application
from app.api.record_change import commit_changes
from app.models import (
    Application,
    Business,
    CreditProduct,
    ScoringResult,
    CreditDecision,
)
from app.services.external_checks import run_external_checks
from app.services.scoring import calculate_scoring
from app.services.state_machine import Status


def process_application_service(
    app: Application,
    db: Session,
) -> Application:
    final_statuses = {
        Status.APPROVED.value,
        Status.APPROVED_WITH_CONDITIONS.value,
        Status.REJECTED.value,
        Status.DOCUMENTS.value,
        Status.DISBURSED.value,
    }

    if app.status in final_statuses:
        return app

    resumable_statuses = {
        Status.SUBMITTED.value,
        Status.NEED_MORE_INFO.value,
        Status.VALIDATION.value,
        Status.EXTERNAL_CHECKS.value,
        Status.SCORING.value,
    }

    if app.status not in resumable_statuses:
        raise ValueError(
            f"Заявку в статусе {app.status} нельзя обработать"
        )

    if app.status in {
        Status.SUBMITTED.value,
        Status.NEED_MORE_INFO.value,
    }:
        transition_application(
            app,
            Status.VALIDATION.value,
            "Проверка данных заявки",
            db,
        )
        commit_changes(db, app)

    business = (
        db.query(Business)
        .filter(Business.id == app.business_id)
        .first()
    )

    if business is None:
        raise ValueError(
            "Компания, связанная с заявкой, не найдена"
        )

    product = (
        db.query(CreditProduct)
        .filter(CreditProduct.id == app.credit_product_id)
        .first()
    )

    if product is None:
        raise ValueError("Кредитный продукт не найден")

    if app.status == Status.VALIDATION.value:
        transition_application(
            app,
            Status.EXTERNAL_CHECKS.value,
            "Запущены внешние проверки",
            db,
        )
        commit_changes(db, app)

    if app.status == Status.EXTERNAL_CHECKS.value:
        checks_result = run_external_checks(
            str(app.business_id)
        )

        if not checks_result["is_all_passed"]:
            transition_application(
                app,
                Status.NEED_MORE_INFO.value,
                "Внешние проверки не пройдены",
                db,
            )
            commit_changes(db, app)
            return app

        transition_application(
            app,
            Status.SCORING.value,
            "Вычисление скоринга",
            db,
        )
        commit_changes(db, app)

    if app.status == Status.SCORING.value:
        scoring_data = calculate_scoring(
            business,
            product,
            app.requested_amount,
        )

        decision = scoring_data["decision"]

        allowed_decisions = {
            Status.APPROVED.value,
            Status.APPROVED_WITH_CONDITIONS.value,
            Status.REJECTED.value,
            Status.NEED_MORE_INFO.value,
        }

        if decision not in allowed_decisions:
            raise ValueError(
                f"Скоринг вернул неизвестное решение: {decision}"
            )

        scoring_result = ScoringResult(
            application_id=app.id,
            total_score=scoring_data["total_score"],
            financial_stability_score=scoring_data["total_score"],
            payment_capacity_score=scoring_data["total_score"],
            business_age_score=scoring_data["total_score"],
            external_checks_score=scoring_data["total_score"],
            input_snapshot="{}",
        )
        db.add(scoring_result)

        decision_result = CreditDecision(
            application_id=app.id,
            decision=decision,
            reason=scoring_data["reason"],
            offered_amount=scoring_data["offered_amount"],
            offered_term_months=app.requested_term_months,
            offered_rate=product.annual_rate,
        )
        db.add(decision_result)

        transition_application(
            app,
            Status.DECISION_PENDING.value,
            "Скоринг завершён, подготовлено решение",
            db,
        )

        transition_application(
            app,
            decision,
            scoring_data["reason"],
            db,
        )

        commit_changes(db, app)

    return app
