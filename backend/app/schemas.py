from datetime import datetime
from decimal import Decimal
from pydantic import Field, BaseModel, ConfigDict
from  uuid import UUID

class ApplicationCreate(BaseModel):
    business_id: UUID = Field(..., description="ID бизнеса")
    credit_product_id: UUID = Field(..., description="ID кредитного продукта")
    requested_amount: Decimal = Field(..., gt=0, description="Сумма кредита")
    requested_term_months: int = Field(..., gt=0, description="Срок в месяцах")
    purpose: str | None = Field(None, description="Цель кредита")
    model_config = ConfigDict(from_attributes=True)

class ApplicationUpdate(BaseModel):
    requested_amount: Decimal = Field(..., gt=0)
    requested_term_months: int = Field(..., gt=0)
    purpose: str = Field(..., min_length=1, max_length=255)

class ApplicationResponse(ApplicationCreate):
    id: UUID
    status: str
    requested_amount:Decimal
    purpose: str
    product_name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str = Field(..., title="Access_token")
    token_type: str =  Field(default="bearer", title="Token")

class EntrepreneurResponse(BaseModel):
    id: UUID = Field(..., title="ID")
    full_name: str = Field(..., title="Full Name")
    created_at: datetime = Field(..., title="Created at")
    model_config = ConfigDict(from_attributes=True)