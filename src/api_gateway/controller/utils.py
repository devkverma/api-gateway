import httpx
from fastapi import HTTPException
from api_gateway.service.proxy_service import build_upstream_headers
from api_gateway.core.logging import get_logger

logger = get_logger()

async def forward_request(
    client: httpx.AsyncClient,
    request,
    upstream_url: str,
):
    headers = build_upstream_headers(request.headers)

    logger.info(
        "Forwarding headers: %s",
        headers,
    )

    try:
        return await client.request(
            method=request.method,
            url=upstream_url,
            params=request.query_params,
            headers=headers,
            content=await request.body(),
        )

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Upstream API request timed out",
        ) from exc

    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to upstream API",
        ) from exc

    except httpx.NetworkError as exc:
        raise HTTPException(
            status_code=502,
            detail="Network error while contacting upstream API",
        ) from exc

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Error while communicating with upstream API",
        ) from exc