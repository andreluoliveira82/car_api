# 🚗 Car API — FastAPI, SQLAlchemy, Pydantic v2, JWT Auth

API completa para gerenciamento de carros, marcas e usuários, construída com **FastAPI**, **SQLAlchemy Async**, **Pydantic v2**, **Alembic**, **JWT Authentication** e arquitetura modular profissional.

Este projeto foi desenvolvido com foco em:

- Código limpo e organizado  
- Validações robustas  
- Schemas bem definidos  
- Paginação e filtros avançados  
- Autenticação e permissões (em desenvolvimento)  
- Documentação automática via Swagger  

---

## 📂 Estrutura do Projeto

```
car_api/
├── app.py
├── core/
│   ├── database.py
│   ├── security.py
│   └── settings.py
├── models/
│   ├── base.py
│   ├── users.py
│   ├── brands.py
│   └── cars.py
├── routers/
│   ├── users.py
│   ├── brands.py
│   └── cars.py
├── schemas/
│   ├── users.py
│   ├── brands.py
│   └── cars.py
├── validators/
│   ├── users.py
│   └── cars.py
└── migrations/
```

---

## 🚀 Tecnologias Utilizadas

- **Python 3.13**
- **FastAPI**
- **SQLAlchemy Async**
- **Pydantic v2**
- **Alembic**
- **Poetry**
- **SQLite** (pode ser trocado por PostgreSQL facilmente)
- **JWT Authentication** (em desenvolvimento)

---

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/car-api.git
cd car-api
```

# 2. Instale as dependências com Poetry

```
poetry install
```

# 3. Ative o ambiente virtual

```
alembic upgrade head
```

# 4. Execute as migrações

```
uvicorn car_api.app:app --reload
```

# ▶️ Executando o Servidor

```
uvicorn car_api.app:app --reload
```
Acesse:

Swagger UI: http://127.0.0.1:8000/docs (127.0.0.1 in Bing)

ReDoc: http://127.0.0.1:8000/redoc (127.0.0.1 in Bing)

# 🔐 Autenticação (em desenvolvimento)
- O projeto terá:
- Login com JWT
- Refresh token
- Permissões por usuário
- Proteção de rotas

# 🚗 Endpoints Principais
## Cars
- POST /cars/ — Criar carro
- GET /cars/{id} — Buscar carro por ID
- GET /cars/ — Listar carros com filtros e paginação
- PUT /cars/{id} — Atualizar carro
- DELETE /cars/{id} — Remover carro

## Brands
- CRUD completo

## Users
- CRUD completo
- Autenticação JWT (em breve)

# 🧪 Testes
```
pytest -v
```

# 📌 Roadmap
- [x] Estrutura inicial do projeto
- [x] Models, Schemas, Validators
- [x] CRUD completo de Cars
- [ ] Autenticação JWT
- [ ] Permissões por usuário
- [ ] Testes automatizados
- [ ] Dockerfile + docker-compose
- [ ] Deploy na nuvem


# 📄 Licença
MIT License — sinta-se livre para usar e modificar.

# 👨‍💻 Autor
Desenvolvido por André — apaixonado por Python, APIs e boas práticas de software.