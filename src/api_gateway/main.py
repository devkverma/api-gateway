from fastapi import FastAPI
from api_gateway.health.health import health_router

app = FastAPI()

app.include_router(health_router)