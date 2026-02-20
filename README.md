# 🚗 Car API

API REST completa para gerenciamento de anúncios de veículos, construída com **FastAPI**, **SQLAlchemy Async**, **Pydantic v2** e **JWT Authentication**.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.129-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Sobre o Projeto

A **Car API** é um backend para marketplace de veículos com:

- ✅ Autenticação JWT (access + refresh tokens)
- ✅ Controle de acesso por papéis (USER / ADMIN)
- ✅ Validação de ownership de recursos
- ✅ CRUD completo de carros, marcas e usuários
- ✅ Filtros avançados e paginação
- ✅ Validações de negócio robustas
- ✅ Documentação automática (Swagger) + técnica (MkDocs)

---

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.13+
- Poetry 2.x

### Instalação

```bash
# Clone o repositório
git clone https://github.com/andreluoliveira82/car-api.git
cd car-api

# Instale as dependências
poetry install

# Configure variáveis de ambiente
cp .env.example .env  # Ou crie seu .env

# Execute migrações
alembic upgrade head

# Inicie o servidor
poetry run task run
```

### Acesse

| Serviço | URL |
|---------|-----|
| API | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| Health Check | http://127.0.0.1:8000/health-check |

---

## 📋 Principais Endpoints

### Autenticação
```bash
POST /api/v1/auth/login      # Obter tokens
POST /api/v1/auth/refresh    # Renovar access token
```

### Usuários
```bash
POST   /api/v1/users/        # Registro
GET    /api/v1/users/me      # Perfil (auth)
PUT    /api/v1/users/me      # Atualizar (auth)
DELETE /api/v1/users/me      # Excluir conta (auth)
```

### Carros
```bash
GET    /api/v1/cars/         # Listar (filtros + paginação)
GET    /api/v1/cars/{id}     # Obter detalhes
POST   /api/v1/cars/         # Criar (auth)
PUT    /api/v1/cars/{id}     # Atualizar (owner)
DELETE /api/v1/cars/{id}     # Excluir (owner)
```

### Admin
```bash
GET    /api/v1/admin/users/        # Listar usuários
PATCH  /api/v1/admin/users/{id}/role   # Alterar papel
POST   /api/v1/admin/cars/         # Criar (qualquer owner)
DELETE /api/v1/admin/cars/{id}     # Excluir (qualquer)
```

---

## 🏗️ Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Routers    │────▶│   Core      │────▶│   Models    │
│ (Endpoints) │     │ (Security)  │     │ (SQLAlchemy)│
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Schemas    │     │  Settings   │     │   Database  │
│ (Pydantic)  │     │  (Config)   │     │   (Async)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Estrutura de diretórios:**

```
car_api/
├── car_api/
│   ├── app.py              # Entry point
│   ├── core/               # Config, database, security
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── routers/            # Rotas públicas/autenticadas
│   │   └── admin/          # Rotas administrativas
│   └── validators/         # Validações de negócio
├── migrations/             # Alembic migrations
├── tests/                  # Testes
├── docs/                   # Documentação técnica
└── pyproject.toml
```

---

## 🔐 Autenticação e Autorização

### Níveis de Acesso

| Nível | Descrição | Endpoints |
|-------|-----------|-----------|
| **Público** | Sem autenticação | Login, registro, listagens |
| **Autenticado** | Token JWT necessário | Perfil, CRUD próprio |
| **Admin** | Token + papel ADMIN | Gestão de usuários, moderação |

### Fluxo de Login

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Senha123"}'

# 2. Use o access_token nas requisições
curl -X GET http://127.0.0.1:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

---

## 🛠️ Stack Tecnológico

