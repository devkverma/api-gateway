import pytest
from api_gateway.service.api_service import get_all_apis, create_api
from api_gateway.dto.api_dto import APICreate

@pytest.mark.anyio
async def test_get_all_apis(db):
    api_one = APICreate(
        slug="weather-api",
        base_url="https://weather.example.com",
        allowed_methods="GET",
    )

    api_two = APICreate(
        slug="jokes-api",
        base_url="https://jokes.example.com",
        allowed_methods="GET",
    )

    await create_api(db, api_one)
    await create_api(db, api_two)

    apis = await get_all_apis(db)

    assert len(apis) == 2