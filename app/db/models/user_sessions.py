from db.base_class import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean
from sqlalchemy.orm import relationship, Session


class User_sessions(Base):
    user_session_id = Column(Integer, primary_key = True)
    user_access_token = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default= datetime.now())

    user_id = Column(Integer, ForeignKey("users.user_id"))
    user = relationship("Users", back_populates="user_session")


def validate_user_session_token(user_id:int, access_token:str, db:Session):
    user_session = db.query(User_sessions).filter(
        User_sessions.user_id == user_id, 
        User_sessions.user_access_token == access_token, 
        User_sessions.is_deleted==False).first()
    return user_session


def delete_session_logout(user_id:int, db:Session):
    session = db.query(User_sessions).filter(User_sessions.user_id ==user_id)
    if not session:
        return{"error": f"Invalid Access Token"}
    session.delete()
    db.commit()
    return {"msg":f"User logged out successfully!"}
    

def create_user_session(user_id:int, access_token:str, db:Session):
    delete_session_logout(user_id,db)
    user_session = User_sessions(user_id = user_id,
                                user_access_token = access_token)  
    db.add(user_session)
    db.commit()
    db.refresh(user_session)
    return user_session


