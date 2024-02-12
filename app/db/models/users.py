from db.base_class import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, Session
from utils.hashing import Hasher
from schemas.user_schema import CreateUser, CreateUserResponse


class Users(Base):
    user_id = Column(Integer, primary_key = True)
    user_name = Column(String, nullable = False)
    user_email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    user_phone = Column(String, nullable = True)
    last_modified_on = Column(DateTime, default= datetime.now())

    user_session = relationship("User_sessions", back_populates="user")
    files = relationship("Files", back_populates="user")


def get_user(user_email:str, db:Session):
    user = db.query(Users).filter(Users.user_email == user_email.lower()).first()
    return user


def create_new_user(user : CreateUser, db: Session):
    user = Users(
        user_email = user.user_email.lower(),
        password = Hasher.get_password_hash(user.password),
        user_name = user.user_name,
        user_phone = user.user_phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    userResponse = CreateUserResponse(user_email=user.user_email, user_name=user.user_name)
    return userResponse







