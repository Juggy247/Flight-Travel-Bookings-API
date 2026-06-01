from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Literal

class PaymentBase(BaseModel):
    booking_id: int = Field(gt=0)
    amount: float = Field(gt=0, le=50000)
    currency: str = Field(default="USD", min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value):
        # ISO 4217 currency codes are 3 uppercase letters
        allowed = ["USD", "EUR", "GBP", "PLN", "MYR", "SGD", "JPY", "THB"]
        if value.upper() not in allowed:
            raise ValueError(f"Currency must be one of: {', '.join(allowed)}")
        return value.upper()

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    status: Literal["pending", "completed", "refunded"]
    paid_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

class PaymentUpdate(BaseModel):
    status: Literal["pending", "completed", "refunded"]