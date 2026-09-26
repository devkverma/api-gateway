from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from api_gateway.repository.models import API
from uuid import UUID
from api_gateway.core.logging import get_logger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from api_gateway.core.exceptions import APIConflictError

logger = get_logger()

# Create api
async def create_api(
    db: AsyncSession,
    api_data: APICreate,
):

    api = API(
        slug = api_data.slug,
        base_url = api_data.base_url,
        description = api_data.description,
        allowed_methods = api_data.allowed_methods,
    )

    try:
        db.add(api)
        await db.commit()
        await db.refresh(api)

    except IntegrityError as exc:
        await db.rollback()

        if "apis_slug_key" in str(exc.orig):
            logger.warning(
                "API creation failed: slug=%s already exists",
                api_data.slug,
            )
            raise APIConflictError(api_data.slug) from exc

        logger.exception("Unexpected integrity error while creating API")
        raise

    except SQLAlchemyError:
        await db.rollback()

        logger.exception(
            "Database error while creating API: slug=%s",
            api_data.slug,
        )

        raise

    logger.info(
        "API created successfully: id=%s slug=%s",
        api.id,
        api.slug,
    )

    return api

# fetch all apis
async def get_all_apis(db: AsyncSession):
    result = await db.execute(select(API))
    return result.scalars().all()

# fetch by id
async def get_api_by_id(db: AsyncSession, api_id: UUID):
    result = await db.execute(
        select(API).where(API.id == api_id)
    )

    return result.scalar_one_or_none()

# search through api
async def search_api(db: AsyncSession, query: str):
    search_pattern = f"%{query}%"

    result = await db.execute(
        select(API).where(
            or_(
                API.slug.ilike(search_pattern),
                API.base_url.ilike(search_pattern),
                API.description.ilike(search_pattern),
            )
        )
    )

    return result.scalars().all()

# update api
async def update_api(
    db: AsyncSession,
    api_id: UUID,
    api_data: APICreate,
):
    api = await get_api_by_id(db, api_id)

    if not api:
        return None
    
    api.slug = api_data.slug
    api.base_url = api_data.base_url
    api.description = api_data.description
    api.allowed_methods = api_data.allowed_methods

    await db.commit()
    await db.refresh(api)

    return api

async def delete_api(
    db: AsyncSession,
    api_id: UUID,
):
    api = await get_api_by_id(db, api_id)

    if not api:
        return False

    await db.delete(api)
    await db.commit()

    return True