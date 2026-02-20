# Desenvolvimento

Este documento descreve como contribuir com o desenvolvimento do **Car API**, incluindo configuração do ambiente, execução de tarefas e boas práticas.

---

## Configuração do Ambiente de Desenvolvimento

### 1. Clone e Instale

```bash
git clone https://github.com/seu-usuario/car-api.git
cd car-api
poetry install
```

### 2. Configure Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

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

### 3. Execute Migrações

```bash
alembic upgrade head
```

### 4. Inicie o Servidor

```bash
poetry run task run
```

---

## Tarefas Disponíveis

O projeto utiliza **Taskipy** para automatizar tarefas comuns, configuradas no `pyproject.toml`.

### Lista de Tarefas

| Tarefa | Comando | Descrição |
|--------|---------|-----------|
| `lint` | `poetry run task lint` | Executa o linter Ruff |
| `format` | `poetry run task format` | Formata o código com Ruff |
| `run` | `poetry run task run` | Inicia o servidor de desenvolvimento |
| `docs` | `poetry run task docs` | Serve a documentação localmente |

### Comandos Equivalentes

```bash
# Lint
poetry run task lint
# ou
ruff check .

# Format (com auto-fix)
poetry run task format
# ou
ruff check --fix && ruff format .

# Run
poetry run task run
# ou
fastapi dev car_api/app.py

# Docs
poetry run task docs
# ou
mkdocs serve -a 127.0.0.1:8001
```

---

## Fluxo de Desenvolvimento

### 1. Criar Branch para Feature

```bash
git checkout -b feature/nova-funcionalidade
```

**Convenção de branches:**

| Prefixo | Uso |
|---------|-----|
| `feature/` | Nova funcionalidade |
| `fix/` | Correção de bug |
| `docs/` | Atualização de documentação |
| `refactor/` | Refatoração de código |
| `test/` | Adição ou atualização de testes |
| `chore/` | Tarefas de manutenção |

### 2. Desenvolver e Testar

```bash
# Fazer alterações no código

# Executar lint
poetry run task lint

# Formatar código
poetry run task format

# Testar manualmente via Swagger ou curl
```

### 3. Commitar Mudanças

```bash
git add .
git commit -m "feat: adicionar nova funcionalidade de X"
```

