from pydantic import BaseModel, Field, EmailStr
import datetime


class UserModel(BaseModel):
    username: EmailStr = Field()
    password: str = Field(min_length=5, max_length=15)


class ActiveSessionModel(BaseModel):
    user_id: int
    username: str
    access_token: str
    expiry_time: datetime.datetime


class UserInRequestModel(BaseModel):
    user_id: int
    username: str
    token: str


class UserGenericModel():
    username: str
    password: str
