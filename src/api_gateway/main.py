from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api_gateway.controller.rest_controller import rest_router
from api_gateway.core.exceptions import APIConflictError
from api_gateway.core.logging import get_logger
from api_gateway.health.health import health_router

logger = get_logger()

app = FastAPI()

app.include_router(health_router)
app.include_router(rest_router)


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