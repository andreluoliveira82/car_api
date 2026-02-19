# ==============================================================================
# File: car_api/routers/brands.py
# Description: FastAPI router for handling car brand-related endpoints in the Car API.
# ==============================================================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from car_api.core.database import get_db_session
from car_api.models.cars import Brand
from car_api.schemas.brands import(
    BrandSchema, 
    BrandListPublicSchema, 
    BrandPublicSchema, 
    BrandUpdateSchema
)

router = APIRouter(
    prefix="/brands",
    tags=["brands"]
)


# ==============================================================================
@router.post(
    path="/", 
    response_model=BrandPublicSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Criar uma nova marca de carro",
    description="Endpoint para criar uma nova marca de carro no sistema."
)
async def create_brand(brand_data: BrandSchema, db: AsyncSession = Depends(get_db_session)) -> BrandPublicSchema:
    """
    Create a new car brand in the database.

    Args:
        brand_data (BrandSchema): The data for the new brand.
        db (AsyncSession): The database session.

    Returns:
        BrandPublicSchema: The created brand data.
    """

    # Verificar se já existe uma marca com o mesmo nome
    existing_brand = await db.scalar(
        select(exists().where(Brand.name == brand_data.name))
    )
    
    if existing_brand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma marca cadastrada com esse nome."
        )

    db_brand = Brand(
        name=brand_data.name,
        description=brand_data.description,
        is_active=brand_data.is_active    
    )

    db.add(db_brand)
    await db.commit()
    await db.refresh(db_brand)

    return db_brand

# ==============================================================================
@router.get(
    path="/{brand_id}",
    status_code=status.HTTP_200_OK,
    response_model=BrandPublicSchema,
    summary="Obter uma marca de carro específica",
    description="Endpoint para obter os detalhes de uma marca de carro específica."
)
async def get_brand(brand_id: int, db: AsyncSession = Depends(get_db_session)) -> BrandPublicSchema:
    """
    Get a specific car brand from the database.

    Args:
        brand_id (int): The ID of the brand to retrieve.
        db (AsyncSession): The database session.

    Returns:
        BrandPublicSchema: The retrieved brand data.
    """
    brand = await db.execute(select(Brand).where(Brand.id == brand_id))
    db_brand = brand.scalar_one_or_none()

    if not db_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca não encontrada."
        )

    return db_brand

# ==============================================================================

@router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=BrandListPublicSchema,
    summary="Listar todas as marcas de carros",
    description="Endpoint para listar todas as marcas de carros cadastradas no sistema."
)
async def list_brands(
    offset: int = Query(0, ge=0, description="Número de itens a pular para paginação."),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de itens a retornar."),
    search: Optional[str] = Query(None, description="Termo de busca para filtrar marcas por nome."),
    is_active: Optional[bool] = Query(None, description="Filtrar marcas por status ativo/inativo."),
    db: AsyncSession = Depends(get_db_session)
) -> BrandListPublicSchema:
    """
    List all car brands in the database.

    Args:
        offset (int): The number of items to skip for pagination.
        limit (int): The maximum number of items to return.
        search (Optional[str]): Search term to filter brands by name.
        is_active (Optional[bool]): Filter brands by active/inactive status.
        db (AsyncSession): The database session.

    Returns:
        BrandListPublicSchema: The list of all car brands wrapped in a public schema.
    """
    query = select(Brand)

    if search:
        search_term = f"%{search}%"
        query = query.where(Brand.name.ilike(search_term))
    
    if is_active is not None:
        query = query.where(Brand.is_active == is_active)

    query = query.offset(offset).limit(limit)
    
    brands = await db.execute(query)
    db_brands = brands.scalars().all()

    if not db_brands:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma marca encontrada.",
        )

    return {
        "brands": db_brands,
        "offset": offset,
        "limit": limit,
        "total": len(db_brands)
    }


#=============================================================================
@router.put(
    path="/{brand_id}",
    status_code=status.HTTP_200_OK,
    response_model=BrandPublicSchema,
    summary="Atualizar uma marca de carro existente",
    description="Endpoint para atualizar os detalhes de uma marca de carro existente no sistema."
)
async def update_brand(
    brand_id: int,
    brand_update: BrandUpdateSchema,
    db: AsyncSession = Depends(get_db_session)
) -> BrandPublicSchema:
    """
    Update an existing car brand in the database.

    Args:
        brand_id (int): The ID of the brand to update.
        brand_update (BrandUpdateSchema): The data to update the brand with.
        db (AsyncSession): The database session.

    Returns:
        BrandPublicSchema: The updated brand data.
    """
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    db_brand = result.scalar_one_or_none()

    if not db_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca não encontrada."
        )

    # Verificar se o nome da marca está sendo atualizado e se já existe outra marca com o mesmo nome
    if brand_update.name and brand_update.name != db_brand.name:
        existing_brand = await db.scalar(
            select(exists().where(Brand.name == brand_update.name).where(Brand.id != brand_id))
        )
        if existing_brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe outra marca cadastrada com esse nome."
            )

    for field, value in brand_update.dict(exclude_unset=True).items():
        setattr(db_brand, field, value)

    await db.commit()
    await db.refresh(db_brand)

    return db_brand


# ==============================================================================
# delete
@router.delete(
    path="/{brand_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar uma marca de carro",
    description="Endpoint para deletar uma marca de carro do sistema."
)
async def delete_brand(brand_id: int, db: AsyncSession = Depends(get_db_session)) -> None:
    """
    Delete a car brand from the database.

    Args:
        brand_id (int): The ID of the brand to delete.
        db (AsyncSession): The database session.

    Returns:
        None
    """
    # Verificar se existem carros associados à marca
    has_cars = await db.scalar(
        select(exists().where(Brand.id == brand_id).where(Brand.cars.any()))
    )

    if has_cars:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar a marca porque existem carros associados a ela."
        )

    # Verificar se a marca existe
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    db_brand = result.scalar_one_or_none()

    if not db_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca não encontrada."
        )

    await db.delete(db_brand)
    await db.commit()