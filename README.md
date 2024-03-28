# fastapi-boilerplate-alembic-postgres-docker

## Overview
This Project is a FastAPI application that utilizes PostgresSQL for data storage and AWS S3 for file storage.

## Prerequisites
- Docker and Docker Compose
- An AWS account 

## Setup
1. Clone the repository
    ```https://github.com/priyankaNav/fastapi-boilerplate-alembic-pg```
2. Navigate to app folder
    ```$ cd fastapi-boilerplate-alembic-pg/app```
3. Update docker-compose.yml 
    1. Update S3 `AWS_SECRET_ACCESS_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_S3_BUCKET_NAME`, `AWS_REGION`
    2. If `DATABASE_URL` is changed in docker-compose, make sure to update the same in `makefile` file
4. To run first time migration and create tables in database
    ```make migrate```
5. To run project
    ```docker-compose up```

## Usage
After running the application, you can access and explore the endpoints with Swagger UI at `http://127.0.0.1:8000/docs`.


