from datetime import date
import uuid
from sqlalchemy.orm import Session
from typing import TypeVar
from decimal import Decimal
from app.database import SessionLocal, Base
from app.models import Entrepreneur, Business, Application, ExternalCheckResult, ScoringResult, CreditDecision, \
    ApplicationStatusHistory, CreditProduct

T = TypeVar('T', bound=Base)

def seed() -> None:
    with (SessionLocal() as session):
        entrepreneur = session.query(Entrepreneur).where(Entrepreneur.full_name == "Губарьков Иван демо").first()
        if entrepreneur is None:
            entrepreneur = create_object(
                Entrepreneur,
                session,
                full_name="Губарьков Иван демо")

        business = session.query(Business).where(Business.tax_id == "7701234567",
                                                 Business.entrepreneur_id == entrepreneur.id).first()
        if business is None:
            business = create_object(
                Business,
                session,
                entrepreneur_id=entrepreneur.id,
                name="ООО Технологии",
                tax_id="7701234567",
                business_type="IT",
                registration_date=date(2022, 5, 10),
                monthly_revenue=Decimal("850000.00"),
                monthly_expenses=Decimal("500000.00"),
                existing_monthly_loan_payments=Decimal("50000.00")
            )

        product = session.query(CreditProduct).where(CreditProduct.name == "Бизнес-старт демо").first()
        if product is None:
            product = create_object(
                CreditProduct,
                session,
                name="Бизнес-старт демо",
                description="Кредит для развития бизнеса",
                min_amount=Decimal("100000.00"),
                max_amount=Decimal("5000000.00"),
                min_term_months=6,
                max_term_months=60,
                annual_rate=Decimal("15.00"),
                is_active=True
            )
        application = session.query(Application).where(Application.credit_product_id == product.id,
                                                       Application.business_id == business.id,
                                                       Application.purpose == "Покупка оборудования").first()
        if application is None:
            application = create_object(
                Application,
                session,
                business_id=business.id,
                credit_product_id=product.id,
                requested_amount=Decimal("1000000.00"),
                requested_term_months=36,
                purpose="Покупка оборудования",
                status="SUBMITTED"
            )

        external_check_result = session.query(ExternalCheckResult).where(ExternalCheckResult.application_id == application.id,
                                                                         ExternalCheckResult.check_type == "TAX_CHECK"
                                                                         ).first()
        if external_check_result is None:
            create_object(
                ExternalCheckResult,
                session,
                application_id=application.id,
                check_type="TAX_CHECK",
                status="PASSED",
                result_data="Нарушений не обнаружено"
            )
        scoring_result = session.query(ScoringResult).where(ScoringResult.application_id == application.id).first()
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
                input_snapshot='{"monthly_revenue": 850000, "monthly_expenses": 500000}'
            )

        credit_decision = session.query(CreditDecision).where(CreditDecision.application_id == application.id).first()
        if credit_decision is None:
            create_object(
                CreditDecision,
                session,
                application_id=application.id,
                decision="APPROVED",
                reason="Достаточная платёжеспособность",
                offered_amount=Decimal("1000000.00"),
                offered_term_months=36,
                offered_rate=Decimal("15.00")
            )
        application_status_history = session.query(ApplicationStatusHistory).where(
            ApplicationStatusHistory.application_id == application.id,
            ApplicationStatusHistory.old_status == "DRAFT",
            ApplicationStatusHistory.new_status == "SUBMITTED").first()
        if application_status_history is None:
            create_object(
                ApplicationStatusHistory,
                session,
                application_id=application.id,
                old_status="DRAFT",
                new_status="SUBMITTED",
                comment="Заявка передана на рассмотрение"
            )
        session.commit()

def create_object(model : type[T], current_session: Session, **kwargs) -> T:
    obj = model(id=uuid.uuid4(), **kwargs)
    current_session.add(obj)
    return obj


if __name__ == '__main__':
    seed()