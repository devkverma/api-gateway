import pytest
from api_gateway.service.api_service import create_api, get_api_by_slug
from api_gateway.dto.api_dto import APICreate

@pytest.mark.anyio
async def test_get_api_by_slug(db):
    api_data = APICreate(
        slug="weather-api",
        base_url="https://api.example.com",
        allowed_methods="GET",
    )

    created_api = await create_api(db, api_data)

    api = await get_api_by_slug(db, created_api.slug)

    assert api is not None
    assert api.id == created_api.id
    assert api.slug == "weather-api"

@pytest.mark.anyio
async def test_get_api_by_slug_returns_none_for_missing_api(db):
    import uuid

    api = await get_api_by_slug(db, "random-slug")

    assert api is None