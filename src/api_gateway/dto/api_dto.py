from pydantic import BaseModel

class APICreate(BaseModel):
    slug: str
    base_url: str
    description: str | None = None

class APIResponse(BaseModel):
    id: int
    slug: str
    base_url: str
    description: str | None = None

    model_config = {
        "from_attributes" : True
    }