**Ver [Padrões de Commit](#padrões-de-commit).**

### 4. Criar Pull Request

1. Push para o remote: `git push origin feature/nova-funcionalidade`
2. Abrir PR no GitHub
3. Aguardar revisão
4. Corrigir issues apontados
5. Merge após aprovação

---

## Padrões de Commit

O projeto segue convenções do **Conventional Commits**.

### Estrutura

```
<tipo>(<escopo>): <descrição curta>

<corpo opcional>

<rodapé opcional>
```

### Tipos

| Tipo | Descrição |
|------|-----------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Atualização de documentação |
| `style` | Formatação, ponto e vírgula, etc. (sem mudança de lógica) |
| `refactor` | Refatoração (sem mudança de comportamento) |
| `test` | Adicionar ou corrigir testes |
| `chore` | Atualização de build, dependências, etc. |

### Exemplos

```bash
# Nova funcionalidade
feat(cars): adicionar filtro por ano na listagem de carros

# Correção de bug
fix(auth): corrigir validação de token expirado

# Documentação
docs(readme): atualizar instruções de instalação

# Refatoração
refactor(users): extrair validação de email para validator

# Testes
test(cars): adicionar testes de integração para CRUD

# Chore
chore(deps): atualizar dependências de desenvolvimento
```

### Escopos Sugeridos

| Escopo | Área |
|--------|------|
| `auth` | Autenticação e autorização |
| `users` | Usuários |
| `cars` | Carros |
| `brands` | Marcas |
| `admin` | Rotas administrativas |
| `db` | Banco de dados e migrações |
| `docs` | Documentação |
| `config` | Configuração e settings |

---

## Boas Práticas de Desenvolvimento

### Código

1. **Siga o estilo existente**: Use Ruff para lint e format
2. **Escreva testes**: Para novas funcionalidades e correções
3. **Documente**: Atualize docstrings e documentação externa
4. **Mantenha simples**: Evite complexidade desnecessária
5. **Valide dados**: Use schemas Pydantic para input/output

### Banco de Dados

1. **Crie migrações**: Toda mudança de schema requer migração
2. **Teste migrações**: Execute `upgrade` e `downgrade` localmente
3. **Nomeie claramente**: Use descrições explícitas nas migrações

```bash
# Bom
alembic revision --autogenerate -m "add plate index to cars table"

# Ruim
alembic revision --autogenerate -m "update cars"
```

### Segurança

1. **Nunca commitar `.env`**: Arquivo no `.gitignore`
2. **Validar input**: Sempre usar schemas Pydantic
3. **Proteger rotas**: Usar `get_current_user` e `require_admin`
4. **Validar ownership**: Verificar propriedade de recursos

### Performance

1. **Evitar N+1**: Usar `lazy='selectin'` em relacionamentos
2. **Paginar listagens**: Sempre usar `offset` e `limit`
3. **Indexar colunas**: Adicionar índices em colunas de filtro

---

## Estrutura de Features

### Adicionar Nova Entidade

1. **Model** (`models/`): Definir tabela SQLAlchemy
2. **Schema** (`schemas/`): Definir validação Pydantic
3. **Validator** (`validators/`): Regras de negócio
4. **Router** (`routers/`): Endpoints da API
5. **Migração** (`migrations/`): Criar tabela no banco

### Adicionar Novo Endpoint

1. Definir rota no router apropriado
2. Especificar métodos HTTP e path
3. Definir schemas de request/response
4. Adicionar documentação (`summary`, `description`)
5. Aplicar autenticação se necessário

### Adicionar Validação

1. Criar função em `validators/`
2. Usar `@field_validator` no schema
3. Testar casos válidos e inválidos

---

## Debugging

### Logs

FastAPI loga automaticamente requisições e erros.

### Debug com Print

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Valor de user_id: {user_id}")
```

### Debug com IDE

Configure o interpretador para usar o ambiente virtual do Poetry:

```bash
poetry run which python
# Use este caminho na sua IDE
```

### Inspecionar no Swagger

Use `/docs` para testar endpoints e inspecionar requests/responses.

---

## Migrações

### Criar Nova Migração

```bash
alembic revision --autogenerate -m "descrição da mudança"
```

### Revisar Migração

Verifique o arquivo gerado em `migrations/versions/`:

```python
def upgrade() -> None:
    # Verificar se as operações estão corretas
    op.create_table('nova_tabela', ...)
```

### Aplicar Migração

```bash
alembic upgrade head
```

### Reverter Migração

```bash
# Última migração
alembic downgrade -1

# Migração específica
alembic downgrade <revision_id>
```

---

## Documentação

### Atualizar Documentação Técnica

1. Editar arquivo Markdown em `docs/`
2. Testar localmente: `poetry run task docs`
3. Commitar mudanças

### Documentar Código

```python
def create_user(
    user: UserCreate,
    db: AsyncSession,
) -> User:
    """
    Create a new user in the database.
    
    Args:
        user: User data for creation
        db: Database session
        
    Returns:
        Created user object
        
    Raises:
        HTTPException: If username or email already exists
    """
```

---

## Resolução de Problemas

### Dependências Conflitantes

```bash
poetry lock --no-update
poetry install
```

### Banco de Dados Corrompido (Dev)

```bash
rm cars.db
alembic upgrade head
```

### Migração Falhou

```bash
# Reverter para estado anterior
alembic downgrade -1

# Corrigir migração
# Editar arquivo em migrations/versions/

# Reaplicar
alembic upgrade head
```

### Ruff Aponta Erros

```bash
# Tentar auto-fix
ruff check --fix

# Ver erros restantes
ruff check
```

---

## Checklist de Pull Request

Antes de abrir um PR, verifique:

- [ ] Código formatado (`poetry run task format`)
- [ ] Lint passando (`poetry run task lint`)
- [ ] Migrações criadas (se aplicável)
- [ ] Documentação atualizada (se aplicável)
- [ ] Commits seguem padrão Conventional Commits
- [ ] Branch atualizada com `main`
- [ ] Testes manuais realizados

---

## Próximo Passo

Consulte [Testes](testing.md) para informações sobre a estratégia de testes do projeto.
