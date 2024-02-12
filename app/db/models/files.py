from db.base_class import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship, Session, defer
import uuid
from fastapi import status, HTTPException



class Files(Base):
    file_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    filename = Column(String, nullable = False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String, nullable=True)
    last_modifed_at =Column(DateTime, default= datetime.now())
    created_at = Column(DateTime, default= datetime.now())

    user_id = Column(Integer, ForeignKey("users.user_id"))
    user = relationship("Users", back_populates="files")




"""
 Creates and Persists file and its metadata in database
"""
def create_file(filename:str, file_size:int, file_type:str, user_id:int, db: Session):
    file = Files(
        filename = filename,
        file_size = file_size,
        file_type = file_type,
        user_id =user_id
        
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    return file.file_uuid


"""
Validates if current user has previlage to access specific file 
"""
def validate_file(file_id :str, user_id:int, db:Session):
    fileInfo = db.query(Files).filter(Files.file_uuid==file_id, Files.user_id == user_id).first() 
    return fileInfo




"""
Updates file and metadata for a given file_id in database
"""
def update_file_info(file_id:str, filename:str, file_size:int, file_type:str,user_id:int, db:Session):
    file_info = db.query(Files).filter(Files.file_uuid==file_id, Files.user_id == user_id).first() 
    if file_info:
        file_info.file_size = file_size
        file_info.filename = filename
        file_info.file_type = file_type
        file_info.last_modifed_at = datetime.now()
        db.commit()
        db.refresh(file_info)
    else:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid file identifier!",
            )
    return file_info


"""
Deletes file record for given file_id from database 
"""
def delete_user_file(file_id:str, user_id:int, db:Session):
    session = db.query(Files).filter(Files.file_uuid ==file_id, Files.user_id==user_id)
    if not session:
        return{"error": f"Invalid File Identifier!"}
    session.delete()
    db.commit()
    return {"msg":f"File deleted Successfully!"}


"""Fetches all files created by user with user_id"""
def list_user_files(user_id:int, db:Session):
    files = db.query(Files).filter(Files.user_id == user_id).options(defer(Files.user_id)).all()
    return files