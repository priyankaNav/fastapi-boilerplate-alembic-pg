from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, status, status, HTTPException
from schemas.user_schema import CreateUser, CreateUserResponse, Token
from db.models.users import Users, create_new_user, get_user
from db.models.user_sessions import delete_session_logout, create_user_session
from services.user_service import validate_user_token, authenticate_user
from db.session import get_db
from fastapi.security import  OAuth2PasswordRequestForm, OAuth2PasswordBearer
from utils.security import create_access_token
from jose import JWTError, jwt  
from typing import Annotated
import os

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM") 
JWT_SECRET_KEY = os.getenv("JWT_SECRET_TOKEN")

router = APIRouter( prefix ="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

"""Create User """
@router.post("/createUser",response_model = CreateUserResponse, status_code=status.HTTP_201_CREATED)   
def create_user(user : CreateUser, db : Session=Depends(get_db)):
    try:
        # Validates if email already registered
        existingUser = get_user(user_email=user.user_email, db=db)
        if existingUser:
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail= "User already registered with this email, try logging in!"
            )
        # Creates a new user in db
        userResponse = create_new_user(user=user, db=db)
        return userResponse
    except(HTTPException, Exception) as e:
        raise HTTPException(status_code=e.status_code, detail=f"{str(e.detail)}")
    

"""User Login """
@router.post("/login", response_model=Token)
def user_login_for_access_token( form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                      db: Session=Depends(get_db)):
    try:
        # Validating user_email and password
        user=authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect username or password",
                                headers={"WWW-Authenticate": "Bearer"},)
        
        # Generate jwt access token
        access_token = create_access_token(data={"user_id": user.user_id, "user_email": user.user_email})
        # Persist user login session
        session = create_user_session(user_id=user.user_id, access_token=access_token, db=db)
        if not session:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST,
                                detail="Oops something went wrong!") 
        return Token(access_token=access_token, token_type="bearer")
    except(HTTPException, Exception) as e:
        raise HTTPException(status_code=e.status_code, detail=f"{str(e.detail)}")
   
 

""" User Logout """
@router.delete("/logout")
def logout(access_token: Annotated[str, Depends(oauth2_scheme)], db:Session=Depends(get_db)):
    try:  
        # Validates user access_token
        user:Users = validate_user_token(access_token, db)
        if user is None:
                raise HTTPException(
                detail=message.get("error"), status_code=status.HTTP_400_BAD_REQUEST
            )    
        # Delete login session to logout the user
        message = delete_session_logout(user_id=user.user_id, db=db)
        if message.get("error"):
            raise HTTPException(
                detail=message.get("error"), status_code=status.HTTP_400_BAD_REQUEST
            )
        return {"message":f"User Logged out Successfully!"}
    except(HTTPException, Exception) as e:
        raise HTTPException(status_code=e.status_code, detail=f"{str(e.detail)}")


"""
Middleware to validate the user jwt access_token and authorize user
"""
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        user_email: str = payload.get("user_email")
        if user_id is None or user_email is None:
            raise credentials_exception
        userInfo = get_user(user_email=user_email, db=db)
    except JWTError:
        raise credentials_exception
    return userInfo

def get_current_active_user(
    current_user: Annotated[Users, Depends(get_current_user)]
):
    if current_user is None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user