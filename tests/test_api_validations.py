import pytest
from pydantic import ValidationError

from api_gateway.dto.api_dto import APICreate

def test_valid_api():
    api = APICreate(
        slug = "weather-api",
        base_url = "https://api.example.com",
        description = "Weather API",
        allowed_methods = "GET,POST",
    )

    assert api.slug == "weather-api"
    assert api.allowed_methods == "GET,POST"

def test_invalid_slug():
    with pytest.raises(ValidationError):
        APICreate(
            slug = "weather api",
            base_url = "https://api.example.com",
            allowed_methods = "GET",
        )

def test_invalid_method():
    with pytest.raises(ValidationError):
        APICreate(
            slug = "weather-api",
            base_url = "https://api.example.com",
            allowed_methods = "GET,WHATEVER",
        )

def test_invalid_url():
    with pytest.raises(ValidationError):
        APICreate(
            slug = "weather-api",
            base_url = "not-a-url",
            allowed_methods = "GET"
        )