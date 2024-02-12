from pydantic import BaseModel, EmailStr, Field

class UserSessionInfo(BaseModel):
    access_token :str
    user_id:int
    user_email:str