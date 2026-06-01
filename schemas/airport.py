from pydantic import BaseModel, Field, ConfigDict
import re
from pydantic import field_validator

class AirportBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    code: str 
    city: str = Field(min_length=2, max_length=100)
    country: str = Field(min_length=2, max_length=100)
    timezone: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, value):
        if not re.match(r"^[A-Z]{3,4}$", value):
            raise ValueError("Airport code must be 3-4 uppercase letters e.g. KUL or WMKK")
        return value
    
    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value):
        if not re.match(r"^[A-Za-z]+/[A-Za-z_]+$", value):
            raise ValueError("Timezone must be in format Region/City e.g. Asia/Kuala_Lumpur")
        return value


class AirportCreate(AirportBase):
    pass

class AirportResponse(BaseModel):
    id: int
    code: str
    name: str
    city: str
    country: str
    timezone: str
    model_config = ConfigDict(from_attributes=True)
