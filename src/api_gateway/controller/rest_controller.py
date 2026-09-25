from fastapi import APIRouter
from api_gateway.controller.api_controller import api_router

rest_router = APIRouter()

rest_router.include_router(api_router)

