from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Literal
import re
from schemas.flight import FlightResponse 

class BookingBase(BaseModel):
    flight_id: int = Field(gt=0)
    seat_number: str | None = None

    @field_validator("seat_number")
    @classmethod
    def validate_seat_number(cls, value):
        if value is None:
            return value
        if not re.match(r"^([1-9]|[1-4][0-9]|50)[A-F]$", value.upper()):
            raise ValueError(
                "Invalid seat number. Must be row 1-50 + letter A-F e.g. 1A, 12B, 48C"
            )
        return value.upper()

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    user_id: int
    status: Literal["confirmed", "cancelled"]
    booked_at: datetime
    flight: FlightResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class BookingUpdate(BaseModel):
    status: Literal["confirmed", "cancelled"]
    