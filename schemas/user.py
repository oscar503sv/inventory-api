from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class TokenBlacklist(BaseModel):
    token: str

    class Config:
        from_attributes = True
