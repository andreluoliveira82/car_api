# ======================================================================
# file: tests/conftest.py
# description: Configurações e fixtures compartilhados para testes pytest
# ======================================================================

import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from car_api.app import app
from car_api.core.database import get_db_session
from car_api.core.security import create_access_token, get_password_hash
from car_api.core.settings import settings
from car_api.models import Base
from car_api.models.cars import (
    Brand,
    Car,
)
from car_api.models.users import User, UserRole

# Configurar variáveis de ambiente para testes antes de importar o app
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///:memory:'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-testing-purposes-only'
os.environ['JWT_ALGORITHM'] = 'HS256'
os.environ['JWT_EXPIRATION_MINUTES'] = '30'
os.environ['JWT_REFRESH_EXPIRATION_DAYS'] = '1'
os.environ['MIN_FACTORY_YEAR'] = '1990'
os.environ['MAX_FUTURE_YEAR'] = '2'
os.environ['MAX_PRICE'] = '1000000'
os.environ['MAX_MILEAGE'] = '1000000'
os.environ['MAX_BRAND_DESCRIPTION'] = '500'


@pytest_asyncio.fixture(scope='function')
async def session():
    """
    Cria um banco de dados SQLite em memória para testes.

    Este fixture:
    1. Inicializa um engine assíncrono com banco em memória
    2. Cria todas as tabelas definidas nos models
    3. Yielda uma sessão AsyncSession para uso nos testes
    4. Limpa o banco (drop das tabelas) após o teste

    Returns:
        AsyncSession: Sessão de banco de dados assíncrona para testes

    Yields:
        AsyncSession: Sessão configurada com expire_on_commit=False
    """
    engine = create_async_engine(
        url='sqlite+aiosqlite:///:memory:',
        echo=False,  # Set True para debug de SQL
    )

    # Cria as tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Yielda a sessão para o teste
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    # Dropa as tabelas após o teste
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Dispose do engine para evitar warnings
    await engine.dispose()


@pytest.fixture
def client(session):
    """
    Cria um cliente de teste HTTP com injeção de dependência de banco mockado.

    Este fixture configura um TestClient do FastAPI que substitui a dependência
    get_db_session por uma que retorna a sessão em memória criada pelo fixture
    `session`. Isso permite que os testes rodem isolados sem tocar no banco real.

    Args:
        session: Fixture de sessão de banco em memória

    Returns:
        TestClient: Cliente HTTP configurado para testes de integração

    Yields:
        TestClient: Cliente com dependências override ativas

    Example:
        def test_create_user(client):
            response = client.post("/api/v1/users", json={...})
            assert response.status_code == 201
    """

    def get_session_override():
        """Override da dependência get_db_session para retornar a sessão de teste."""
        return session

    # Configura o override de dependências
    with TestClient(app) as test_client:
        app.dependency_overrides[get_db_session] = get_session_override
        yield test_client

    # Limpa os overrides após o teste
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_data():
    """
    Dados de usuário fake para testes
    """
    return {
        'username': 'testuser',
        'full_name': 'User Test Fullname',
        'email': 'testuser@carapi.com',
        'password': 'TestPassword123',
    }


