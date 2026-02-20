# Estrutura do Projeto

Este documento descreve a organização de diretórios e arquivos do **Car API**, explicando o papel de cada componente na arquitetura.

---

## Visão Geral

```
car_api/
├── car_api/                     # Pacote principal da aplicação
│   ├── __init__.py
│   ├── app.py                   # Entry point da aplicação FastAPI
│   ├── core/                    # Módulos centrais (config, db, security)
│   ├── models/                  # Models SQLAlchemy
│   ├── schemas/                 # Schemas Pydantic
│   ├── routers/                 # Rotas da API (públicas e autenticadas)
│   │   ├── admin/               # Rotas administrativas
│   │   ├── auth.py              # Autenticação (login, refresh)
│   │   ├── users.py             # Rotas de usuário (self-service)
│   │   ├── cars.py              # Rotas de carros (CRUD com ownership)
│   │   └── brands.py            # Rotas de marcas (leitura pública)
│   ├── validators/              # Validações de negócio
│   └── seeds/                   # Dados iniciais (opcional)
├── migrations/                  # Migrações Alembic
│   ├── versions/                # Scripts de migração
│   ├── env.py                   # Configuração do Alembic
│   └── script.py.mako           # Template para novas migrações
├── tests/                       # Testes automatizados
├── docs/                        # Documentação técnica
├── .env                         # Variáveis de ambiente (não versionado)
├── .env.example                 # Template de variáveis de ambiente
├── alembic.ini                  # Configuração do Alembic
├── pyproject.toml               # Dependências e configurações Poetry
├── poetry.lock                  # Lock de dependências
├── mkdocs.yml                   # Configuração da documentação
└── README.md                    # Visão geral do projeto
```

---

## Diretório Principal: `car_api/`

### `app.py` — Entry Point

**Propósito:** Ponto de entrada da aplicação FastAPI.

**Responsabilidades:**

- Instancia a aplicação `FastAPI()`
- Registra todos os routers (públicos e administrativos)
- Define prefixo comum (`/api/v1`)
- Expõe endpoint de health check

**Estrutura:**

```python
app = FastAPI()
prefix = '/api/v1'

# Rotas públicas e autenticadas
app.include_router(router=auth.router, prefix=prefix)
app.include_router(router=users.router, prefix=prefix)
app.include_router(router=brands.router, prefix=prefix)
app.include_router(router=cars.router, prefix=prefix)

# Rotas administrativas
app.include_router(router=admin_users.router, prefix=prefix)
app.include_router(router=admin_brands.router, prefix=prefix)
app.include_router(router=admin_cars.router, prefix=prefix)
```

---

## Diretório: `core/`

Módulos centrais que fornecem infraestrutura para toda a aplicação.

| Arquivo | Propósito |
|---------|-----------|
| `settings.py` | Configurações via pydantic-settings |
| `database.py` | Conexão e sessão do SQLAlchemy Async |
| `security.py` | Autenticação, autorização, JWT, hash de senha |

### `settings.py`

Define a classe `Settings` com todas as variáveis de ambiente. Uma instância global `settings` é exportada para uso em todo o projeto.

### `database.py`

Configura:

- Engine assíncrona
- Session factory (`AsyncSessionLocal`)
- Dependência `get_db_session()` para injeção nos endpoints

### `security.py`

Contém:

- Funções de hash de senha (`get_password_hash`, `verify_password`)
- Criação e validação de tokens JWT
- Dependências `get_current_user` e `require_admin`
- Validação de ownership (`verify_car_ownership`)

---

## Diretório: `models/`

Models SQLAlchemy que representam as tabelas do banco de dados.

| Arquivo | Modelos | Descrição |
|---------|---------|-----------|
| `base.py` | `Base` | Classe base para todos os models |
| `users.py` | `User`, `UserRole` | Usuários e papéis (USER/ADMIN) |
| `cars.py` | `Car`, `Brand`, enums | Carros, marcas e enums relacionados |

### Características dos Models

- Herdam de `Base` (SQLAlchemy Declarative)
- Usam type hints com `Mapped[]`
- Timestamps automáticos (`created_at`, `updated_at`)
- Relacionamentos com `lazy='selectin'` para evitar N+1

### Relacionamentos

```
User (1) ──── (N) Car
Brand (1) ──── (N) Car
```

---

## Diretório: `schemas/`

Schemas Pydantic para validação e serialização de dados.

| Arquivo | Schemas | Propósito |
|---------|---------|-----------|
| `users.py` | `UserBase`, `UserCreate`, `UserUpdate`, `UserPublicSchema` | Validação e resposta de usuários |
| `cars.py` | `CarSchema`, `CarUpdateSchema`, `CarPublicSchema`, `CarListPublicSchema`, `AdminCarCreateSchema` | Validação e resposta de carros |
| `brands.py` | `BrandCreateSchema`, `BrandUpdateSchema`, `BrandPublicSchema`, `BrandListPublicSchema` | Validação e resposta de marcas |
| `auth.py` | `LoginRequest`, `RefreshTokenRequest`, `TokenResponse`, `TokenPairResponse` | Autenticação |

### Padrão de Nomenclatura

| Sufixo | Uso |
|--------|-----|
| `Base` | Campos compartilhados |
| `Create` / `Schema` | Input de criação |
| `Update` | Input de atualização (campos opcionais) |
| `PublicSchema` | Output público |
| `ListPublicSchema` | Output paginado |

---

## Diretório: `routers/`

Rotas da API divididas por domínio e nível de acesso.

### Separação por Acesso

