import pytest

from api_gateway.service.api_service import search_api, create_api
from api_gateway.dto.api_dto import APICreate

@pytest.mark.anyio
async def test_search_api_by_slug(db):
    api = APICreate(
        slug="weather-api",
        base_url="https://example.api.com",
        allowed_methods="GET",
    )

    await create_api(db, api)

    results = await search_api(db, "weather")

    assert len(results) == 1
    assert results[0].slug == "weather-api"

@pytest.mark.anyio
async def test_search_api_by_description(db):
    api = APICreate(
        slug="xyz",
        base_url="https://example.api.com",
        description="current weather service",
        allowed_methods="GET",
    )

    await create_api(db, api)

    results = await search_api(db, "weather")

    assert len(results) == 1
    assert results[0].description == "current weather service"

@pytest.mark.anyio
async def test_search_api_by_base_url(db):
    api = APICreate(
        slug="xyz",
        base_url="https://weather.api.com",
        allowed_methods="GET",
    )

    await create_api(db, api)

    results = await search_api(db, "weather")

    assert len(results) == 1
    assert str(results[0].base_url) == "https://weather.api.com/"