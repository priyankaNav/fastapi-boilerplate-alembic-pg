from pydantic import BaseModel, EmailStr, Field

class CreateUser(BaseModel):
    user_email: EmailStr
    password: str= Field(..., min_length=6, max_length=16)
    user_name: str= Field(...,min_length=3)
    user_phone: str=Field(...,)

class CreateUserResponse(BaseModel):
    user_email: EmailStr
    user_name: str= Field(...,min_length=3)

class Token(BaseModel):
    access_token: str
    token_type: str