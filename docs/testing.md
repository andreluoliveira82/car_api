# Testes

Este documento descreve a estratégia de testes do **Car API**, incluindo tipos de testes esperados, estrutura e boas práticas.

---

## Visão Geral

A estratégia de testes do projeto segue a **pirâmide de testes**, priorizando testes unitários e de integração, com uma camada menor de testes end-to-end (E2E).

```
        /\
       /  \      E2E (poucos)
      /----\
     /      \    Integração
    /--------\
   /          \  Unitários (muitos)
  /------------\
```

---

## Tipos de Testes

### Testes Unitários

**Propósito:** Validar unidades isoladas de código (funções, validators, schemas).

**O que testar:**

- Validators de negócio (`validators/`)
- Schemas Pydantic (validações de campo)
- Funções utilitárias (`core/security.py`)
- Models SQLAlchemy (relacionamentos)

**Exemplo esperado:**

```python
# tests/test_validators/test_users.py
def test_validate_password_success():
    assert validate_password("Senha123") == "Senha123"

def test_validate_password_too_short():
    with pytest.raises(ValueError, match="pelo menos 6 caracteres"):
        validate_password("Ab1")

def test_validate_password_no_number():
    with pytest.raises(ValueError, match="pelo menos um número"):
        validate_password("SenhaApenas")
```

---

### Testes de Integração

**Propósito:** Validar a integração entre componentes (routers + database).

**O que testar:**

- Endpoints da API (CRUD completo)
- Autenticação e autorização
- Relacionamentos entre models
- Migrações de banco de dados

**Exemplo esperado:**

```python
# tests/test_cars.py
@pytest.mark.asyncio
async def test_create_car_success(client, auth_token, test_brand):
    response = await client.post(
        "/api/v1/cars/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "car_type": "suv",
            "model": "Corolla Cross",
            "factory_year": 2025,
            "model_year": 2026,
            "color": "white",
            "fuel_type": "flex",
            "transmission": "automatic",
            "condition": "new",
            "mileage": 0,
            "plate": "ABC0D12",
            "price": 105999.99,
            "brand_id": test_brand.id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["model"] == "Corolla Cross"
```

---

### Testes End-to-End (E2E)

**Propósito:** Validar fluxos completos do sistema.

**O que testar:**

- Fluxo de autenticação completo (login → uso → refresh → logout)
- Fluxo de CRUD completo (criar → listar → atualizar → excluir)
- Cenários de erro complexos

**Exemplo esperado:**

```python
# tests/test_e2e/test_car_workflow.py
@pytest.mark.asyncio
async def test_full_car_workflow(client):
    # 1. Registrar usuário
    # 2. Fazer login
    # 3. Criar carro
    # 4. Listar carros
    # 5. Atualizar carro
    # 6. Excluir carro
    # 7. Verificar exclusão
```

---

## Estrutura de Testes

### Diretório de Testes

```
tests/
├── conftest.py                    # Fixtures compartilhadas
├── test_validators/
│   ├── test_users.py              # Tests para validators de usuário
│   └── test_cars.py               # Tests para validators de carro
├── test_schemas/
│   ├── test_users.py              # Tests para schemas de usuário
│   └── test_cars.py               # Tests para schemas de carro
├── test_routers/
│   ├── test_auth.py               # Tests para autenticação
│   ├── test_users.py              # Tests para rotas de usuário
│   ├── test_cars.py               # Tests para rotas de carro
│   └── test_brands.py             # Tests para rotas de marca
├── test_admin/
│   ├── test_users.py              # Tests para admin de usuários
│   ├── test_cars.py               # Tests para admin de carros
│   └── test_brands.py             # Tests para admin de marcas
└── test_e2e/
    └── test_workflows.py          # Tests de fluxos completos
```

---

## Fixtures (conftest.py)

### Fixtures Esperadas

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from car_api.app import app
from car_api.core.database import get_db_session
from car_api.models.base import Base


@pytest.fixture(scope="session")
def event_loop():
    """Criar loop de eventos para testes async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Criar engine de teste em memória."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Criar sessão de teste."""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_session):
    """Criar cliente de teste com dependência de DB sobrescrita."""
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_session):
    """Criar usuário de teste."""
    from car_api.models.users import User
    from car_api.core.security import get_password_hash
    
    user = User(
        username="testuser",
        full_name="Test User",
        email="test@example.com",
        password=get_password_hash("Senha123"),
        role=UserRole.USER,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def test_admin(test_session):
    """Criar admin de teste."""
    from car_api.models.users import User
    from car_api.core.security import get_password_hash
    
    admin = User(
        username="admin",
        full_name="Admin User",
        email="admin@example.com",
        password=get_password_hash("Senha123"),
        role=UserRole.ADMIN,
    )
    test_session.add(admin)
    await test_session.commit()
    await test_session.refresh(admin)
    return admin


@pytest.fixture
async def auth_token(client, test_user):
    """Obter token de autenticação para usuário de teste."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Senha123"},
    )
    return response.json()["access_token"]


@pytest.fixture
async def admin_token(client, test_admin):
    """Obter token de autenticação para admin."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Senha123"},
    )
    return response.json()["access_token"]


