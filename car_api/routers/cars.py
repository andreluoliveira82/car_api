# ===============================================================================================
# File: car_api/routers/cars.py
# Description: FastAPI router for handling car cars-related endpoints in the Car API.
# ===============================================================================================

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from car_api.core.database import get_db_session
from car_api.core.security import get_current_user, verify_car_ownership
from car_api.models.cars import (
    Brand,
    Car,
    CarColor,
    CarCondition,
    CarStatus,
    CarType,
    FuelType,
    TransmissionType,
)
from car_api.models.users import User
from car_api.schemas.cars import (
    CarListPublicSchema,
    CarPublicSchema,
    CarSchema,
    CarUpdateSchema,
)
from car_api.validators.cars import validate_car_model_year

router = APIRouter(prefix='/cars', tags=['cars'])


# ===============================================================================================
@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=CarPublicSchema,
    summary='Criar um novo carro.',
    description='Endpoint para criar um novo carro no sistema.',
)
async def create_car(
    car: CarSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> CarPublicSchema:
    """
    Create a new car in the database.
    """

    # ============================
    # Validar se a marca existe
    # ============================
    brand_exists = await db.scalar(select(exists().where(Brand.id == car.brand_id)))
    if not brand_exists:
        raise HTTPException(status_code=400, detail='A marca informada não existe.')

    # ============================
    # Validar se o proprietário existe
    # ============================
    owner_exists = await db.scalar(select(exists().where(User.id == car.owner_id)))
    if not owner_exists:
        raise HTTPException(status_code=400, detail='O proprietário informado não existe.')

    # ============================
    # Validar placa duplicada
    # ============================
    plate_exists = await db.scalar(select(exists().where(Car.plate == car.plate)))
    if plate_exists:
        raise HTTPException(
            status_code=400, detail='Já existe um carro cadastrado com esta placa.'
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
        plate=car.plate,
        fuel_type=car.fuel_type,
        transmission=car.transmission,
        condition=car.condition,
        status=car.status,
        mileage=car.mileage,
        price=car.price,
        description=car.description,
        brand_id=car.brand_id,
        owner_id=current_user.id,
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


# ===============================================================================================
@router.get(
    path='/{car_id}',
    status_code=status.HTTP_200_OK,
    response_model=CarPublicSchema,
    summary='Obter detalhes de um carro pelo ID.',
    description='Retorna os detalhes completos de um carro, incluindo marca e proprietário.',
)
async def get_car_by_id(
    car_id: int,
    # current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> CarPublicSchema:
    """
    Retrieve a car by its ID, including brand and owner relationships.
    """

    result = await db.execute(
        select(Car)
        .options(selectinload(Car.brand), selectinload(Car.owner))
        .where(Car.id == car_id)
    )

    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Carro com ID {car_id} não encontrado.',
        )

    return car


# ===============================================================================================
@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=CarListPublicSchema,
    summary='Listar carros com paginação e filtros opcionais.',
    description=(
        'Retorna uma lista paginada de carros. '
        'Permite filtrar por tipo, cor, ano, preço, marca, status e outros atributos.'
    ),
)
async def list_cars(
    # Paginação
    offset: int = Query(0, ge=0, examples=0),
    limit: int = Query(10, ge=1, le=100, examples=10),
    # Filtros opcionais
    search: Optional[str] = Query(None, description='Pesquisa pelo modelo, cor ou placa'),
    car_type: Optional[CarType] = Query(None, examples='suv'),
    color: Optional[CarColor] = Query(None, examples='white'),
    fuel_type: Optional[FuelType] = Query(None, examples='flex'),
    transmission: Optional[TransmissionType] = Query(None, examples='automatic'),
    condition: Optional[CarCondition] = Query(None, examples='used'),
    status: Optional[CarStatus] = Query(None, examples='available'),
    brand_id: Optional[int] = Query(None, examples=1),
    owner_id: Optional[int] = Query(None, examples=3),
    min_year: Optional[int] = Query(None, examples=2015),
    max_year: Optional[int] = Query(None, examples=2026),
    min_price: Optional[Decimal] = Query(None, examples=50000),
    max_price: Optional[Decimal] = Query(None, examples=200000),
    # current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    List cars with optional filters and pagination.
    """

    # ============================
    # Construir query base
    # ============================
    query = select(Car).options(selectinload(Car.brand), selectinload(Car.owner))

    # ============================
    # Aplicar filtros opcionais
    # ============================
    if search:
        search_term = f'%{search}%'
        query = query.where(
            (Car.model.ilike(search_term))
            | (Car.color.ilike(search_term))
            | (Car.plate.ilike(search_term))
        )

    if car_type:
        query = query.where(Car.car_type == car_type)

    if color:
        query = query.where(Car.color == color)

    if fuel_type:
        query = query.where(Car.fuel_type == fuel_type)

    if transmission:
        query = query.where(Car.transmission == transmission)

    if condition:
        query = query.where(Car.condition == condition)

    if status:
        query = query.where(Car.status == status)

    if brand_id:
        query = query.where(Car.brand_id == brand_id)

    if owner_id:
        query = query.where(Car.owner_id == owner_id)

    if min_year:
        query = query.where(Car.model_year >= min_year)

    if max_year:
        query = query.where(Car.model_year <= max_year)

    if min_price:
        query = query.where(Car.price >= min_price)

    if max_price:
        query = query.where(Car.price <= max_price)

    # ============================
    # Contar total antes da paginação
    # ============================
    total = await db.scalar(select(func.count()).select_from(query.subquery()))

    # ============================
    # Aplicar paginação
    # ============================
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    cars = result.scalars().all()

    # ============================
    # Retornar resposta paginada
    # ============================
    return CarListPublicSchema(cars=cars, offset=offset, limit=limit, total=total)


# ===============================================================================================
@router.put(
    path='/{car_id}',
    status_code=status.HTTP_200_OK,
    response_model=CarPublicSchema,
    summary='Atualizar um carro pelo ID.',
    description='Atualiza parcialmente os dados de um carro existente.',
)
async def update_car(
    car_id: int,
    car_data: CarUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> CarPublicSchema:
    """
    Update an existing car by ID.
    """

    # ============================
    # Verificar se o carro existe
    # ============================
    result = await db.execute(
        select(Car)
        .options(selectinload(Car.brand), selectinload(Car.owner))
        .where(Car.id == car_id)
    )
    db_car = result.scalar_one_or_none()

    if not db_car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Carro com ID {car_id} não encontrado.',
        )

    # ============================
    # Validar se o usuário logado é o dono do carro
    # =============================
    verify_car_ownership(current_user, db_car.owner_id)

    # ============================
    # Validar placa duplicada
    # ============================
    if car_data.plate and car_data.plate != db_car.plate:
        plate_exists = await db.scalar(
            select(func.count()).where(Car.plate == car_data.plate)
        )
        if plate_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Já existe um carro cadastrado com esta placa.',
            )

    # ============================
    # Validar marca (se enviada)
    # ============================
    if car_data.brand_id:
        brand_exists = await db.scalar(
            select(func.count()).where(Car.brand_id == car_data.brand_id)
        )
        if not brand_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='A marca informada não existe.',
            )

    # ============================
    # Validar proprietário (se enviado)
    # ============================
    if car_data.owner_id:
        owner_exists = await db.scalar(
            select(func.count()).where(Car.owner_id == car_data.owner_id)
        )
        if not owner_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='O proprietário informado não existe.',
            )

    # ============================
    # Aplicar atualizações campo a campo
    # ============================
    update_fields = car_data.model_dump(exclude_unset=True)

    for field, value in update_fields.items():
        setattr(db_car, field, value)

    # ============================
    # Validar anos (factory/model)
    # ============================
    if ('factory_year' in update_fields) or ('model_year' in update_fields):
        validate_car_model_year(db_car.model_year, db_car.factory_year)

    # ============================
    # Salvar alterações
    # ============================
    await db.commit()
    await db.refresh(db_car)

    return db_car


# ===============================================================================================
@router.delete(
    path='/{car_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Excluir um carro pelo ID.',
    description='Remove um carro existente do sistema.',
)
async def delete_car(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete a car by its ID.
    """

    # ============================
    # Verificar se o carro existe
    # ============================
    result = await db.execute(select(Car).where(Car.id == car_id))
    db_car = result.scalar_one_or_none()

    if not db_car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Carro com ID {car_id} não encontrado.',
        )

    # ============================
    # Validar se o usuário logado é o dono do carro
    # =============================
    verify_car_ownership(current_user, db_car.owner_id)

    # ============================
    # Remover o carro
    # ============================
    await db.delete(db_car)
    await db.commit()

    # ============================
    # Retorno 204 (sem conteúdo)
    # ============================
