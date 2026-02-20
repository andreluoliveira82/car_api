# Deploy

Este documento descreve as considerações e boas práticas para implantar o **Car API** em ambientes de produção.

---

## Visão Geral

O Car API foi desenvolvido com foco em portabilidade e pode ser implantado em diferentes ambientes:

- **Servidores tradicionais** (VM, bare metal)
- **Containers** (Docker, Kubernetes)
- **Plataformas cloud** (AWS, GCP, Azure, Heroku, Railway)
- **Serverless** (com adaptações)

---

## Pré-requisitos de Produção

### Ambiente

| Requisito | Descrição |
|-----------|-----------|
| Python 3.13+ | Versão compatível com o projeto |
| HTTPS obrigatório | TLS/SSL para tráfego criptografado |
| Banco de dados | PostgreSQL recomendado |
| Variáveis de ambiente | Gerenciadas pelo orchestrator |
| Domínio próprio | Para certificados SSL |

### Segurança

| Item | Requisito |
|------|-----------|
| `JWT_SECRET_KEY` | Mínimo 32 bytes aleatórios |
| `DATABASE_URL` | Credenciais seguras, sem hardcoding |
| CORS | Configurado para domínios específicos |
| Rate limiting | Proteger endpoints de autenticação |
| Logs | Sem dados sensíveis (senhas, tokens) |

---

## Configuração de Produção

### Variáveis de Ambiente

```env
# Banco de dados (PostgreSQL recomendado)
DATABASE_URL=postgresql+asyncpg://user:secure_password@db.host.com:5432/car_api

# JWT
JWT_SECRET_KEY=K7gNU3sdo+OL0wNhqoVWhr3g6s1xYv72ol_pe_Ug7go=
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15
JWT_REFRESH_EXPIRATION_DAYS=1

# Domínio
ALLOWED_HOSTS=api.meudominio.com,meudominio.com

# CORS
ALLOW_ORIGINS=https://meudominio.com,https://app.meudominio.com

# Logs
LOG_LEVEL=INFO
```

### Diferenças para Desenvolvimento

| Configuração | Dev | Prod |
|--------------|-----|------|
| `DATABASE_URL` | SQLite local | PostgreSQL/MySQL |
| `JWT_EXPIRATION_MINUTES` | 60 | 15 |
| `JWT_REFRESH_EXPIRATION_DAYS` | 7 | 1 |
| `LOG_LEVEL` | DEBUG | INFO ou WARNING |
| Debug | Habilitado | Desabilitado |

---

## Opções de Deploy

### 1. Deploy com Docker

**Dockerfile sugerido:**

```dockerfile
FROM python:3.13-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install poetry==2.0.0

# Configurar working directory
WORKDIR /app

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Instalar dependências (sem dev)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copiar código da aplicação
COPY . .

# Executar migrações
RUN poetry run alembic upgrade head

# Expor porta
EXPOSE 8000

# Comando de execução
CMD ["uvicorn", "car_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/car_api
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=car_api
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

**Build e execução:**

```bash
docker-compose up -d --build
```

---

### 2. Deploy em Servidor Tradicional

**Passos:**

1. **Preparar servidor:**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python
sudo apt install -y python3.13 python3.13-venv python3-pip

# Instalar Nginx
sudo apt install -y nginx
```

2. **Clonar e configurar:**

```bash
git clone https://github.com/seu-usuario/car-api.git
cd car-api

# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependências
poetry install --no-dev

# Configurar .env
cp .env.example .env
# Editar .env com valores de produção
```

3. **Executar migrações:**

```bash
poetry run alembic upgrade head
```

4. **Configurar Gunicorn/Uvicorn:**

```bash
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
```

5. **Iniciar serviço:**

```bash
poetry run gunicorn car_api.app:app -c gunicorn.conf.py
```

6. **Configurar Nginx (reverse proxy):**

