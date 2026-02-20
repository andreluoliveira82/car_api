# Pré-requisitos

Este documento descreve os requisitos de ambiente e as ferramentas necessárias para desenvolver e executar o **Car API**.

---

## Requisitos de Ambiente

| Componente | Versão Mínima | Versão Recomendada | Descrição |
|------------|---------------|--------------------|-----------|
| **Python** | 3.13 | 3.13.x | Linguagem principal do projeto |
| **Poetry** | 2.0.0 | 2.x | Gerenciador de dependências e ambientes virtuais |
| **Git** | 2.x | 2.x | Controle de versão |
| **SQLite** | 3.x | 3.x | Banco de dados padrão (embutido) |

### Observações sobre o Banco de Dados

O projeto utiliza **SQLite** como banco de dados padrão para desenvolvimento, configurado via SQLAlchemy Async. A migração para bancos de produção (PostgreSQL, MySQL) é suportada através da alteração da `DATABASE_URL` nas variáveis de ambiente.

---

## Ferramentas Utilizadas

### Gerenciamento de Dependências

- **Poetry**: Gerencia dependências, ambientes virtuais e empacotamento do projeto.

### Qualidade de Código

- **Ruff**: Linter e formatador de código (substitui Flake8, Black, isort).
  - Configurado no `pyproject.toml` com regras específicas do projeto.

### Documentação

- **MkDocs** + **Material for MkDocs**: Geração de documentação estática.
- **PyMdown Extensions**: Suporte a diagramas Mermaid e formatação avançada.

### Banco de Dados e Migrações

- **SQLAlchemy Async**: ORM assíncrono para operações de banco de dados.
- **Alembic**: Gerenciamento de migrações de schema.
- **aiosqlite**: Driver assíncrono para SQLite.

### Autenticação e Segurança

- **PyJWT**: Geração e validação de tokens JWT.
- **pwdlib** (com argon2): Hash de senhas com algoritmo recomendado.

### Framework e Validação

- **FastAPI**: Framework web assíncrono.
- **Pydantic v2**: Validação de dados e schemas.
- **pydantic-settings**: Gerenciamento de configurações via variáveis de ambiente.

---

## Verificação do Ambiente

Antes de iniciar, verifique as versões instaladas:

```bash
python --version      # Deve retornar Python 3.13.x
poetry --version      # Deve retornar Poetry 2.x
git --version         # Deve retornar Git 2.x
```

---

## Considerações de Sistema Operacional

O projeto é compatível com:

- **Linux** (desenvolvimento principal)
- **macOS**
- **Windows** (via WSL2 recomendado)

A execução do servidor de desenvolvimento utiliza `fastapi dev`, que está disponível nas versões mais recentes do FastAPI.
