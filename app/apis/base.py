from fastapi import APIRouter
from apis.v1 import user_registration_router
from apis.v1 import file_acess_router

api_router = APIRouter()

api_router.include_router(user_registration_router.router)
api_router.include_router(file_acess_router.router)
