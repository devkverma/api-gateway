"""
Resolve upstream API by slug ✅
Validate requested HTTP method against allowed_methods
Construct the upstream URL
Forward query parameters
Forward request headers/body appropriately
Call upstream with httpx.AsyncClient
Return the upstream response
Handle upstream failures
timeout → 504 Gateway Timeout
connection failure → 502 Bad Gateway
unknown slug → 404
method not allowed → 405
Add integration tests for the proxy flow.
"""

def is_method_allowed(api: API, method: str):
    allowed_methods = {
        item.strip().upper()
        for item in api.allowed_methods.split(",")
    }

    return method.upper() in allowed_methods

