from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import datetime

class UserCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def no_special_characters(cls, value: str) -> str:
        if "_" in value or "-" in value:
            raise ValueError("Name cannot contain underscore or dashes")
        return value.strip()

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    #model config (from attributes means receive an object from databases and read its
    #attributes instead of waiting for json type which pydantic expect in default

class Token(BaseModel):
    access_token: str
    token_type: str