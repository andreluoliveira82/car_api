# ==============================================================================
# File: car_api/routers/brands.py
# Description: FastAPI router for brand-related operations in the Car API.
# ==============================================================================

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.core.database import get_db_session
from car_api.models.cars import Brand
from car_api.schemas.brands import (
    BrandListPublicSchema,
    BrandPublicSchema,
)

router = APIRouter(prefix='/brands', tags=['brands'])


# ==============================================================================
@router.get(
    path='/{brand_id}',
    response_model=BrandPublicSchema,
    summary='Obter marca por ID',
    description='Retorna os dados públicos de uma marca.',
)
async def get_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> BrandPublicSchema:
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Marca não encontrada.',
        )
    return brand


# ==============================================================================
@router.get(
    path='/',
    response_model=BrandListPublicSchema,
    summary='Listar marcas',
    description='Lista marcas com paginação e filtros opcionais.',
)
async def list_brands(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    db: AsyncSession = Depends(get_db_session),
) -> BrandListPublicSchema:
    query = select(Brand)

    if search:
        query = query.where(Brand.name.ilike(f'%{search}%'))

    if is_active is not None:
        query = query.where(Brand.is_active == is_active)

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    brands = result.scalars().all()

    return BrandListPublicSchema(
        brands=brands,
        offset=offset,
        limit=limit,
        total=total,
    )
