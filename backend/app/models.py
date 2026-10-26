import uuid
from datetime import datetime, timezone, date
from decimal import Decimal
from sqlalchemy import DateTime, String, ForeignKey, Numeric, Date, Text, Integer, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Entrepreneur(Base):
    __tablename__ = 'entrepreneurs'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default= lambda: datetime.now(timezone.utc)
    )

class Business(Base):
    __tablename__ = 'businesses'
    __table_args__ = (
        CheckConstraint("monthly_revenue >= 0", name="business_monthly_revenue_positive"),
        CheckConstraint("monthly_expenses >= 0", name="business_expenses_months_positive"),
        CheckConstraint("existing_monthly_loan_payments >= 0",
                        name="business_existing_monthly_loan_payments_positive"),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    entrepreneur_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('entrepreneurs.id'),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    tax_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False
    )
    business_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    registration_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )
    monthly_revenue: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )
    monthly_expenses: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )
    existing_monthly_loan_payments: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=lambda: datetime.now(timezone.utc),
        default= lambda: datetime.now(timezone.utc)
    )

class CreditProduct(Base):
    __tablename__ = "credit_products"
    __table_args__ = (
        CheckConstraint("min_amount > 0", name="ck_credit_products_min_amount_positive"),
        CheckConstraint("max_amount >= min_amount", name="ck_credit_products_max_amount_positive"),
        CheckConstraint("min_term_months > 0", name="ck_credit_products_min_term_months_positive"),
        CheckConstraint("max_term_months >= min_term_months", name="ck_credit_products_max_term_months_positive"),
        CheckConstraint("annual_rate >= 0", name="ck_credit_products_annual_rate_positive")
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    min_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )
    max_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )
    min_term_months: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    max_term_months: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    annual_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        CheckConstraint("requested_amount > 0", name="ck_applications_requested_amount_positive"),
        CheckConstraint("requested_term_months > 0", name="ck_applications_requested_term_months_positive")
    )
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('businesses.id'),
        nullable=False
    )
    credit_product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('credit_products.id'),
        nullable=False
    )
    product: Mapped["CreditProduct"] = relationship(
        "CreditProduct"
    )
    requested_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )
    requested_term_months: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    purpose: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="DRAFT"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default= lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=lambda: datetime.now(timezone.utc),
        default= lambda: datetime.now(timezone.utc)
    )

class ExternalCheckResult(Base):
    __tablename__ = "external_check_results"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('applications.id'),
        nullable=False
    )
    check_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    result_data: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default= lambda: datetime.now(timezone.utc)
    )

class ScoringResult(Base):
    __tablename__ = 'scoring_results'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('applications.id'),
        nullable=False
    )
    total_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )
    financial_stability_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )
    payment_capacity_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )
    business_age_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )
    external_checks_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )
    input_snapshot: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default= lambda: datetime.now(timezone.utc)
    )

class CreditDecision(Base):
    __tablename__ = "credit_decisions"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('applications.id'),
        nullable=False
    )
    decision: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    offered_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        nullable=True
    )
    offered_term_months: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    offered_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default= lambda: datetime.now(timezone.utc)
    )

class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('applications.id'),
        nullable=False
    )
    old_status: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True
    )
    new_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default= lambda: datetime.now(timezone.utc)
    )
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )


class ApplicationDocument(Base):
    __tablename__ = "application_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id"),
        nullable=False
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
