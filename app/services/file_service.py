from fastapi import UploadFile
from db.models.users import Users
from sqlalchemy.orm import Session
from utils.aws_s3_utility import s3_file_upload
from db.models.files import Files, create_file, update_file_info, list_user_files
import time
from typing import List
import math

"""
Uploads file to S3 and then saves the file details in database
"""
def file_upload(file: UploadFile, current_user: Users, db:Session):
   
    temp = file.filename.split('.')
    # Generate a unique filename to upload to S3 to prevent from overwriting
    s3_filename = temp[0] + "-" + str(int(time.time())) +  "." + temp[1]
    # Uploads file to s3
    s3_file_upload(file.file, filename=s3_filename)
    # save file metadata in database
    file_id = create_file(filename=s3_filename, file_size=file.size, file_type=file.content_type, user_id=current_user.user_id , db=db)
    return file_id



"""Uploads the modified file to s3 and updates file metadata for given file_id"""
def file_update(file_id :str, file: UploadFile, current_user: Users, db:Session):
    temp = file.filename.split('.')
    s3_filename = temp[0] + "-" + str(int(time.time())) +  "." + temp[1]
    url = s3_file_upload(file.file, filename=s3_filename)
    update_file_info(file_id=file_id, filename=s3_filename, file_size=file.size, file_type=file.content_type, user_id=current_user.user_id , db=db)
    return file_id

"""Converts Size in bytes to more readable format"""
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

""" Get user files"""
def get_user_files(user_id:int, db:Session):
    user_files:List[Files] = list_user_files(user_id=user_id, db=db)
    for file in user_files:
        file.file_size = convert_size(file.file_size)
        temp = file.filename.split('-')
        file.filename = "-".join(temp[:-1]) + '.' + temp[-1].split('.')[1]
    return user_files