from pydantic import BaseModel, constr, EmailStr, Field
from datetime import date



class UsersBase(BaseModel):
    email: EmailStr
    name: str
    group: str
    gender: str
    userType: str
    class Config:
        orm_mode = True


class UsersCreate(UsersBase):
    password: str = Field(alias="password")


class Users(UsersBase):
    id: int
    user_uuid: str
    creation_date: date
