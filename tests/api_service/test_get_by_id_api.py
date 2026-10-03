import pytest
from api_gateway.service.api_service import create_api, get_api_by_id
from api_gateway.dto.api_dto import APICreate

@pytest.mark.anyio
async def test_get_api_by_id(db):
    api_data = APICreate(
        slug="weather-api",
        base_url="https://api.example.com",
        allowed_methods="GET",
    )

    created_api = await create_api(db, api_data)

    api = await get_api_by_id(db, created_api.id)

    assert api is not None
    assert api.id == created_api.id
    assert api.slug == "weather-api"

@pytest.mark.anyio
async def test_get_api_by_id_returns_none_for_missing_api(db):
    import uuid

    api = await get_api_by_id(db, uuid.uuid4())

    assert api is None