| Diretório/Arquivo | Acesso | Descrição |
|-------------------|--------|-----------|
| `auth.py` | Público | Login e refresh de token |
| `users.py` | Público (registro) / Autenticado (perfil) | Auto-gerenciamento de usuário |
| `cars.py` | Autenticado | CRUD de carros com ownership |
| `brands.py` | Público | Listagem e consulta de marcas |
| `admin/` | Admin | Rotas administrativas |

### Rotas Públicas

- `POST /auth/login` — Autenticação
- `POST /auth/refresh` — Refresh de token
- `POST /users/` — Registro de usuário
- `GET /brands/` — Listar marcas
- `GET /brands/{id}` — Obter marca
- `GET /cars/` — Listar carros (filtros e paginação)
- `GET /cars/{id}` — Obter carro

### Rotas Autenticadas (User)

- `GET /users/me` — Perfil do usuário
- `PUT /users/me` — Atualizar perfil
- `DELETE /users/me` — Excluir conta
- `POST /cars/` — Criar carro (próprio)
- `PUT /cars/{id}` — Atualizar carro (próprio)
- `DELETE /cars/{id}` — Excluir carro (próprio)

### Rotas Administrativas (`/admin`)

| Router | Endpoints | Propósito |
|--------|-----------|-----------|
| `admin/users.py` | `GET`, `GET/{id}`, `PATCH/{id}/activate`, `PATCH/{id}/deactivate`, `PATCH/{id}/role` | Gestão de usuários |
| `admin/cars.py` | `POST`, `GET /`, `PATCH/{id}/status`, `PATCH/{id}/deactivate`, `DELETE/{id}` | Gestão de carros |
| `admin/brands.py` | `POST`, `PUT/{id}`, `PATCH/{id}/activate`, `PATCH/{id}/deactivate`, `DELETE/{id}` | Gestão de marcas |

---

## Diretório: `validators/`

Validações de negócio reutilizáveis.

| Arquivo | Validações |
|---------|------------|
| `users.py` | Senha, nome completo, username, email |
| `cars.py` | Modelo, placa, anos, preço, mileage, nome/descrição da marca |

### Padrão de Implementação

- Funções puras (sem efeitos colaterais)
- Lançam `ValueError` com mensagens em português
- Retornam valor normalizado
- Usadas em validators do Pydantic

---

## Diretório: `migrations/`

Migrações de banco de dados gerenciadas pelo Alembic.

| Arquivo/Diretório | Propósito |
|-------------------|-----------|
| `versions/` | Scripts de migração (um por versão) |
| `env.py` | Configuração do Alembic (online/offline, async) |
| `script.py.mako` | Template para novas migrações |
| `README` | Instruções sobre migrações |

### Comandos Úteis

```bash
# Criar nova migração
alembic revision --autogenerate -m "descrição"

# Aplicar migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1
```

---

## Diretório: `seeds/`

Dados iniciais opcionais para popular o banco de dados em desenvolvimento.

**Exemplo de uso:**

- Criar usuário admin inicial
- Popular marcas de carros conhecidas
- Criar dados de exemplo para testes

---

## Diretório: `tests/`

Testes automatizados (estrutura a ser implementada).

**Estrutura sugerida:**

```
tests/
├── conftest.py              # Fixtures do pytest
├── test_users.py            # Testes de usuários
├── test_cars.py             # Testes de carros
├── test_brands.py           # Testes de marcas
├── test_auth.py             # Testes de autenticação
└── test_admin/              # Testes administrativos
```

---

## Diretório: `docs/`

Documentação técnica em Markdown, servida via MkDocs.

| Arquivo | Conteúdo |
|---------|----------|
| `index.md` | Página inicial |
| `prerequisites.md` | Pré-requisitos |
| `installation.md` | Instalação |
| `configuration.md` | Configuração |
| `guidelines.md` | Padrões de código |
| `structure.md` | Estrutura do projeto |
| `api-endpoints.md` | Endpoints da API |
| `system-modeling.md` | Diagramas e modelagem |
| `authentication.md` | Autenticação e segurança |
| `development.md` | Desenvolvimento |
| `testing.md` | Testes |
| `deployment.md` | Deploy |
| `contributing.md` | Contribuição |
| `release-notes.md` | Histórico de versões |

---

## Arquivos de Configuração

| Arquivo | Propósito |
|---------|-----------|
| `pyproject.toml` | Dependências, scripts Taskipy, config Ruff |
| `poetry.lock` | Lock de dependências (versionado) |
| `alembic.ini` | Configuração do Alembic |
| `mkdocs.yml` | Configuração da documentação |
| `.env` | Variáveis de ambiente (não versionado) |
| `.gitignore` | Arquivos ignorados pelo Git |

---

## Fluxo de Dependências

```
app.py
  │
  ├── routers/
  │     ├── auth.py ────────┐
  │     ├── users.py ───────┤
  │     ├── cars.py ────────┤
  │     ├── brands.py ──────┤
  │     └── admin/ ─────────┤
  │                         │
  ├── core/                 │
  │     ├── settings.py ◄───┘ (importam configurações)
  │     ├── database.py ───► (injetam sessão)
  │     └── security.py ───► (autenticação/autorização)
  │
  ├── models/ ◄───────────── (importados por routers e schemas)
  │
  └── schemas/ ◄──────────── (importados por routers)
        │
        └── validators/ ◄─── (usados em field_validator)
```

---

## Próximo Passo

Consulte [API Endpoints](api-endpoints.md) para uma visão detalhada dos endpoints disponíveis.
