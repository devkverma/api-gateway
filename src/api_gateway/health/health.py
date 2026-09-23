from fastapi import APIRouter
from api_gateway.health.db import db_router
from api_gateway.health.server import server_router

health_router = APIRouter(prefix = "/health")

health_router.include_router(db_router)
health_router.include_router(server_router)