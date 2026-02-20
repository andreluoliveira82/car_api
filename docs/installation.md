# Instalação

Guia passo a passo para configurar e executar o **Car API** localmente.

---

## 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/car-api.git
cd car-api
```

---

## 2. Instale as Dependências

O projeto utiliza **Poetry** para gerenciamento de dependências. Instale todas as dependências (incluindo as de desenvolvimento):

```bash
poetry install
```

Este comando:

- Cria um ambiente virtual isolado
- Instala todas as dependências listadas no `pyproject.toml`
- Configura o ambiente para desenvolvimento

---

## 3. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as configurações necessárias:

```bash
cp .env.example .env  # Se existir um template
```

Ou crie manualmente:

```env
DATABASE_URL=sqlite+aiosqlite:///./cars.db

JWT_SECRET_KEY=sua-chave-secreta-forte-aqui
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
JWT_REFRESH_EXPIRATION_DAYS=1

MIN_FACTORY_YEAR=2000
MAX_FUTURE_YEAR=1
MAX_PRICE=10000000
MAX_MILEAGE=1000000
MAX_BRAND_DESCRIPTION=500
```

> **Nota**: Em produção, utilize valores seguros para `JWT_SECRET_KEY` (mínimo 32 caracteres aleatórios).

---

## 4. Execute as Migrações

Antes de rodar a aplicação, é necessário criar o schema do banco de dados:

```bash
alembic upgrade head
```

Este comando executa todas as migrações pendentes e cria as tabelas no banco de dados.

---

## 5. Execute a Aplicação

### Modo de Desenvolvimento

Utilize o comando configurado no **Taskipy**:

```bash
poetry run task run
```

Ou diretamente com FastAPI:

```bash
fastapi dev car_api/app.py
```

O servidor será iniciado em:

- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health-check

---

## 6. Sirva a Documentação (Opcional)

Para visualizar a documentação técnica localmente:

```bash
poetry run task docs
```

A documentação estará disponível em: http://127.0.0.1:8001

---

## Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `poetry run task lint` | Executa o linter (Ruff) |
| `poetry run task format` | Formata o código com Ruff |
| `poetry run task run` | Inicia o servidor de desenvolvimento |
| `poetry run task docs` | Serve a documentação localmente |
| `alembic revision --autogenerate -m "mensagem"` | Cria nova migração |
| `alembic upgrade head` | Aplica todas as migrações |
| `alembic downgrade -1` | Reverte última migração |

---

## Solução de Problemas

### Erro: "No module named 'car_api'"

Certifique-se de que o ambiente virtual do Poetry está ativo:

```bash
poetry shell
```

### Erro: "DATABASE_URL not found"

Verifique se o arquivo `.env` existe e contém a variável `DATABASE_URL`.

### Erro: "Table already exists"

O banco de dados já foi migrado. Execute:

```bash
rm cars.db  # Apenas em desenvolvimento
alembic upgrade head
```

---

## Próximo Passo

Após a instalação, consulte o documento de [Configuração](configuration.md) para entender as opções de ambiente e personalização.
