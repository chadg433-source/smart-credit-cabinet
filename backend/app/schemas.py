from decimal import Decimal

from pydantic import Field, BaseModel, ConfigDict
from sqlalchemy import true
from  uuid import UUID

class ApplicationCreate(BaseModel):
    business_id: UUID = Field(..., description="ID бизнеса")
    credit_product_id: UUID = Field(..., description="ID кредитного продукта")
    requested_amount: Decimal = Field(..., gt=0, description="Сумма кредита")
    requested_term_months: int = Field(..., gt=0, description="Срок в месяцах")
    purpose: str | None = Field(None, description="Цель кредита")
    model_config = ConfigDict(from_attributes=True)

class ApplicationResponse(ApplicationCreate):
    id: UUID
    status: str
    requested_amount:Decimal
    purpose: str
    model_config = ConfigDict(from_attributes=True)




