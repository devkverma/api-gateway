from pydantic import BaseModel, Field, HttpUrl, field_validator
from uuid import UUID

class APICreate(BaseModel):
    slug: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    base_url: HttpUrl
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    allowed_methods: str

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        value = value.strip().lower()

        if not value:
            raise ValueError("Slug can not be empty")
        return value

    @field_validator("allowed_methods")
    @classmethod
    def validate_allowed_methods(cls, value : str) -> str:
        allowed_methods = {
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
            "HEAD",
        }

        methods = {
            method.strip().upper()
            for method in value.split(",")
            if method.strip()
        }

        if not methods:
            raise ValueError("At least one http method is required")

        invalid_methods = methods - allowed_methods

        if invalid_methods:
            raise ValueError(
                f"Unsupported HTTP method: {', '.join(sorted(invalid_methods))}"
            )

        return ",".join(sorted(methods))

class APIResponse(BaseModel):
    id: UUID
    slug: str
    base_url: str
    description: str | None = None
    allowed_methods: str
    
    model_config = {
        "from_attributes" : True
    }