@pytest.fixture
async def test_brand(test_session):
    """Criar marca de teste."""
    from car_api.models.cars import Brand
    
    brand = Brand(name="Toyota", description="Japanese brand", is_active=True)
    test_session.add(brand)
    await test_session.commit()
    await test_session.refresh(brand)
    return brand


@pytest.fixture
async def test_car(test_session, test_user, test_brand):
    """Criar carro de teste."""
    from car_api.models.cars import Car, CarType, CarColor, FuelType, CarCondition
    
    car = Car(
        car_type=CarType.SEDAN,
        model="Corolla",
        factory_year=2020,
        model_year=2021,
        color=CarColor.SILVER,
        fuel_type=FuelType.FLEX,
        transmission="automatic",
        condition=CarCondition.USED,
        mileage=15000,
        plate="ABC1D23",
        price=85000.00,
        brand_id=test_brand.id,
        owner_id=test_user.id,
    )
    test_session.add(car)
    await test_session.commit()
    await test_session.refresh(car)
    return car
```

---

## Boas Práticas

### Nomenclatura

```python
def test_<unidade>_<cenário>_<resultado_esperado>():
    ...

# Exemplos
def test_validate_password_success():
def test_validate_password_too_short_raises_error():
def test_create_car_unauthorized_returns_401():
def test_update_car_owner_mismatch_returns_403():
```

### Isolamento

- Cada teste deve ser independente
- Usar banco de dados em memória (`:memory:`)
- Limpar estado entre testes (fixtures com `scope="function"`)

### Cobertura

- Testar caminhos felizes (success)
- Testar caminhos de erro (exceptions, validações)
- Testar casos de borda (valores mínimos/máximos)

### Async

- Usar `@pytest.mark.asyncio` para testes async
- Usar `await` para chamadas de API e banco de dados

---

## Execução de Testes

### Comandos

```bash
# Rodar todos os testes
pytest

# Rodar com verbose
pytest -v

# Rodar com cobertura
pytest --cov=car_api --cov-report=html

# Rodar testes específicos
pytest tests/test_validators/
pytest tests/test_routers/test_cars.py

# Rodar teste específico
pytest tests/test_validators/test_users.py::test_validate_password_success

# Rodar apenas testes marcados
pytest -m asyncio
```

### Configuração do pytest

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

---

## Matriz de Testes por Módulo

| Módulo | Unitários | Integração | E2E |
|--------|-----------|------------|-----|
| `validators/users.py` | ✅ | - | - |
| `validators/cars.py` | ✅ | - | - |
| `schemas/*.py` | ✅ | - | - |
| `core/security.py` | ✅ | - | - |
| `routers/auth.py` | - | ✅ | ✅ |
| `routers/users.py` | - | ✅ | ✅ |
| `routers/cars.py` | - | ✅ | ✅ |
| `routers/brands.py` | - | ✅ | - |
| `routers/admin/*.py` | - | ✅ | ✅ |
| `models/*.py` | ✅ | ✅ | - |

---

## Status Atual

> **Nota:** A suíte de testes está em fase de implementação.

### Implementado

- [ ] Fixtures básicas em `conftest.py`
- [ ] Tests de validators
- [ ] Tests de schemas
- [ ] Tests de autenticação
- [ ] Tests de CRUD de carros
- [ ] Tests de controle de acesso

### Planejado

- [ ] Tests de admin routes
- [ ] Tests de migrações
- [ ] Tests de performance
- [ ] Tests de carga (stress testing)
- [ ] CI/CD integration (GitHub Actions)

---

## Cobertura de Testes

### Meta de Cobertura

| Tipo | Meta |
|------|------|
| Lines | 80% |
| Functions | 85% |
| Classes | 90% |

### Gerar Relatório

```bash
# HTML report
pytest --cov=car_api --cov-report=html
# Abrir: htmlcov/index.html

# Terminal report
pytest --cov=car_api --cov-report=term-missing
```

---

## Debug de Testes

### Verbose

```bash
pytest -v -s
```

### Print em testes

```bash
pytest -s  # Mostra prints
```

### Debug de falhas

```bash
pytest --tb=long  # Traceback completo
pytest --pdb      # Drop para pdb no erro
```

---

## Próximo Passo

Consulte [Deploy](deployment.md) para informações sobre implantação em produção.
