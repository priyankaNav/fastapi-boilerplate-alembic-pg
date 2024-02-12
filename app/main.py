from fastapi import FastAPI
from db.session import engine
from db.base import Base
from apis.base import api_router
from dotenv import load_dotenv

import os
load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME") 
PROJECT_VERSION = os.getenv("PROJECT_VERSION") 


def include_router(app):
    app.include_router(api_router)

def create_tables():    
    Base.metadata.create_all(bind = engine)

def start_application():
    app = FastAPI(title=PROJECT_NAME, version=PROJECT_VERSION)
    create_tables()
    include_router(app)
    return app

app = start_application()



