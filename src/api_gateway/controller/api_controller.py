from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api_gateway.repository.connection import get_db
from api_gateway.service.api_service import (
    create_api,
    delete_api,
    get_all_apis,
    get_api_by_id,
    update_api,
)
from api_gateway.dto.api_dto import APICreate, APIResponse


api_router = APIRouter(
    prefix="/apis",
    tags=["APIs"],
)

DBSession = Annotated[AsyncSession, Depends(get_db)]


@api_router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_api_endpoint(
    db: DBSession,
    data: APICreate,
):
    return await create_api(db, data)


@api_router.get(
    "/",
    response_model=list[APIResponse],
    status_code=status.HTTP_200_OK,
)
async def list_apis_endpoint(
    db: DBSession,
):
    return await get_all_apis(db)


@api_router.get(
    "/{api_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
async def get_api_endpoint(
    db: DBSession,
    api_id: int,
):
    api = await get_api_by_id(db, api_id)

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API with id {api_id} not found",
        )

    return api


@api_router.put(
    "/{api_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
async def update_api_endpoint(
    db: DBSession,
    api_id: int,
    api_data: APICreate,
):
    api = await update_api(db, api_id, api_data)

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API with id {api_id} not found",
        )

    return api


@api_router.delete(
    "/{api_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_api_endpoint(
    db: DBSession,
    api_id: int,
):
    deleted = await delete_api(db, api_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API with id {api_id} not found",
        )