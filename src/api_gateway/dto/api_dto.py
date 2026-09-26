from pydantic import BaseModel
from uuid import UUID

class APICreate(BaseModel):
    slug: str
    base_url: str
    description: str | None = None
    allowed_methods: str

class APIResponse(BaseModel):
    id: UUID
    slug: str
    base_url: str
    description: str | None = None
    allowed_methods: str
    
    model_config = {
        "from_attributes" : True
    }
