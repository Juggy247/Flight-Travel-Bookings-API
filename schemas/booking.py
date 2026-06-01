from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal

class BookingBase(BaseModel):
    flight_id: int = Field(gt=0)
    seat_number: str | None = None

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    user_id: int
    status: Literal["confirmed", "cancelled"]
    booked_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BookingUpdate(BaseModel):
    status: Literal["confirmed", "cancelled"]
    