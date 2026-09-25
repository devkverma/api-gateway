from fastapi import FastAPI
from api_gateway.health.health import health_router
from api_gateway.controller.rest_controller import rest_router

app = FastAPI()

app.include_router(health_router)
app.include_router(rest_router)