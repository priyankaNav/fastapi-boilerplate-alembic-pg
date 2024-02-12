from sqlalchemy.orm import Session
from db.models.users import Users
from utils.hashing import Hasher
from db.models.users import get_user
from jose import jwt
from fastapi import HTTPException, status
from jose import jwt
import os

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM") 
JWT_SECRET_KEY = os.getenv("JWT_SECRET_TOKEN")

"""
Validates given user_email and password
"""
def authenticate_user(email:str, password:str, db:Session):
    user = get_user(user_email = email.lower(), db = db)
    if not user:
        return False
    if not Hasher.verify_password(password, user.password):
        return False
    return user

"""
Validates user_access_token to authorize the user
"""
def validate_user_token(token: str, db:Session):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        user_email: str = payload.get("user_email")
        if user_id is None or user_email is None:
            raise HTTPException(status=status.HTTP_401_UNAUTHORIZED,  detail="Could not validate credentials")
    except:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    userInfo:Users = get_user(user_email=user_email, db=db)
       
    return userInfo


