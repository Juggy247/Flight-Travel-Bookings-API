from pydantic import BaseModel, Field, StrictStr, model_validator, ConfigDict, field_validator
from datetime import datetime, timezone
import re

def validate_datetime(value):
    if value is None:
        return value
    if value < datetime.now(timezone.utc).replace(tzinfo=None):
        raise ValueError("Boarding time must be in the future")
    return value

class AirportBase(BaseModel):
    id: int
    code: str
    name: str
    city: str
    country: str
    model_config = ConfigDict(from_attributes=True)

class FlightBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    origin_id: int = Field(gt=0)
    destination_id: int = Field(gt=0)
    flight_number: str
    boarding_time: datetime
    arrival_time: datetime
    price: float = Field(gt=0, le=50000)
    seats: int = Field(gt=0, le=853)

class FlightCreate(FlightBase):

    @model_validator(mode='before')
    @classmethod
    def no_numeric_strings(cls, values):
        if not isinstance(values, dict):
            try:
                values = {k: v for k, v in values.__dict__.items()
                        if not k.startswith('_')}
            except AttributeError:
                return values
        for field in ['name', 'flight_number']:
            val = values.get(field)
            if isinstance(val, str):
                if val.strip() == "":
                    raise ValueError(f"{field} cannot be empty or whitespace")
                if val.strip().isdigit():
                    raise ValueError(f"{field} cannot be purely numeric")
        return values

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):                
        if not re.match(r"^[a-zA-Z0-9\s\-\.]+$", value):
            raise ValueError("Name can only contain letters, numbers, spaces, hyphens and dots")
        return value

    @field_validator("boarding_time", "arrival_time")
    @classmethod
    def check_boarding_time(cls, value):
        return validate_datetime(value)

    @field_validator("flight_number")
    @classmethod
    def validate_flight_number(cls, value):
        if not re.match(r"^[A-Z]{2}\d{1,4}$", value):
            raise ValueError("Flight number must be 2 uppercase letters followed by 1-4 digits e.g. AK101")
        return value
    
    @model_validator(mode='after')
    def validate_flight_logic(self):
        # arrival must be after boarding
        if self.arrival_time and self.boarding_time:
            if self.arrival_time <= self.boarding_time:
                raise ValueError("Arrival time must be after boarding time")
        # origin and destination must be different
        if self.origin_id == self.destination_id:
            raise ValueError("Origin and destination airports cannot be the same")
        return self


class FlightResponse(FlightBase):
    id: int
    origin_airport: AirportBase | None = None
    destination_airport: AirportBase | None = None
    model_config = ConfigDict(from_attributes=True)


class FlightUpdate(BaseModel):
    name: StrictStr | None = None
    origin_id: int | None = Field(default=None, gt=0)        
    destination_id: int | None = Field(default=None, gt=0)   
    boarding_time: datetime | None = None
    arrival_time: datetime | None = None                     
    price: float | None = Field(default=None, gt=0)
    seats: int | None = Field(default=None, gt=0)

    @field_validator("boarding_time", "arrival_time")
    @classmethod
    def check_boarding_time(cls, value):
        return validate_datetime(value)