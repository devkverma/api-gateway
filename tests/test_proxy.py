import pytest
import httpx
from httpx import AsyncClient, ASGITransport, Response
from unittest.mock import AsyncMock

from api_gateway.main import app
from api_gateway.dto.api_dto import APICreate
from api_gateway.service.api_service import create_api

from starlette.datastructures import QueryParams


@pytest.mark.anyio
async def test_proxy_get(
    db,
    override_get_db,
    mock_http_client,
):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    mock_http_client.request = AsyncMock(
        return_value=Response(
            status_code=200,
            json={"message": "hello"},
        )
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/proxy/myapi")

    assert response.status_code == 200
    assert response.json() == {"message": "hello"}

@pytest.mark.anyio
async def test_proxy_forwards_path_and_query_params(
    db,
    override_get_db,
    mock_http_client,
):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    mock_response = Response(
        status_code=200,
        json={"message": "hello"},
    )

    mock_request = AsyncMock(return_value=mock_response)
    mock_http_client.request = mock_request

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:

            response = await client.get(
                "/proxy/myapi/users?id=123"
            )

    assert response.status_code == 200
    assert response.json() == {"message": "hello"}

    mock_request.assert_awaited_once()

    call_kwargs = mock_request.await_args.kwargs

    assert call_kwargs["method"] == "GET"
    assert call_kwargs["url"] == "https://example.com/users"
    assert call_kwargs["params"] == QueryParams("id=123")
    assert call_kwargs["content"] == b""

@pytest.mark.anyio
async def test_proxy_forwards_post_body(
    db,
    override_get_db,
    mock_http_client,
):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="POST",
    )

    await create_api(db, api_data)

    mock_response = Response(
        status_code=201,
        json={"id": 123},
    )

    mock_request = AsyncMock(return_value=mock_response)
    mock_http_client.request = mock_request

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/proxy/myapi/users",
            json={"name": "John"},
        )

    assert response.status_code == 201
    assert response.json() == {"id": 123}

    mock_request.assert_awaited_once()

    call_kwargs = mock_request.await_args.kwargs

    assert call_kwargs["method"] == "POST"
    assert call_kwargs["url"] == "https://example.com/users"
    assert call_kwargs["content"] == b'{"name":"John"}'

@pytest.mark.anyio
async def test_proxy_returns_404_for_unknown_slug(db, override_get_db):
    response = None

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/proxy/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "API 'does-not-exist' not found"
    }

@pytest.mark.anyio
async def test_proxy_rejects_disallowed_method(db, override_get_db):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post("/proxy/myapi")

    assert response.status_code == 405
    assert response.json() == {
        "detail": "Method 'POST' is not allowed"
    }

@pytest.mark.anyio
async def test_proxy_preserves_upstream_status_code(
    db,
    override_get_db,
    mock_http_client,
):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    mock_response = Response(
        status_code=404,
        json={"detail": "Resource not found"},
    )

    mock_http_client.request = AsyncMock(
        return_value=mock_response
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/proxy/myapi/users")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Resource not found"
    }

@pytest.mark.anyio
async def test_proxy_preserves_upstream_500(
    db,
    override_get_db,
    mock_http_client,
):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    mock_response = Response(
        status_code=500,
        json={"detail": "Upstream failure"},
    )

    mock_http_client.request = AsyncMock(
        return_value=mock_response
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/proxy/myapi")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Upstream failure"
    }

@pytest.mark.anyio
async def test_proxy_returns_502_when_upstream_unreachable(
    db,
    override_get_db,
    mock_http_client,
):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    mock_http_client.request = AsyncMock(
        side_effect=httpx.ConnectError("Connection failed")
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/proxy/myapi")

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Unable to connect to upstream API"
    }

@pytest.mark.anyio
async def test_proxy_returns_504_on_connect_timeout(
    db,
    override_get_db,
    mock_http_client,
):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    mock_http_client.request = AsyncMock(
        side_effect=httpx.ConnectTimeout("Connection timed out")
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/proxy/myapi")

    assert response.status_code == 504
    assert response.json() == {
        "detail": "Upstream API request timed out"
    }

@pytest.mark.anyio
async def test_proxy_returns_504_on_read_timeout(
    db,
    override_get_db,
    mock_http_client,
):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    mock_http_client.request = AsyncMock(
        side_effect=httpx.ReadTimeout("Read timed out")
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/proxy/myapi")

    assert response.status_code == 504
    assert response.json() == {
        "detail": "Upstream API request timed out"
    }

@pytest.mark.anyio
async def test_proxy_forwards_request_headers(
    db,
    override_get_db,
    mock_http_client,
):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    mock_http_client.request = AsyncMock(
        return_value=Response(
            status_code=200,
            json={"message": "hello"},
        )
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/proxy/myapi",
            headers={
                "Authorization": "Bearer test-token",
                "X-Request-ID": "abc123",
            },
        )

    assert response.status_code == 200

    call_kwargs = mock_http_client.request.await_args.kwargs

    assert call_kwargs["headers"]["authorization"] == "Bearer test-token"
    assert call_kwargs["headers"]["x-request-id"] == "abc123"

@pytest.mark.anyio
async def test_proxy_filters_hop_by_hop_headers(
    db,
    override_get_db,
    mock_http_client,
):
    api_data = APICreate(
        slug="myapi",
        base_url="https://example.com",
        description="Test API",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    mock_http_client.request = AsyncMock(
        return_value=Response(
            status_code=200,
            json={"message": "hello"},
        )
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/proxy/myapi",
            headers={
                "Authorization": "Bearer test-token",
                "X-Request-ID": "abc123",
                "Connection": "keep-alive",
                "Transfer-Encoding": "chunked",
            },
        )

    assert response.status_code == 200

    call_kwargs = mock_http_client.request.await_args.kwargs
    headers = call_kwargs["headers"]

    assert headers["authorization"] == "Bearer test-token"
    assert headers["x-request-id"] == "abc123"

    assert "connection" not in headers
    assert "transfer-encoding" not in headers