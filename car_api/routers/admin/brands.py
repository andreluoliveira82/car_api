# ==============================================================================
# File: car_api/routers/admin/brands.py
# Description: Administrative routes for managing brands in the Car API.
# ==============================================================================


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.core.database import get_db_session
from car_api.core.security import require_admin
from car_api.models.cars import Brand
from car_api.models.users import User
from car_api.schemas.brands import (
    BrandCreateSchema,
    BrandPublicSchema,
    BrandUpdateSchema,
)

router = APIRouter(
    prefix='/admin/brands',
    tags=['admin - brands'],
)


# ==============================================================================
@router.post(
    '/',
    response_model=BrandPublicSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Criar marca',
    description='Cria uma nova marca no catálogo. Acesso restrito a administradores.',
)
async def create_brand(
    brand_data: BrandCreateSchema,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    exists_brand = await db.scalar(select(exists().where(Brand.name == brand_data.name)))
    if exists_brand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Já existe uma marca cadastrada com esse nome.',
        )

    brand = Brand(
        name=brand_data.name,
        description=brand_data.description,
        is_active=True,
    )

    db.add(brand)
    await db.commit()
    await db.refresh(brand)

    return brand


# ==============================================================================
@router.put(
    '/{brand_id}',
    response_model=BrandPublicSchema,
    summary='Atualizar marca',
    description='Atualiza os dados de uma marca existente.',
)
async def update_brand(
    brand_id: int,
    brand_update: BrandUpdateSchema,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Marca não encontrada.',
        )

    if brand_update.name and brand_update.name != brand.name:
        exists_brand = await db.scalar(
            select(
                exists().where(Brand.name == brand_update.name).where(Brand.id != brand_id)
            )
        )
        if exists_brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Já existe outra marca com esse nome.',
            )

    for field, value in brand_update.model_dump(exclude_unset=True).items():
        setattr(brand, field, value)

    await db.commit()
    await db.refresh(brand)

    return brand


# ==============================================================================
@router.patch(
    '/{brand_id}/activate',
    response_model=BrandPublicSchema,
    summary='Ativar marca',
)
async def activate_brand(
    brand_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Marca não encontrada.',
        )

    brand.is_active = True
    await db.commit()
    await db.refresh(brand)

    return brand


# ==============================================================================
@router.patch(
    '/{brand_id}/deactivate',
    response_model=BrandPublicSchema,
    summary='Desativar marca',
)
async def deactivate_brand(
    brand_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Marca não encontrada.',
        )

    brand.is_active = False
    await db.commit()
    await db.refresh(brand)

    return brand


# ==============================================================================
@router.delete(
    '/{brand_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Excluir marca',
)
async def delete_brand(
    brand_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    has_cars = await db.scalar(
        select(exists().where(Brand.id == brand_id).where(Brand.cars.any()))
    )
    if has_cars:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Não é possível deletar a marca porque existem carros associados.',
        )

    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Marca não encontrada.',
        )

    await db.delete(brand)
    await db.commit()
