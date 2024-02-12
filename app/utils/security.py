from datetime import datetime,timedelta
from typing import Optional
from jose import jwt
import os

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM") 
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_TOKEN")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt