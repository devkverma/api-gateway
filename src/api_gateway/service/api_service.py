from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api_gateway.repository.models import API

# Create api
async def create_api(
    db: AsyncSession,
    api_data: APICreate,
):

    api = API(
        slug = api_data.slug,
        base_url = api_data.base_url,
        description = api_data.description,
    )

    db.add(api)
    await db.commit()
    await db.refresh(api)

    return api

# fetch all apis
async def get_all_apis(db: AsyncSession):
    result = await db.execute(select(API))
    return result.scalars().all()

# fetch by id
async def get_api_by_id(db: AsyncSession, api_id: int):
    result = await db.execute(
        select(API).where(API.id == api_id)
    )

    return result.scalar_one_or_none()

# update api
async def update_api(
    db: AsyncSession,
    api_id: int,
    api_data: APICreate,
):
    api = await get_api_by_id(db, api_id)

    if not api:
        return None
    
    api.slug = api_data.slug
    api.base_url = api_data.slug
    api.description = api_data.description

    await db.commit()
    await db.refresh(api)

    return api

async def delete_api(
    db: AsyncSession,
    api_id: int,
):
    api = await get_api_by_id(db, api_id)

    if not api:
        return False

    await db.delete(api)
    await db.commit()

    return True