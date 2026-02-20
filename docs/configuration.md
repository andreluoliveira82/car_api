# Configuração

Este documento descreve as variáveis de ambiente, configurações principais e considerações sobre diferentes ambientes (desenvolvimento e produção).

---

## Variáveis de Ambiente

Todas as configurações são gerenciadas pela classe `Settings` em `car_api/core/settings.py`, utilizando **pydantic-settings**. As variáveis devem ser definidas em um arquivo `.env` na raiz do projeto ou no ambiente do sistema.

### Banco de Dados

| Variável | Descrição | Exemplo (Dev) | Exemplo (Prod) |
|----------|-----------|---------------|----------------|
| `DATABASE_URL` | URL de conexão com o banco de dados | `sqlite+aiosqlite:///./cars.db` | `postgresql+asyncpg://user:pass@host:5432/dbname` |

**Observações:**

- O projeto utiliza SQLAlchemy Async, portanto a URL deve incluir o driver assíncrono.
- Para SQLite: use `sqlite+aiosqlite://`
- Para PostgreSQL: use `postgresql+asyncpg://`
- Para MySQL: use `mysql+aiomysql://`

---

### Autenticação JWT

| Variável | Descrição | Padrão | Recomendação |
|----------|-----------|--------|--------------|
| `JWT_SECRET_KEY` | Chave secreta para assinar tokens | (obrigatório) | Mínimo 32 caracteres aleatórios |
| `JWT_ALGORITHM` | Algoritmo de assinatura | `HS256` | Manter HS256 ou usar RS256 em produção |
| `JWT_EXPIRATION_MINUTES` | Validade do access token (minutos) | `30` | 15-60 minutos |
| `JWT_REFRESH_EXPIRATION_DAYS` | Validade do refresh token (dias) | `1` | 1-7 dias |

**Exemplo de geração de chave segura:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### Regras de Negócio

| Variável | Descrição | Padrão | Uso |
|----------|-----------|--------|-----|
| `MIN_FACTORY_YEAR` | Ano mínimo de fabricação | `2000` | Validação de carros |
| `MAX_FUTURE_YEAR` | Anos futuros permitidos | `1` | Limite de ano do modelo |
| `MAX_PRICE` | Preço máximo permitido | `10000000` | Validação de preço |
| `MAX_MILEAGE` | Quilometragem máxima | `1000000` | Validação de mileage |
| `MAX_BRAND_DESCRIPTION` | Tamanho máximo da descrição da marca | `500` | Validação de texto |

---

## Estrutura de Configuração

```python
# car_api/core/settings.py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_MINUTES: int = 30
    JWT_REFRESH_EXPIRATION_DAYS: int = 1
    
    MIN_FACTORY_YEAR: int
    MAX_FUTURE_YEAR: int
    MAX_PRICE: int
    MAX_MILEAGE: int
    MAX_BRAND_DESCRIPTION: int

settings = Settings()
```

A instância global `settings` é importada em todo o projeto para acesso às configurações.

---

## Ambientes

### Desenvolvimento

**Características:**

- Banco de dados SQLite local
- Debug implícito (logs detalhados)
- Tokens com expiração mais longa para conveniência
- Chave JWT pode ser simples (apenas para dev)

**Arquivo `.env` sugerido:**

```env
DATABASE_URL=sqlite+aiosqlite:///./cars.db

JWT_SECRET_KEY=dev-secret-key-not-for-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
JWT_REFRESH_EXPIRATION_DAYS=7

MIN_FACTORY_YEAR=2000
MAX_FUTURE_YEAR=1
MAX_PRICE=10000000
MAX_MILEAGE=1000000
MAX_BRAND_DESCRIPTION=500
```

---

### Produção

**Características:**

- Banco de dados PostgreSQL ou MySQL
- Chave JWT gerada criptograficamente
- Tokens com expiração curta
- Variáveis de ambiente injetadas pelo orchestrator (Docker, Kubernetes, etc.)
- Sem arquivo `.env` em produção real

**Recomendações:**

1. **Nunca commitar** o arquivo `.env` no repositório
2. Usar segredos gerenciados (AWS Secrets Manager, Azure Key Vault, etc.)
3. Habilitar apenas HTTPS
4. Configurar CORS adequadamente
5. Usar connection pooling no banco de dados

**Exemplo de `.env` para produção:**

```env
DATABASE_URL=postgresql+asyncpg://user:secure-pass@db.host.com:5432/car_api

JWT_SECRET_KEY=K7gNU3sdo+OL0wNhqoVWhr3g6s1xYv72ol_pe_Ug7go=
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15
JWT_REFRESH_EXPIRATION_DAYS=1

MIN_FACTORY_YEAR=2000
MAX_FUTURE_YEAR=1
MAX_PRICE=10000000
MAX_MILEAGE=1000000
MAX_BRAND_DESCRIPTION=500
```

---

## Configurações do Ruff

O linter/formatador está configurado no `pyproject.toml`:

```toml
[tool.ruff]
line-length = 92

[tool.ruff.lint]
preview = true
select = ['I', 'F', 'E', 'W', 'PL', 'PT']
ignore = [
    'E501',        # Comentários e docstrings longos
    'PLR2004',     # Números mágicos
    'PLR0917',     # Muitos argumentos
    'PLR0913',     # Muitos parâmetros
    'PLR0912',     # Muitas branches
]

[tool.ruff.format]
preview = true
quote-style = 'single'
```

**Regras selecionadas:**

- `I`: Ordenação de imports
- `F`: Erros do Pyflakes
- `E`, `W`: Erros e warnings do Pycodestyle
- `PL`: Pylint
- `PT`: Boas práticas para testes

---

## Considerações sobre Configuração

### Por que pydantic-settings?

- Validação automática de tipos
- Documentação implícita via type hints
- Suporte a múltiplas fontes de configuração
- Mensagens de erro claras

### Por que uma instância global `settings`?

- Evita passar configurações como dependência em todos os endpoints
- Centraliza o acesso às configurações
- Facilita testes (pode ser mockada)

---

## Próximo Passo

Consulte [Guidelines e Padrões](guidelines.md) para entender as convenções de código adotadas no projeto.