@pytest_asyncio.fixture
async def user(session, user_data):
    """
    Cria um usuário padrão para testes.
    """
    hashed_password = get_password_hash(user_data['password'])
    db_user = User(
        username=user_data['username'],
        full_name=user_data['full_name'],
        email=user_data['email'],
        password=hashed_password,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@pytest_asyncio.fixture
async def admin_user(session):
    """
    Cria um usuário administrador para testes.
    """
    hashed_password = get_password_hash('AdminPass123!')
    db_admin = User(
        username='adminuser',
        full_name='Admin User',
        email='admin@carapi.com',
        password=hashed_password,
        role=UserRole.ADMIN,
        is_active=True,
    )
    session.add(db_admin)
    await session.commit()
    await session.refresh(db_admin)

    return db_admin


@pytest_asyncio.fixture
async def second_user(session):
    """
    Cria um segundo usuário para testes de permissão.
    """
    hashed_password = get_password_hash('SecondPassword123!')
    db_user = User(
        username='seconduser',
        full_name='Second User',
        email='second@carapi.com',
        password=hashed_password,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@pytest_asyncio.fixture
async def brand_data():
    """
    Dados de marca para testes.
    """
    return {
        'name': 'Toyota',
        'description': 'Marca japonesa de carros confiáveis.',
    }


@pytest_asyncio.fixture
async def brand(session, brand_data):
    """
    Cria uma marca padrão para testes.
    """
    db_brand = Brand(
        name=brand_data['name'],
        description=brand_data['description'],
        is_active=True,
    )
    session.add(db_brand)
    await session.commit()
    await session.refresh(db_brand)

    return db_brand


@pytest_asyncio.fixture
async def second_brand(session):
    """
    Cria uma segunda marca para testes.
    """
    db_brand = Brand(
        name='Honda',
        description='Marca japonesa de automóveis.',
        is_active=True,
    )
    session.add(db_brand)
    await session.commit()
    await session.refresh(db_brand)

    return db_brand


@pytest_asyncio.fixture
def car_data():
    """
    Dados de carro para testes.
    Nota: Este fixture retorna apenas os dados, sem depender de brand.
    Os testes devem setar brand_id conforme necessário.
    """
    return {
        'car_type': 'suv',
        'model': 'Corolla Cross',
        'factory_year': 2024,
        'model_year': 2025,
        'color': 'white',
        'fuel_type': 'flex',
        'transmission': 'automatic',
        'condition': 'new',
        'status': 'available',
        'mileage': 0,
        'plate': 'ABC1D23',
        'price': 150000.00,
        'description': 'Carro zero km, muito confortável.',
        'brand_id': 1,  # Será atualizado nos testes
    }


@pytest_asyncio.fixture
async def car(session, car_data, user, brand):
    """
    Cria um carro padrão para testes.
    """
    db_car = Car(
        car_type=car_data['car_type'],
        model=car_data['model'],
        factory_year=car_data['factory_year'],
        model_year=car_data['model_year'],
        color=car_data['color'],
        fuel_type=car_data['fuel_type'],
        transmission=car_data['transmission'],
        condition=car_data['condition'],
        status=car_data['status'],
        mileage=car_data['mileage'],
        plate=car_data['plate'],
        price=car_data['price'],
        description=car_data['description'],
        brand_id=brand.id,
        owner_id=user.id,
    )
    session.add(db_car)
    await session.commit()
    await session.refresh(db_car)

    return db_car


@pytest_asyncio.fixture
async def second_car(session, brand, second_user):
    """
    Cria um segundo carro para testes.
    """
    db_car = Car(
        car_type='sedan',
        model='Civic',
        factory_year=2023,
        model_year=2024,
        color='silver',
        fuel_type='gasoline',
        transmission='automatic',
        condition='used',
        status='available',
        mileage=15000,
        plate='XYZ9A87',
        price=120000.00,
        description='Carro em ótimo estado.',
        brand_id=brand.id,
        owner_id=second_user.id,
    )
    session.add(db_car)
    await session.commit()
    await session.refresh(db_car)

    return db_car


@pytest_asyncio.fixture
async def inactive_user(session):
    """
    Cria um usuário inativo para testes.
    """
    hashed_password = get_password_hash('InactivePassword123!')
    db_user = User(
        username='inactiveuser',
        full_name='Inactive User',
        email='inactive@carapi.com',
        password=hashed_password,
        is_active=False,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@pytest_asyncio.fixture
async def inactive_brand(session):
    """
    Cria uma marca inativa para testes.
    """
    db_brand = Brand(
        name='Inactive Brand',
        description='Marca desativada.',
        is_active=False,
    )
    session.add(db_brand)
    await session.commit()
    await session.refresh(db_brand)

    return db_brand


@pytest_asyncio.fixture
def auth_headers(client, user):
    """
    Gera headers de autenticação para um usuário.
    """
    token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
    )
    return {'Authorization': f'Bearer {token}'}


@pytest_asyncio.fixture
def admin_auth_headers(client, admin_user):
    """
    Gera headers de autenticação para um administrador.
    """
    token = create_access_token(
        subject=str(admin_user.id),
        role=admin_user.role.value,
    )
    return {'Authorization': f'Bearer {token}'}


@pytest_asyncio.fixture
def invalid_auth_headers():
    """
    Headers com token inválido.
    """
    return {'Authorization': 'Bearer invalid_token_here'}


@pytest_asyncio.fixture
def expired_auth_headers():
    """
    Headers com token expirado (simulado).
    """
    # Criar token já expirado
    payload = {
        'sub': '1',
        'role': 'user',
        'exp': datetime.now(timezone.utc) - timedelta(minutes=1),
        'iat': datetime.now(timezone.utc) - timedelta(minutes=61),
        'type': 'access',
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return {'Authorization': f'Bearer {token}'}
