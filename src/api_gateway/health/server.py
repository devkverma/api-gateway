from fastapi import APIRouter, Depends

server_router = APIRouter()


@server_router.get("/server")
def server_health():
    """
    This endpoint will help us to know the status of the server.
    """
    return {
        "status_code": 200,
        "response": "OK"
    }