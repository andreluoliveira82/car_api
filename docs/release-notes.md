# Release Notes

Histórico de versões e mudanças do **Car API**.

---

## Versionamento

O projeto segue **Semantic Versioning** (SemVer):

```
MAJOR.MINOR.PATCH
```

| Parte | Quando incrementar | Exemplo |
|-------|-------------------|---------|
| **MAJOR** | Mudanças incompatíveis (breaking changes) | `1.0.0` → `2.0.0` |
| **MINOR** | Novas funcionalidades (compatíveis) | `1.0.0` → `1.1.0` |
| **PATCH** | Correções de bugs (compatíveis) | `1.0.0` → `1.0.1` |

---

## Estrutura de Release Notes

Cada release deve conter:

```markdown
## [Versão] - AAAA-MM-DD

### Adicionado
- Novas funcionalidades

### Alterado
- Mudanças em funcionalidades existentes

### Removido
- Funcionalidades removidas

### Corrigido
- Bugs corrigidos

### Segurança
- Vulnerabilidades corrigidas
```

---

## Releases

### [0.1.0] - 2025-02-20

**Primeira versão estável do Car API.**

#### Adicionado

- **Estrutura do Projeto**
  - Arquitetura modular com separação clara de responsabilidades
  - Organização em camadas: routers, schemas, models, validators, core

- **Models e Banco de Dados**
  - Model `User` com suporte a papéis (USER/ADMIN)
  - Model `Car` com enums para tipo, cor, combustível, transmissão, condição e status
  - Model `Brand` para marcas de carros
  - Timestamps automáticos (`created_at`, `updated_at`)
  - Relacionamentos com carregamento eager (`selectin`)

- **Autenticação e Segurança**
  - Autenticação JWT com access token e refresh token
  - Hash de senhas com Argon2 (via pwdlib)
  - Controle de acesso baseado em papéis (RBAC)
  - Validação de ownership para recursos de carros
  - Dependências `get_current_user` e `require_admin`

- **Endpoints Públicos**
  - `POST /auth/login` — Autenticação de usuários
  - `POST /auth/refresh` — Refresh de token
  - `POST /users/` — Registro de novos usuários
  - `GET /brands/` — Listagem de marcas com paginação
  - `GET /brands/{id}` — Consulta de marca por ID
  - `GET /cars/` — Listagem de carros com filtros avançados
  - `GET /cars/{id}` — Consulta de carro por ID

- **Endpoints Autenticados**
  - `GET /users/me` — Perfil do usuário autenticado
  - `PUT /users/me` — Atualização de perfil (inclui senha)
  - `DELETE /users/me` — Exclusão de conta
  - `POST /cars/` — Criação de carro (vinculado ao usuário)
  - `PUT /cars/{id}` — Atualização de carro (apenas proprietário)
  - `DELETE /cars/{id}` — Exclusão de carro (apenas proprietário)

- **Endpoints Administrativos**
  - `GET /admin/users/` — Listagem de todos os usuários
  - `GET /admin/users/{id}` — Consulta de usuário por ID
  - `PATCH /admin/users/{id}/activate` — Ativar usuário
  - `PATCH /admin/users/{id}/deactivate` — Desativar usuário
  - `PATCH /admin/users/{id}/role` — Alterar papel do usuário
  - `POST /admin/cars/` — Criação de carro para qualquer usuário
  - `GET /admin/cars/` — Listagem de todos os carros
  - `PATCH /admin/cars/{id}/status` — Alterar status do carro
  - `PATCH /admin/cars/{id}/deactivate` — Desativar anúncio
  - `DELETE /admin/cars/{id}` — Exclusão de carro
  - `POST /admin/brands/` — Criação de marca
  - `PUT /admin/brands/{id}` — Atualização de marca
  - `PATCH /admin/brands/{id}/activate` — Ativar marca
  - `PATCH /admin/brands/{id}/deactivate` — Desativar marca
  - `DELETE /admin/brands/{id}` — Exclusão de marca

- **Validações de Negócio**
  - Validação de senha (mínimo 6 caracteres, letras e números)
  - Validação de username (letras, números, underscore, não reservado)
  - Validação de email (formato e domínios descartáveis)
  - Validação de placa (padrão antigo e Mercosul)
  - Validação de anos de fabricação e modelo
  - Validação de preço e quilometragem máximos
  - Validação de nome e descrição de marca

- **Schemas Pydantic**
  - Schemas de criação, atualização e resposta para todas as entidades
  - Validações de campo com `@field_validator`
  - Validações cruzadas com `@model_validator`
  - Suporte a respostas paginadas

- **Configuração e Infraestrutura**
  - Configurações via pydantic-settings
  - Suporte a variáveis de ambiente
  - SQLAlchemy Async com aiosqlite
  - Alembic para migrações
  - Taskipy para automação de tarefas

- **Qualidade de Código**
  - Ruff configurado como linter e formatador
  - Regras de linting personalizadas
  - Convenções de nomenclatura documentadas
  - Docstrings em funções e classes

- **Documentação**
  - Documentação técnica completa em Markdown
  - MkDocs com tema Material
  - Diagramas Mermaid para modelagem do sistema
  - Swagger UI e ReDoc para documentação da API

#### Alterado

- Nenhuma alteração (versão inicial)

#### Removido

- Nenhuma remoção (versão inicial)

#### Corrigido

- Nenhuma correção (versão inicial)

#### Segurança

- Implementação inicial de autenticação JWT
- Hash de senhas com Argon2
- Validação de ownership no backend
- Controle de acesso por papel (USER/ADMIN)

---

## Roadmap

### Versão 0.2.0 (Planejado)

- [ ] Suíte de testes automatizados
- [ ] CI/CD com GitHub Actions
- [ ] Dockerfile e docker-compose
- [ ] Rate limiting em endpoints de autenticação
- [ ] Logs estruturados
- [ ] Cache com Redis (opcional)

### Versão 0.3.0 (Planejado)

- [ ] Upload de imagens para carros
- [ ] Busca full-text em modelos e descrições
- [ ] Webhooks para eventos (carro vendido, etc.)
- [ ] API de favoritos/watchlist

### Versão 1.0.0 (Futuro)

- [ ] Estabilização da API (sem breaking changes)
- [ ] Documentação completa em português e inglês
- [ ] Suporte a múltiplos bancos de dados
- [ ] Versionamento de API (`/api/v2/`)

---

## Breaking Changes

### Guia de Migração

Quando houver breaking changes, este documento será atualizado com:

1. Descrição da mudança
2. Impacto esperado
3. Passos para migração
4. Exemplos de código antes/depois

---

## Histórico de Commits

Para ver o histórico completo de mudanças:

```bash
git log --oneline
```

Ou acesse o repositório no GitHub.

---

## Reportar Issues

Encontrou um bug ou tem sugestão de melhoria?

1. Verifique se já existe uma issue relacionada
2. Crie uma nova issue com template apropriado
3. Aguarde resposta dos mantenedores

---

## Contato

Para dúvidas sobre releases:

- **GitHub Issues**: https://github.com/andreluoliveira82/car-api/issues
- **Email**: andreluoliveira@outlook.com
