from contextlib import asynccontextmanager
import httpx

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api_gateway.controller.api_controller import api_router
from api_gateway.core.exceptions import APIConflictError
from api_gateway.core.logging import get_logger
from api_gateway.health.health import health_router
from api_gateway.controller.proxy_controller import proxy_router

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    timeout = httpx.Timeout(
        connect=5.0,
        read=10.0,
        write=10.0,
        pool=5.0,
    )

    limits = httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
    )

    app.state.http_client = httpx.AsyncClient(
        timeout=timeout,
        limits=limits,
    )

    yield

    await app.state.http_client.aclose()

app = FastAPI(
    title="API Gateway",
    lifespan=lifespan
    )

app.include_router(health_router)
app.include_router(api_router)
app.include_router(proxy_router)


@app.exception_handler(APIConflictError)
async def api_conflict_handler(
    request: Request,
    exc: APIConflictError,
):
    logger.warning(
        "API conflict: method=%s path=%s slug=%s",
        request.method,
        request.url.path,
        exc.slug,
    )

    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )