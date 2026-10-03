from api_gateway.repository.models import API


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host",
}

def is_method_allowed(api: API, method: str):
    allowed_methods = {
        item.strip().upper()
        for item in api.allowed_methods.split(",")
    }

    return method.upper() in allowed_methods

def build_upstream_url(api: API, path: str) -> str:
    return f"{str(api.base_url).rstrip('/')}/{path.lstrip('/')}"

def build_upstream_headers(headers) -> dict[str, str]:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

def build_downstream_headers(headers) -> dict[str, str]:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }