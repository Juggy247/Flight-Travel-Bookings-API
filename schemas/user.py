from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import datetime
import re

class UserBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr

    @field_validator("first_name", "last_name")
    @classmethod
    def no_special_characters(cls, value: str) -> str:
        if "_" in value or "-" in value:
            raise ValueError("Name cannot contain underscore or dashes")
        return value.strip()

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    phone: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            return value
        if not re.match(r"^\+?[0-9][0-9\s\-]{6,19}$", value):
            raise ValueError("Invalid phone number format.")
        return value

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    #model config (from attributes means receive an object from databases and read its
    #attributes instead of waiting for json type which pydantic expect in default

class Token(BaseModel):
    access_token: str
    token_type: str