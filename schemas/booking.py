from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Literal

class BookingCreate(BaseModel):
    flight_id: int

class BookingResponse(BaseModel):
    id: int
    user_id: int
    flight_id: int
    status: str
    booked_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BookingUpdate(BaseModel):
    status: Literal["confirmed", "cancelled"]
    