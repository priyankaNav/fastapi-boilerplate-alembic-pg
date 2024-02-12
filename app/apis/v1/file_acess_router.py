from fastapi import APIRouter, status, Response
from sqlalchemy.orm import Session
from fastapi import File, UploadFile, Depends, Query
from db.session import get_db
from fastapi import status, HTTPException
from fastapi.security import  OAuth2PasswordBearer
from db.models.users import Users
from typing import Annotated, List
from db.models.files import  Files, validate_file, delete_user_file
from services.file_service import file_upload, file_update, get_user_files
from botocore.exceptions import BotoCoreError, ClientError
from apis.v1.user_registration_router import get_current_active_user
from utils.aws_s3_utility import s3_file_download, delete_file_s3


router = APIRouter( prefix ="/files", tags=["files"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

"""Uploads File to S3"""
@router.post("/upload")
def upload_file( file: Annotated[UploadFile, File()], 
    current_user: Annotated[Users, Depends(get_current_active_user)], 
    db:Session=Depends(get_db)):

    try:
        # Uploads file to S3 and then persists in DB
        file_id = file_upload(file=file, current_user=current_user, db=db)
    except(BotoCoreError, ClientError, HTTPException, Exception) as e:
        raise HTTPException(status_code=e.status_code, detail=f"{str(e.detail)}")
    return {"file_id":file_id}


"""Retrieves file for a specific file_id"""
@router.get("/download/")
def download_file( file_id: Annotated[str, Query(min_length=36, max_length=36, description= "Please enter a valid UUID")], current_user: Annotated[Users, Depends(get_current_active_user)], 
                       db:Session=Depends(get_db)):
    try:
        fileInfo = validate_file(file_id=file_id, user_id=current_user.user_id,  db=db)
        if fileInfo is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this operation!",
            )
        # Generating the user given filename 
        original_filename = "-".join(fileInfo.filename.split('-')[:-1])
        # Gets file from S3
        response = s3_file_download(fileInfo.filename)
        
        content_disposition= f"attachment; filename={original_filename}"

        return Response(content= response['Body'].read(), 
                        media_type=fileInfo.file_type,
                        headers = {"content-disposition":content_disposition})
    
    except(BotoCoreError, ClientError, HTTPException, Exception) as e:
            raise HTTPException(400, detail=f"{str(e.detail)}")

        
"""Updates file metadata for a specific file_id"""
@router.put("/")
def update_file( file_id: Annotated[str, Query(min_length=36, max_length=36, description= "Please enter a valid UUID")], file: Annotated[UploadFile, File()], 
                    current_user: Annotated[Users, Depends(get_current_active_user)],
                    db:Session=Depends(get_db)):
    try:
        #Validates if the file is associated with current logged-in user
        fileInfo = validate_file(file_id=file_id, user_id=current_user.user_id,  db=db)
        if fileInfo is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this operation!",
            )
        file_id = file_update(file_id=file_id, file=file, current_user=current_user, db=db)
    except(BotoCoreError, ClientError, HTTPException, Exception) as e:
        raise HTTPException(status_code=e.status_code, detail=f"{str(e.detail)}")
    return {"file_id":file_id}

    
"""Deletes file from S3 and database for given file_id"""
@router.delete("/")
def delete_file( file_id: Annotated[str, Query(min_length=36, max_length=36, description= "Please enter a valid UUID")], current_user: Annotated[Users, Depends(get_current_active_user)],
                       db:Session=Depends(get_db)):
    try:
        file_info = validate_file(file_id=file_id, user_id=current_user.user_id,  db=db)
        if file_info is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this operation!",
            )
        # Delete files from s3
        response = delete_file_s3(filename= file_info.filename)
       
        # Delete file from db
        message = delete_user_file(file_id=file_id, user_id=current_user.user_id, db=db)
        if message.get("error"):
            raise HTTPException(detail=message.get("error"), status_code=status.HTTP_400_BAD_REQUEST)
    
    except(BotoCoreError, ClientError, HTTPException, Exception) as e:
        raise HTTPException(status_code=e.status_code, detail=f"{str(e.detail)}")

    return {"message": "File deleted successfully!"}
        



"""Retrieves file for a specific file_id"""
@router.get("/")
def fetch_user_files(current_user: Annotated[Users, Depends(get_current_active_user)], 
                       db:Session=Depends(get_db)):
    try:
        user_files: List[Files] = get_user_files(current_user.user_id, db=db)
        return user_files
    
    except(HTTPException, Exception) as e:
            raise HTTPException(400, detail=f"{str(e.detail)}")