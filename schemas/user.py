from pydantic import BaseModel

class User(BaseModel):
    username: str
    role: str

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str
