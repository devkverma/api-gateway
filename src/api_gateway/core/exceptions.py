class APIException(Exception):
    """Base exception for application-specific errors."""


class APINotFoundError(APIException):
    def __init__(self, api_id):
        self.api_id = api_id
        super().__init__(f"API with id {api_id} not found")


class APIConflictError(APIException):
    def __init__(self, slug: str):
        self.slug = slug
        super().__init__(f"API with slug '{slug}' already exists")