| Categoria | Tecnologia |
|-----------|------------|
| **Linguagem** | Python 3.13 |
| **Framework** | FastAPI |
| **ORM** | SQLAlchemy Async |
| **Validação** | Pydantic v2 |
| **Auth** | PyJWT + pwdlib (Argon2) |
| **Banco de Dados** | SQLite (dev) / PostgreSQL (prod) |
| **Migrações** | Alembic |
| **Gerenciador** | Poetry |
| **Qualidade** | Ruff |
| **Documentação** | MkDocs + Material |

---

## 📚 Documentação

A documentação completa está disponível em:

- **Swagger UI** — Documentação interativa da API: `/docs`
- **ReDoc** — Documentação alternativa: `/redoc`
- **Documentação Técnica** — Guias completos: `docs/`

### Guias Disponíveis

| Documento | Descrição |
|-----------|-----------|
| [Prerequisites](docs/prerequisites.md) | Requisitos de ambiente |
| [Installation](docs/installation.md) | Instalação passo a passo |
| [Configuration](docs/configuration.md) | Variáveis de ambiente |
| [Guidelines](docs/guidelines.md) | Padrões de código |
| [Structure](docs/structure.md) | Estrutura do projeto |
| [API Endpoints](docs/api-endpoints.md) | Catálogo de endpoints |
| [System Modeling](docs/system-modeling.md) | Diagramas e modelagem |
| [Authentication](docs/authentication.md) | JWT e segurança |
| [Development](docs/development.md) | Fluxo de desenvolvimento |
| [Testing](docs/testing.md) | Estratégia de testes |
| [Deployment](docs/deployment.md) | Deploy em produção |
| [Contributing](docs/contributing.md) | Como contribuir |
| [Release Notes](docs/release-notes.md) | Histórico de versões |

---

## ⚙️ Comandos Úteis

```bash
# Lint
poetry run task lint

# Format
poetry run task format

# Run
poetry run task run

# Docs
poetry run task docs

# Migrações
alembic revision --autogenerate -m "mensagem"
alembic upgrade head
alembic downgrade -1
```

---

## 📦 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=sqlite+aiosqlite:///./cars.db

JWT_SECRET_KEY=sua-chave-secreta-forte
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
JWT_REFRESH_EXPIRATION_DAYS=1

MIN_FACTORY_YEAR=2000
MAX_FUTURE_YEAR=1
MAX_PRICE=10000000
MAX_MILEAGE=1000000
MAX_BRAND_DESCRIPTION=500
```

---

## 🧪 Testes

```bash
# Executar testes
pytest -v

# Com cobertura
pytest --cov=car_api --cov-report=html
```

---

## 📌 Roadmap

### ✅ Concluído

- [x] Estrutura modular do projeto
- [x] Models, Schemas, Validators
- [x] CRUD completo de Carros
- [x] CRUD completo de Usuários
- [x] CRUD completo de Marcas
- [x] Autenticação JWT
- [x] Controle de acesso por papel (USER / ADMIN)
- [x] Validação de ownership
- [x] Documentação técnica completa

### 🔄 Em Desenvolvimento

- [ ] Suíte de testes automatizados
- [ ] CI/CD (GitHub Actions)
- [ ] Dockerfile + docker-compose

### 📋 Planejado

- [ ] Upload de imagens
- [ ] Rate limiting
- [ ] Cache com Redis
- [ ] Deploy em produção

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja o guia de [Contribuição](docs/contributing.md).

```bash
# 1. Fork o projeto
# 2. Crie uma branch para sua feature
git checkout -b feature/minha-feature

# 3. Commit suas mudanças
git commit -m 'feat: adicionar minha feature'

# 4. Push para o remote
git push origin feature/minha-feature

# 5. Abra um Pull Request
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

**André Oliveira**  
Email: andreluoliveira@outlook.com  
GitHub: [andreluoliveira82](https://github.com/andreluoliveira82)

---

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) — Framework web moderno
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM poderoso
- [Pydantic](https://docs.pydantic.dev/) — Validação de dados
- [MkDocs](https://www.mkdocs.org/) — Gerador de documentação
