import boto3
import os
from fastapi import HTTPException
from botocore.exceptions import BotoCoreError, ClientError
import os

AWS_ACCESS_KEY_ID= os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY= os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME= os.getenv("AWS_S3_BUCKET_NAME")
AWS_REGION= os.getenv("AWS_REGION")

session = boto3.Session(
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name = AWS_REGION
)

s3_client = session.client('s3')

def s3_file_upload(file_data , filename: str):
    """
    Uploads given file to s3
    """
    try:
        s3_client.upload_fileobj(file_data, BUCKET_NAME, filename)
        location = session.client('s3').get_bucket_location(Bucket=BUCKET_NAME)['LocationConstraint']
        url = f"https://{BUCKET_NAME}.s3.{location}.amazonaws.com/{filename}"
        return url
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=400, detail=f"Failed to upload file to S3: {str(e)}")
     


def s3_file_download(filename:str):
    """
    Downloads file from S3
    """
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=filename)
        return response
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=400, detail=f"Failed to upload file to S3: {str(e)}")



def delete_file_s3(filename:str):
    """
    Deletes File from s3
    """
    try:
        response = s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 204:
            return response
        else:
            raise HTTPException(status_code=400, detail=f"Invalid Input!")
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete file from S3: {str(e)}")
