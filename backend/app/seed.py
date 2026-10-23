from datetime import date
import uuid
from sqlalchemy.orm import Session
from typing import TypeVar
from decimal import Decimal
from app.database import SessionLocal, Base
from app.models import Entrepreneur, Business, Application, ExternalCheckResult, ScoringResult, CreditDecision, \
    ApplicationStatusHistory, CreditProduct

T = TypeVar('T', bound=Base)

def seed():
    with SessionLocal() as session:
        # Проверяем, есть ли уже данные
        if session.query(Business).first():
            print("Данные уже существуют, пропускаем сид.")
            return
        entrepreneur = create_object(
            Entrepreneur,
            session,
            full_name="Губарьков Иван")
        session.flush()

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
        session.flush()
        product = create_object(
            CreditProduct,
            session,
            name="Бизнес-старт",
            description="Кредит для развития бизнеса",
            min_amount=Decimal("100000.00"),
            max_amount=Decimal("5000000.00"),
            min_term_months=6,
            max_term_months=60,
            annual_rate=Decimal("15.00"),
            is_active=True
        )
        session.flush()

        print("="*10)
        print("Entrepreneur ID:", entrepreneur.id)
        print("Business ID:", business.id)
        print("Product ID:", product.id)
        print("=" * 10)

        print("="*10)
        print("Business ID for application:", business.id)
        print("Product ID for application:", product.id)
        print("=" * 10)

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
        create_object(
            ExternalCheckResult,
            session,
            application_id=application.id,
            check_type="TAX_CHECK",
            status="PASSED",
            result_data="Нарушений не обнаружено"
        )
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