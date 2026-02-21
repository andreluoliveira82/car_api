# ==============================================================================
# File: car_api/routers/admin/cars.py
# Description: Administrative routes for managing cars in the Car API.
# ==============================================================================

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from car_api.core.database import get_db_session
from car_api.core.security import require_admin
from car_api.models.cars import Brand, Car, CarStatus
from car_api.models.users import User
from car_api.schemas.cars import AdminCarCreateSchema, CarListPublicSchema, CarPublicSchema

router = APIRouter(
    prefix='/admin/cars',
    tags=['admin - cars'],
)


# ==============================================================================
@router.post(
    '/',
    response_model=CarPublicSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Criar carro para um usuário',
    description=(
        'Cria um novo carro no sistema em nome de um usuário específico. '
        'Acesso restrito a administradores.'
    ),
)
async def create_car_admin(
    car: AdminCarCreateSchema,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
) -> CarPublicSchema:
    """
    Create a new car on behalf of a user (administrative operation).
    """

    # ============================
    # Validar se a marca existe
    # ============================
    brand_exists = await db.scalar(select(exists().where(Brand.id == car.brand_id)))
    if not brand_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='A marca informada não existe.',
        )

    # ============================
    # Validar se o proprietário existe
    # ============================
    owner_exists = await db.scalar(select(exists().where(User.id == car.owner_id)))
    if not owner_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='O usuário proprietário informado não existe.',
        )

    # ============================
    # Validar placa duplicada
    # ============================
    plate_exists = await db.scalar(select(exists().where(Car.plate == car.plate)))
    if plate_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Já existe um carro cadastrado com esta placa.',
        )

    # ============================
    # Criar o carro
    # ============================
    db_car = Car(
        car_type=car.car_type,
        model=car.model,
        factory_year=car.factory_year,
        model_year=car.model_year,
        color=car.color,
        fuel_type=car.fuel_type,
        transmission=car.transmission,
        condition=car.condition,
        status=car.status,
        mileage=car.mileage,
        plate=car.plate,
        price=car.price,
        description=car.description,
        brand_id=car.brand_id,
        owner_id=car.owner_id,
    )

    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)

    # ============================
    # Carregar relações (brand e owner)
    # ============================
    result = await db.execute(
        select(Car)
        .options(selectinload(Car.brand), selectinload(Car.owner))
        .where(Car.id == db_car.id)
    )

    return result.scalar_one()


# ==============================================================================
@router.get(
    '/',
    response_model=CarListPublicSchema,
    summary='Listar todos os carros',
    description='Lista todos os carros do sistema, independentemente do status.',
)
async def list_all_cars(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[CarStatus] = Query(None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    query = select(Car).options(selectinload(Car.brand), selectinload(Car.owner))

    if status:
        query = query.where(Car.status == status)

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    cars = result.scalars().all()

    return CarListPublicSchema(
        cars=cars,
        offset=offset,
        limit=limit,
        total=total,
    )


# ==============================================================================
@router.patch(
    '/{car_id}/status',
    response_model=CarPublicSchema,
    summary='Alterar status do carro',
)
async def change_car_status(
    car_id: int,
    status: CarStatus,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    car = await db.get(Car, car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Carro não encontrado.',
        )

    car.status = status
    await db.commit()
    await db.refresh(car)

    return car


# ==============================================================================
@router.patch(
    '/{car_id}/deactivate',
    response_model=CarPublicSchema,
    summary='Desativar anúncio',
)
async def deactivate_car(
    car_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    car = await db.get(Car, car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Carro não encontrado.',
        )

    car.status = CarStatus.UNAVAILABLE
    await db.commit()
    await db.refresh(car)

    return car


# ==============================================================================
@router.delete(
    '/{car_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Remover carro',
)
async def delete_car_admin(
    car_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    car = await db.get(Car, car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Carro não encontrado.',
        )

    await db.delete(car)
    await db.commit()
