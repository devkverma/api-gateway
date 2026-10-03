import httpx

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from api_gateway.repository.connection import get_db
from api_gateway.service.api_service import get_api_by_slug
from api_gateway.service.proxy_service import (
    build_upstream_url,
    is_method_allowed,
    build_downstream_headers,
)
from api_gateway.controller.utils import forward_request
from api_gateway.core.logging import get_logger


logger = get_logger()

proxy_router = APIRouter(
    prefix="/proxy",
    tags=["Proxy"],
)

DBSession = Annotated[
    AsyncSession,
    Depends(get_db),
]


@proxy_router.api_route(
    "/{slug}/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "HEAD",
    ],
)
async def proxy_request(
    slug: str,
    path: str,
    request: Request,
    db: DBSession,
):
    logger.info(
        "Proxy request received: method=%s slug=%s path=%s",
        request.method,
        slug,
        path,
    )

    try:
        api = await get_api_by_slug(db, slug)

    except SQLAlchemyError:
        logger.exception(
            "Database error while looking up API: slug=%s",
            slug,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API configuration",
        )

    if api is None:
        logger.warning(
            "Proxy request rejected: API not found: slug=%s",
            slug,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API '{slug}' not found",
        )

    if not is_method_allowed(api, request.method):
        logger.warning(
            "Proxy request rejected: method not allowed: "
            "method=%s slug=%s allowed_methods=%s",
            request.method,
            slug,
            api.allowed_methods,
        )
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"Method '{request.method}' is not allowed",
        )

    try:
        upstream_url = build_upstream_url(api, path)

    except Exception:
        logger.exception(
            "Failed to build upstream URL: slug=%s path=%s",
            slug,
            path,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to build upstream request",
        )

    try:
        client: httpx.AsyncClient = request.app.state.http_client

    except AttributeError:
        logger.exception(
            "HTTP client is not configured: slug=%s",
            slug,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Proxy HTTP client is not configured",
        )

    logger.info(
        "Forwarding request: method=%s slug=%s upstream_url=%s",
        request.method,
        slug,
        upstream_url,
    )

    try:
        response = await forward_request(
            client=client,
            request=request,
            upstream_url=upstream_url,
        )

    except HTTPException:
        logger.exception(
            "Upstream request failed: method=%s slug=%s upstream_url=%s",
            request.method,
            slug,
            upstream_url,
        )
        raise

    except Exception:
        logger.exception(
            "Unexpected error while proxying request: "
            "method=%s slug=%s upstream_url=%s",
            request.method,
            slug,
            upstream_url,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected error while communicating with upstream API",
        )

    if response.status_code >= 400:
        logger.warning(
            "Upstream returned error: method=%s slug=%s upstream_url=%s status_code=%s",
            request.method,
            slug,
            upstream_url,
            response.status_code,
        )
    else:
        logger.info(
            "Upstream response received: method=%s slug=%s status_code=%s",
            request.method,
            slug,
            response.status_code,
        )

    try:
        downstream_headers = build_downstream_headers(
            response.headers
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=downstream_headers,
            media_type=response.headers.get("content-type"),
        )

    except Exception:
        logger.exception(
            "Failed to build downstream response: "
            "method=%s slug=%s upstream_url=%s status_code=%s",
            request.method,
            slug,
            upstream_url,
            response.status_code,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to process upstream response",
        )


@proxy_router.api_route(
    "/{slug}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "HEAD",
    ],
)
async def proxy_route_root(
    slug: str,
    request: Request,
    db: DBSession,
):
    return await proxy_request(
        slug=slug,
        path="",
        request=request,
        db=db,
    )