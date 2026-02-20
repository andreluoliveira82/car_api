# Guidelines e Padrões

Este documento descreve os padrões de código, convenções de nomenclatura e práticas adotadas no **Car API**.

---

## Padrões de Código

### Estilo e Formatação

O projeto utiliza **Ruff** como linter e formatador único, substituindo ferramentas como Flake8, Black e isort.

**Configuração principal:**

```toml
[tool.ruff]
line-length = 92
quote-style = 'single'
```

**Regras de linting:**

- `I`: Ordenação de imports (isort)
- `F`: Pyflakes (erros de sintaxe e nomes não definidos)
- `E`, `W`: Pycodestyle (PEP 8)
- `PL`: Pylint (complexidade, boas práticas)
- `PT`: pytest style

**Regras ignoradas (decisões conscientes):**

| Regra | Motivo |
|-------|--------|
| `E501` | Docstrings e comentários longos são aceitáveis |
| `PLR2004` | Números mágicos são comuns em configurações e validações |
| `PLR0917` | Muitos argumentos em funções de serviço são aceitáveis |
| `PLR0913` | Muitos parâmetros em endpoints são necessários para filtros |
| `PLR0912` | Muitas branches em endpoints complexos são inevitáveis |

### Execução

```bash
# Lint
poetry run task lint

# Format (com auto-fix prévio)
poetry run task format
```

---

## Convenções de Nomenclatura

### Arquivos e Diretórios

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Módulos Python | `snake_case.py` | `database.py`, `user_service.py` |
| Pacotes | `snake_case` | `car_api`, `core`, `routers` |
| Arquivos de teste | `test_*.py` ou `*_test.py` | `test_users.py` |
| Migrações | `*_revision.py` | `001_create_users_table.py` |

### Classes e Tipos

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Classes | `PascalCase` | `User`, `CarSchema`, `BaseModel` |
| Enums | `PascalCase` | `UserRole`, `CarStatus`, `CarType` |
| Exceções | `PascalCase` com sufixo `Error` ou `Exception` | `AuthenticationError` |

### Variáveis e Funções

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Variáveis locais | `snake_case` | `user_id`, `db_session` |
| Funções | `snake_case` | `get_user_by_id`, `create_access_token` |
| Constantes | `UPPER_SNAKE_CASE` | `JWT_SECRET_KEY`, `MAX_PRICE` |
| Parâmetros de endpoint | `snake_case` | `car_id`, `offset`, `limit` |

### Banco de Dados

| Elemento | Convenção | Exemplo |
|----------|-----------|---------|
| Tabelas | `snake_case` plural | `users`, `cars`, `brands` |
| Colunas | `snake_case` | `created_at`, `owner_id` |
| Chaves estrangeiras | `tabela_id` | `user_id`, `brand_id` |

---

## Organização de Código

### Estrutura de Arquivos

Cada módulo segue a estrutura:

```python
# ==============================================================================
# File: car_api/core/security.py
# Description: Descrição do propósito do arquivo.
# ==============================================================================

# Imports padrão
from datetime import datetime

# Imports de terceiros
import jwt
from fastapi import Depends

# Imports locais
from car_api.core.settings import settings

# Constantes
JWT_ALGORITHM = 'HS256'

# Classes e funções
def create_access_token(...):
    ...
```

**Ordem de imports:**

1. Biblioteca padrão Python
2. Bibliotecas de terceiros
3. Imports locais do projeto

**Cabeçalho do arquivo:**

- Comentário em bloco com nome do arquivo e descrição
- Separador de seções com `# ===`

### Docstrings

**Funções e métodos:**

```python
def authenticate_user(
    email: str,
    password: str,
    db: AsyncSession,
) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Args:
        email: User's email address
        password: Plain text password
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
```

**Classes:**

```python
class User(Base):
    """
    SQLAlchemy model representing a user in the Car API.
    
    This model stores authentication, authorization and profile data.
    """
```

**Endpoints FastAPI:**

Utilizam parâmetros do decorador `@router` para documentação:

```python
@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    summary='Criar um novo usuário',
    description='Permite que visitantes se cadastrem no sistema.',
)
```

---

## Organização de Rotas

### Separação por Responsabilidade

| Diretório | Propósito | Prefixo |
|-----------|-----------|---------|
| `routers/` | Rotas públicas e autenticadas | `/api/v1` |
| `routers/admin/` | Rotas administrativas | `/api/v1/admin` |

