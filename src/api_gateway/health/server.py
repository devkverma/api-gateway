from fastapi import APIRouter, Depends

server_router = APIRouter()


@server_router.get("/server")
def server_health():
    return {
        "status_code": 200,
        "response": "OK"
    }