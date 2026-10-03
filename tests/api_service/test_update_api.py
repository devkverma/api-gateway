import pytest
from api_gateway.service.api_service import create_api, update_api
from api_gateway.dto.api_dto import APICreate

@pytest.mark.anyio
async def test_update_api(db):
    api_old = APICreate(
        slug="weather-v1",
        base_url="https://example.api.com",
        allowed_methods="GET",
    )

    api = await create_api(db, api_old)

    api_new = APICreate(
        slug="weather-v2",
        base_url="https://weather.api.com",
        allowed_methods="GET,POST",
    )

    updated = await update_api(db, api.id, api_new)

    assert updated is not None
    assert updated.id == api.id
    assert updated.slug == "weather-v2"
    assert str(updated.base_url) == "https://weather.api.com/"
    assert updated.allowed_methods == "GET,POST"

@pytest.mark.anyio
async def test_update_missing_api_returns_none(db):
    import uuid

    result = await update_api(
        db,
        uuid.uuid4(),
        APICreate(
            slug="weather-api",
            base_url="https://example.com",
            allowed_methods="GET",
        ),
    )

    assert result is None