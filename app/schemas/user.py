from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str
    role_id: int = 4  # Default to donor role


class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: int
    uuid: str
    role_id: int
    is_email_verified: int
    is_phone_verified: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    password_hash: str


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(UserCreate):
    pass


class UserMe(UserInDBBase):
    role_name: Optional[str] = None