import pytest
from api_gateway.service.api_service import delete_api, create_api, get_api_by_id
from api_gateway.dto.api_dto import APICreate


@pytest.mark.anyio
async def test_delete_api(db):
    api = await create_api(
        db,
        APICreate(
            slug="weather-api",
            base_url="https://example.com",
            allowed_methods="GET",
        ),
    )

    deleted = await delete_api(db, api.id)

    assert deleted is True

    result = await get_api_by_id(db, api.id)

    assert result is None

@pytest.mark.anyio
async def test_delete_missing_api_returns_false(db):
    import uuid

    deleted = await delete_api(
        db,
        uuid.uuid4(),
    )

    assert deleted is False