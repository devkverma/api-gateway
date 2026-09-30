import pytest

from api_gateway.dto.api_dto import APICreate
from api_gateway.service.api_service import create_api
from api_gateway.core.exceptions import APIConflictError

@pytest.mark.anyio
async def test_create_api(db):
    api_data = APICreate(
        slug="weather-api",
        base_url="https://api.example.com",
        description="Weather API",
        allowed_methods="GET",
    )

    api = await create_api(db, api_data)

    assert api.id is not None
    assert api.slug == "weather-api"
    assert str(api.base_url) == "https://api.example.com/"
    assert api.description == "Weather API"
    assert api.allowed_methods == "GET"

@pytest.mark.anyio
async def test_create_api_rejects_duplicate_slug(db):
    api_data = APICreate(
        slug="weather-api",
        base_url="https://example.com",
        allowed_methods="GET",
    )

    await create_api(db, api_data)

    with pytest.raises(APIConflictError):
        await create_api(db, api_data)