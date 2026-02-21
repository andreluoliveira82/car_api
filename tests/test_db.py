# ======================================================================
# file: tests/test_db.py
# description: Testes de conexão e consistência do banco de dados
# ======================================================================

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from car_api.models import Base, Brand, Car, User


@pytest.mark.asyncio
async def test_database_connection(session):
    """
    Testa se a conexão com o banco de dados está funcionando.
    """
    # Executa uma query simples para verificar conexão
    result = await session.execute(text('SELECT 1'))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_tables_created(session):
    """
    Verifica se todas as tabelas foram criadas corretamente.
    """
    # Verifica se as tabelas existem no metadata
    assert 'users' in Base.metadata.tables
    assert 'brands' in Base.metadata.tables
    assert 'cars' in Base.metadata.tables


@pytest.mark.asyncio
async def test_users_table_exists(session):
    """
    Verifica se a tabela de usuários existe e pode ser consultada.
    """
    result = await session.execute(select(User))
    users = result.scalars().all()
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_brands_table_exists(session):
    """
    Verifica se a tabela de marcas existe e pode ser consultada.
    """
    result = await session.execute(select(Brand))
    brands = result.scalars().all()
    assert isinstance(brands, list)


@pytest.mark.asyncio
async def test_cars_table_exists(session):
    """
    Verifica se a tabela de carros existe e pode ser consultada.
    """
    result = await session.execute(select(Car))
    cars = result.scalars().all()
    assert isinstance(cars, list)


@pytest.mark.asyncio
async def test_insert_and_retrieve_user(session):
    """
    Testa inserção e recuperação de um usuário.
    """
    user = User(
        username='db_test_user',
        full_name='DB Test User',
        email='db_test@carapi.com',
        password='hashed_password_here',
    )
    session.add(user)
    await session.commit()

    # Recupera o usuário
    result = await session.execute(select(User).where(User.email == 'db_test@carapi.com'))
    retrieved_user = result.scalar_one_or_none()

    assert retrieved_user is not None
    assert retrieved_user.username == 'db_test_user'
    assert retrieved_user.email == 'db_test@carapi.com'


@pytest.mark.asyncio
async def test_insert_and_retrieve_brand(session):
    """
    Testa inserção e recuperação de uma marca.
    """
    brand = Brand(
        name='Test Brand',
        description='Marca de teste para DB',
        is_active=True,
    )
    session.add(brand)
    await session.commit()

    # Recupera a marca
    result = await session.execute(select(Brand).where(Brand.name == 'Test Brand'))
    retrieved_brand = result.scalar_one_or_none()

    assert retrieved_brand is not None
    assert retrieved_brand.name == 'Test Brand'
    assert retrieved_brand.is_active is True


@pytest.mark.asyncio
async def test_insert_and_retrieve_car(session):
    """
    Testa inserção e recuperação de um carro.
    """
    # Cria marca e usuário primeiro
    brand = Brand(name='Test Brand', description='Test', is_active=True)
    session.add(brand)
    await session.commit()

    user = User(
        username='db_car_user',
        full_name='DB Car User',
        email='db_car@carapi.com',
        password='hashed_password',
    )
    session.add(user)
    await session.commit()

    car = Car(
        car_type='hatch',
        model='Test Car',
        factory_year=2024,
        model_year=2025,
        color='black',
        fuel_type='flex',
        transmission='manual',
        condition='new',
        status='available',
        mileage=0,
        plate='TST1A23',
        price=50000.00,
        description='Carro de teste',
        brand_id=brand.id,
        owner_id=user.id,
    )
    session.add(car)
    await session.commit()

    # Recupera o carro
    result = await session.execute(select(Car).where(Car.plate == 'TST1A23'))
    retrieved_car = result.scalar_one_or_none()

    assert retrieved_car is not None
    assert retrieved_car.model == 'Test Car'
    assert retrieved_car.brand_id == brand.id
    assert retrieved_car.owner_id == user.id


@pytest.mark.asyncio
async def test_user_relationships(session):
    """
    Testa relacionamentos entre User e Car.
    """
    # Cria marca
    brand = Brand(name='Relation Brand', description='Test', is_active=True)
    session.add(brand)
    await session.commit()

    # Cria usuário
    user = User(
        username='relation_user',
        full_name='Relation User',
        email='relation@carapi.com',
        password='hashed_password',
    )
    session.add(user)
    await session.commit()

    # Cria um carro para o usuário
    car = Car(
        car_type='sedan',
        model='Relation Test Car',
        factory_year=2023,
        model_year=2024,
        color='white',
        fuel_type='gasoline',
        transmission='automatic',
        condition='used',
        status='available',
        mileage=10000,
        plate='REL2B34',
        price=80000.00,
        description='Carro de teste de relacionamento',
        brand_id=brand.id,
        owner_id=user.id,
    )
    session.add(car)
    await session.commit()

    # Recupera usuário com relacionamentos
    result = await session.execute(select(User).where(User.id == user.id))
    retrieved_user = result.scalar_one()

    assert len(retrieved_user.cars) == 1
    assert retrieved_user.cars[0].model == 'Relation Test Car'


