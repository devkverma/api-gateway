from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api_gateway.repository.connection import get_db

db_router = APIRouter()


@db_router.get("/db")
async def database_health(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        await db.execute(text("SELECT 1"))

        return {
            "status_code": 200,
            "response" : "Database connected successfully"
        }
    except Exception as e:
        return {
            "status_code": 500,
            "error": f"Internal server error: {e}"
        }