```nginx
server {
    listen 80;
    server_name api.meudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

7. **Configurar HTTPS (Let's Encrypt):**

```bash
sudo certbot --nginx -d api.meudominio.com
```

---

### 3. Deploy em Plataformas Cloud

#### AWS (Elastic Beanstalk)

**Arquivo `.ebextensions/01_config.config`:**

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    DATABASE_URL: "${DATABASE_URL}"
    JWT_SECRET_KEY: "${JWT_SECRET_KEY}"
  aws:elasticbeanstalk:container:python:
    WSGIPath: car_api.app:app
```

#### Heroku

**Procfile:**

```
web: uvicorn car_api.app:app --host 0.0.0.0 --port $PORT
```

**runtime.txt:**

```
python-3.13.x
```

#### Railway / Render

- Conectar repositório GitHub
- Configurar variáveis de ambiente no dashboard
- Deploy automático a cada push

---

## Banco de Dados

### PostgreSQL (Recomendado)

**Vantagens:**

- Suporte completo a SQLAlchemy Async
- Performance superior ao SQLite
- Recursos avançados (índices, full-text search)
- Escalabilidade

**Configuração da URL:**

```
postgresql+asyncpg://user:password@host:5432/database
```

**Instalar driver:**

```bash
poetry add asyncpg
```

**Atualizar settings.py:**

```python
# Em produção, usar PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/car_api
```

### Migrações em Produção

**Antes do deploy:**

```bash
# 1. Backup do banco
pg_dump -U user car_api > backup_$(date +%Y%m%d).sql

# 2. Executar migrações
alembic upgrade head

# 3. Verificar status
alembic current
```

**Rollback (se necessário):**

```bash
alembic downgrade -1
```

---

## Segurança em Produção

### HTTPS

- **Obrigatório** para todas as comunicações
- Usar Let's Encrypt (gratuito) ou certificado comercial
- Configurar redirect HTTP → HTTPS

### CORS

```python
# car_api/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://meudominio.com"],  # Específico!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/auth/login")
@limiter.limit("5/minute")  # Máximo 5 logins por minuto
async def login(...):
    ...
```

### Headers de Segurança

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

---

## Monitoramento e Logs

### Logs

**Configurar logging:**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("car_api")
```

**Boas práticas:**

- Logar requisições e respostas (sem dados sensíveis)
- Logar erros com stack trace
- Usar níveis apropriados (DEBUG, INFO, WARNING, ERROR)

### Health Check

Endpoint já existente:

```
GET /health-check
```

**Uso em load balancers:**

```yaml
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health-check
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
```

### Métricas

**Sugestões:**

- Tempo de resposta por endpoint
- Taxa de erro (4xx, 5xx)
- Uso de CPU/memória
- Conexões de banco de dados

---

## Checklist de Deploy

### Pré-Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados configurado
- [ ] Migrações testadas localmente
- [ ] Tests passando
- [ ] Lint e format OK
- [ ] HTTPS configurado
- [ ] CORS configurado
- [ ] Backup do banco (se aplicável)

### Pós-Deploy

- [ ] Health check respondendo
- [ ] Endpoints públicos acessíveis
- [ ] Autenticação funcionando
- [ ] Logs sendo gerados
- [ ] Monitoramento configurado
- [ ] Rollback testado

---

## Rollback

### Em caso de falha

1. **Reverter código:**

```bash
git revert HEAD
git push
```

2. **Reverter migração:**

```bash
alembic downgrade -1
```

3. **Restaurar backup:**

```bash
psql -U user car_api < backup_YYYYMMDD.sql
```

---

## Escalabilidade

### Horizontal

- Múltiplas instâncias da API
- Load balancer distribuindo tráfego
- Banco de dados compartilhado

### Vertical

- Aumentar recursos da instância (CPU, RAM)
- Otimizar queries do banco de dados
- Usar cache (Redis) para dados frequentes

### Cache (Opcional)

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="car-api-cache")
```

---

## Próximo Passo

Consulte [Contribuição](contributing.md) para diretrizes sobre como contribuir com o projeto.
