from datetime import date
import uuid
from sqlalchemy.orm import Session
from typing import TypeVar
from decimal import Decimal
from app.database import SessionLocal, Base
from app.models import (
    Entrepreneur,
    Business,
    Application,
    ExternalCheckResult,
    ScoringResult,
    CreditDecision,
    ApplicationStatusHistory,
    CreditProduct,
)
from app.config import settings

T = TypeVar("T", bound=Base)


def seed() -> None:
    with SessionLocal() as session:
        # 1. Предприниматель
        entrepreneur = (
            session.query(Entrepreneur)
            .where(Entrepreneur.id == settings.demo_user_id)
            .first()
        )

        if entrepreneur is None:
            entrepreneur = create_object(
                Entrepreneur,
                session,
                id=settings.demo_user_id,
                full_name="Губарьков Иван демо",
            )
            session.flush()

        # 2. Бизнесы (3 штуки)
        business = (
            session.query(Business)
            .where(
                Business.tax_id == "7701234567",
                Business.entrepreneur_id == entrepreneur.id,
            )
            .first()
        )
        if business is None:
            business = create_object(
                Business,
                session,
                id=settings.demo_business_id,
                entrepreneur_id=entrepreneur.id,
                name="ООО Технологии",
                tax_id="7701234567",
                business_type="IT",
                registration_date=date(2022, 5, 10),
                monthly_revenue=Decimal("850000.00"),
                monthly_expenses=Decimal("500000.00"),
                existing_monthly_loan_payments=Decimal("50000.00"),
            )

        perspective = (
            session.query(Business)
            .where(
                Business.tax_id == "7702345678",
                Business.entrepreneur_id == entrepreneur.id,
            )
            .first()
        )
        if perspective is None:
            create_object(
                Business,
                session,
                entrepreneur_id=entrepreneur.id,
                name="ООО Перспектива",
                tax_id="7702345678",
                business_type="Торговля",
                registration_date=date(2021, 8, 15),
                monthly_revenue=Decimal("500000.00"),
                monthly_expenses=Decimal("440000.00"),
                existing_monthly_loan_payments=Decimal("100000.00"),
            )

        risk = (
            session.query(Business)
            .where(
                Business.tax_id == "7703456789",
                Business.entrepreneur_id == entrepreneur.id,
            )
            .first()
        )
        if risk is None:
            create_object(
                Business,
                session,
                entrepreneur_id=entrepreneur.id,
                name="ООО Риск",
                tax_id="7703456789",
                business_type="Производство",
                registration_date=date(2024, 3, 20),
                monthly_revenue=Decimal("300000.00"),
                monthly_expenses=Decimal("290000.00"),
                existing_monthly_loan_payments=Decimal("180000.00"),
            )

        session.flush()

        # 3. Продукты (3 штуки)
        product1 = (
            session.query(CreditProduct)
            .where(CreditProduct.name == "Экспресс-кредит")
            .first()
        )
        if product1 is None:
            product1 = create_object(
                CreditProduct,
                session,
                name="Экспресс-кредит",
                description="Быстрые деньги на развитие бизнеса",
                min_amount=Decimal("50000.00"),
                max_amount=Decimal("1000000.00"),
                min_term_months=6,
                max_term_months=24,
                annual_rate=Decimal("18.00"),
                is_active=True,
            )

        product2 = (
            session.query(CreditProduct)
            .where(CreditProduct.name == "Кредит на оборот")
            .first()
        )
        if product2 is None:
            product2 = create_object(
                CreditProduct,
                session,
                name="Кредит на оборот",
                description="Для пополнения складских запасов",
                min_amount=Decimal("500000.00"),
                max_amount=Decimal("5000000.00"),
                min_term_months=12,
                max_term_months=36,
                annual_rate=Decimal("15.00"),
                is_active=True,
            )

        product3 = (
            session.query(CreditProduct)
            .where(CreditProduct.name == "Инвестиционный")
            .first()
        )
        if product3 is None:
            product3 = create_object(
                CreditProduct,
                session,
                name="Инвестиционный",
                description="На покупку оборудования или расширение",
                min_amount=Decimal("1000000.00"),
                max_amount=Decimal("10000000.00"),
                min_term_months=24,
                max_term_months=60,
                annual_rate=Decimal("12.00"),
                is_active=True,
            )

        session.flush()

        # 4. Демо-заявка (по первому продукту)
        application = (
            session.query(Application)
            .where(
                Application.credit_product_id == product1.id,
                Application.business_id == business.id,
                Application.purpose == "Покупка оборудования",
            )
            .first()
        )
        if application is None:
            application = create_object(
                Application,
                session,
                business_id=business.id,
                credit_product_id=product1.id,
                requested_amount=Decimal("1000000.00"),
                requested_term_months=36,
                purpose="Покупка оборудования",
                status="SUBMITTED",
            )

        # 5. Проверки и скоринг для демо-заявки
        external_check_result = (
            session.query(ExternalCheckResult)
            .where(
                ExternalCheckResult.application_id == application.id,
                ExternalCheckResult.check_type == "TAX_CHECK",
            )
            .first()
        )
        if external_check_result is None:
            create_object(
                ExternalCheckResult,
                session,
                application_id=application.id,
                check_type="TAX_CHECK",
                status="PASSED",
                result_data="Нарушений не обнаружено",
            )

        scoring_result = (
            session.query(ScoringResult)
            .where(ScoringResult.application_id == application.id)
            .first()
        )
        if scoring_result is None:
            create_object(
                ScoringResult,
                session,
                application_id=application.id,
                total_score=Decimal("85.00"),
                financial_stability_score=Decimal("90.00"),
                payment_capacity_score=Decimal("80.00"),
                business_age_score=Decimal("85.00"),
                external_checks_score=Decimal("85.00"),
                input_snapshot='{"monthly_revenue": 850000, "monthly_expenses": 500000}',
            )

        credit_decision = (
            session.query(CreditDecision)
            .where(CreditDecision.application_id == application.id)
            .first()
        )
        if credit_decision is None:
            create_object(
                CreditDecision,
                session,
                application_id=application.id,
                decision="APPROVED",
                reason="Достаточная платёжеспособность",
                offered_amount=Decimal("1000000.00"),
                offered_term_months=36,
                offered_rate=Decimal("15.00"),
            )

        application_status_history = (
            session.query(ApplicationStatusHistory)
            .where(
                ApplicationStatusHistory.application_id == application.id,
                ApplicationStatusHistory.old_status == "DRAFT",
                ApplicationStatusHistory.new_status == "SUBMITTED",
            )
            .first()
        )
        if application_status_history is None:
            create_object(
                ApplicationStatusHistory,
                session,
                application_id=application.id,
                old_status="DRAFT",
                new_status="SUBMITTED",
                comment="Заявка передана на рассмотрение",
            )

        session.commit()
        print("Сид успешно выполнен. Данные созданы (или уже существовали).")


def create_object(
    model: type[T],
    current_session: Session,
    id: uuid.UUID | None = None,
    **kwargs,
) -> T:
    if id is None:
        id = uuid.uuid4()
    obj = model(id=id, **kwargs)
    current_session.add(obj)
    return obj


if __name__ == "__main__":
    seed()