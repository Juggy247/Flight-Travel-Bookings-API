from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str | None = None

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