@pytest.mark.asyncio
async def test_brand_cars_relationship(session):
    """
    Testa relacionamentos entre Brand e Car.
    """
    # Cria marca
    brand = Brand(name='Brand Relation Brand', description='Test', is_active=True)
    session.add(brand)
    await session.commit()

    # Cria usuário
    user = User(
        username='brand_relation_user',
        full_name='Brand Relation User',
        email='brand_relation@carapi.com',
        password='hashed_password',
    )
    session.add(user)
    await session.commit()

    # Cria um carro para a marca
    car = Car(
        car_type='suv',
        model='Brand Relation Test',
        factory_year=2024,
        model_year=2025,
        color='silver',
        fuel_type='flex',
        transmission='automatic',
        condition='new',
        status='available',
        mileage=0,
        plate='BRL3C45',
        price=120000.00,
        description='Carro de teste de marca',
        brand_id=brand.id,
        owner_id=user.id,
    )
    session.add(car)
    await session.commit()

    # Recupera marca com relacionamentos
    result = await session.execute(select(Brand).where(Brand.id == brand.id))
    retrieved_brand = result.scalar_one()

    assert len(retrieved_brand.cars) == 1
    assert retrieved_brand.cars[0].model == 'Brand Relation Test'


@pytest.mark.asyncio
async def test_rollback_on_error(session):
    """
    Testa se o rollback funciona corretamente em caso de erro.
    """
    # Tenta inserir um usuário
    user = User(
        username='rollback_user',
        full_name='Rollback Test',
        email='rollback@carapi.com',
        password='password123',
    )
    session.add(user)
    await session.rollback()

    # Verifica se o usuário não foi inserido
    result = await session.execute(select(User).where(User.username == 'rollback_user'))
    retrieved_user = result.scalar_one_or_none()

    assert retrieved_user is None


@pytest.mark.asyncio
async def test_cleanup_between_tests(session):
    """
    Testa se o cleanup funciona entre testes.
    Este teste verifica que o banco começa limpo.
    """
    # Conta usuários
    result = await session.execute(select(User))
    users = result.scalars().all()

    # O banco deve estar vazio no início de cada teste
    # (os fixtures que adicionam dados são explícitos)
    assert len(users) == 0


@pytest.mark.asyncio
async def test_user_unique_constraint(session):
    """
    Testa restrição de unicidade de username.
    """
    user1 = User(
        username='unique_user',
        full_name='Unique User 1',
        email='unique1@carapi.com',
        password='password123',
    )
    session.add(user1)
    await session.commit()

    # Tenta criar usuário com mesmo username
    user2 = User(
        username='unique_user',
        full_name='Unique User 2',
        email='unique2@carapi.com',
        password='password456',
    )
    session.add(user2)

    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.asyncio
async def test_user_email_unique_constraint(session):
    """
    Testa restrição de unicidade de email.
    """
    user1 = User(
        username='email_user1',
        full_name='Email User 1',
        email='same_email@carapi.com',
        password='password123',
    )
    session.add(user1)
    await session.commit()

    # Tenta criar usuário com mesmo email
    user2 = User(
        username='email_user2',
        full_name='Email User 2',
        email='same_email@carapi.com',
        password='password456',
    )
    session.add(user2)

    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.asyncio
async def test_car_plate_unique_constraint(session):
    """
    Testa restrição de unicidade de placa.
    """
    # Cria marca e usuário primeiro
    brand = Brand(name='Plate Brand', description='Test', is_active=True)
    session.add(brand)
    await session.commit()

    user = User(
        username='plate_user',
        full_name='Plate User',
        email='plate@carapi.com',
        password='password123',
    )
    session.add(user)
    await session.commit()

    car1 = Car(
        car_type='hatch',
        model='Plate Test 1',
        factory_year=2024,
        model_year=2025,
        color='black',
        fuel_type='flex',
        transmission='manual',
        condition='new',
        status='available',
        mileage=0,
        plate='PLT1A23',
        price=50000.00,
        description='Carro 1',
        brand_id=brand.id,
        owner_id=user.id,
    )
    session.add(car1)
    await session.commit()

    # Tenta criar carro com mesma placa
    car2 = Car(
        car_type='sedan',
        model='Plate Test 2',
        factory_year=2023,
        model_year=2024,
        color='white',
        fuel_type='gasoline',
        transmission='automatic',
        condition='used',
        status='available',
        mileage=10000,
        plate='PLT1A23',  # Mesma placa
        price=60000.00,
        description='Carro 2',
        brand_id=brand.id,
        owner_id=user.id,
    )
    session.add(car2)

    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.asyncio
async def test_brand_name_unique_constraint(session):
    """
    Testa restrição de unicidade de nome da marca.
    """
    brand1 = Brand(
        name='Unique Brand',
        description='Brand 1',
        is_active=True,
    )
    session.add(brand1)
    await session.commit()

    # Tenta criar marca com mesmo nome
    brand2 = Brand(
        name='Unique Brand',
        description='Brand 2',
        is_active=True,
    )
    session.add(brand2)

    with pytest.raises(IntegrityError):
        await session.commit()