### Tags no Swagger

Cada router define uma `tag` para agrupamento no Swagger UI:

```python
router = APIRouter(prefix='/users', tags=['users'])
router = APIRouter(prefix='/admin/users', tags=['admin - users'])
```

### Padrão de Endpoints

| Método | Path | Propósito |
|--------|------|-----------|
| `POST /` | Criação |
| `GET /{id}` | Obter por ID |
| `GET /` | Listar com filtros |
| `PUT /{id}` | Atualização completa |
| `PATCH /{id}/...` | Atualização parcial específica |
| `DELETE /{id}` | Remoção |

---

## Organização de Schemas

### Nomenclatura de Schemas

| Sufixo | Propósito | Exemplo |
|--------|-----------|---------|
| `Base` | Atributos compartilhados | `UserBase` |
| `Create` | Criação (input) | `UserCreate`, `CarSchema` |
| `Update` | Atualização (input, campos opcionais) | `UserUpdate`, `CarUpdateSchema` |
| `PublicSchema` | Resposta pública (output) | `UserPublicSchema`, `CarPublicSchema` |
| `ListPublicSchema` | Resposta paginada | `CarListPublicSchema` |

### Validações com Pydantic

**Field validators:**

```python
class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def validate_password_field(cls, value):
        return validate_password(value)
```

**Model validators (pós-validação):**

```python
class CarSchema(BaseModel):
    factory_year: int
    model_year: int

    @model_validator(mode='after')
    def validate_years(self):
        validate_car_model_year(self.model_year, self.factory_year)
        return self
```

---

## Organização de Models

### SQLAlchemy Models

Todos os models herdam de `Base` e seguem:

```python
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    # Timestamps automáticos
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now(),
    )
    
    # Relacionamentos
    cars: Mapped[List['Car']] = relationship(
        'Car',
        back_populates='owner',
        lazy='selectin',
    )
```

### Enums

Enums herdam de `str, Enum` para serialização automática:

```python
class UserRole(str, Enum):
    USER = 'user'
    ADMIN = 'admin'
```

---

## Validações de Negócio

### Local e Propósito

Validações de negócio estão em `car_api/validators/`, separadas por domínio:

- `validators/users.py`: Validações de usuário (senha, username, email)
- `validators/cars.py`: Validações de carro (placa, ano, preço)

### Padrão de Implementação

```python
def validate_password(value: str) -> str:
    value = value.strip()

    match value:
        case '':
            raise ValueError('A senha não pode estar vazia.')
        case _ if len(value) < 6:
            raise ValueError('A senha deve ter pelo menos 6 caracteres.')

    if not any(char.isdigit() for char in value):
        raise ValueError('A senha deve conter pelo menos um número.')

    return value
```

**Características:**

- Funções puras (sem efeitos colaterais)
- Lançam `ValueError` com mensagens em português
- Retornam o valor normalizado (strip, upper, etc.)

---

## Segurança

### Senhas

- Hash com **Argon2** (via `pwdlib`)
- Validação de força mínima (6-15 caracteres, letras e números)

### Tokens JWT

- Assinatura com **HS256**
- Access token: 30 minutos
- Refresh token: 1 dia
- Validação de tipo (`access` vs `refresh`)

### Controle de Acesso

- `get_current_user`: Obtém usuário autenticado
- `require_admin`: Exige papel ADMIN
- `verify_car_ownership`: Valida ownership de recursos

---

## Banco de Dados

### SQLAlchemy Async

Todas as operações usam async/await:

```python
async with AsyncSessionLocal() as session:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
```

### Relacionamentos

- `lazy='selectin'`: Carregamento eager para evitar N+1
- `cascade='all, delete-orphan'`: Exclusão em cascata quando apropriado

### Timestamps

- `created_at`: `server_default=func.now()`
- `updated_at`: `server_default=func.now(), server_onupdate=func.now()`

---

## Tratamento de Erros

### HTTP Exceptions

```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Carro não encontrado.',
)
```

### Validações de Negócio

```python
if not brand_exists:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='A marca informada não existe.',
    )
```

### Mensagens de Erro

- Em português brasileiro (pt-BR)
- Claras e acionáveis
- Sem expor detalhes internos

---

## Próximo Passo

Consulte [Estrutura do Projeto](structure.md) para entender a organização de diretórios e arquivos.
