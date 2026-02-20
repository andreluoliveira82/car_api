# Contribuição

Este documento descreve as diretrizes para contribuir com o **Car API**, incluindo padrões de código, organização de PRs e fluxo de trabalho.

---

## Como Contribuir

### 1. Fork e Clone

```bash
# Fazer fork no GitHub
# Clonar seu fork
git clone https://github.com/seu-usuario/car-api.git
cd car-api

# Adicionar remote original
git remote add upstream https://github.com/andreluoliveira82/car-api.git
```

### 2. Criar Branch

```bash
git checkout -b feature/sua-feature
```

**Convenção de nomes:**

| Prefixo | Uso | Exemplo |
|---------|-----|---------|
| `feature/` | Nova funcionalidade | `feature/filtrar-carros-por-ano` |
| `fix/` | Correção de bug | `fix/validacao-placa-mercosul` |
| `docs/` | Documentação | `docs/atualizar-readme` |
| `refactor/` | Refatoração | `refactor/extract-validator` |
| `test/` | Testes | `test/adicionar-tests-cars` |
| `chore/` | Manutenção | `chore/atualizar-dependencias` |

### 3. Desenvolver

```bash
# Instalar dependências
poetry install

# Configurar ambiente
cp .env.example .env

# Desenvolver feature

# Executar lint e format
poetry run task lint
poetry run task format

# Commitar mudanças
git add .
git commit -m "feat: descrição da mudança"
```

### 4. Abrir Pull Request

1. Push para seu fork: `git push origin feature/sua-feature`
2. Abrir PR no GitHub
3. Preencher template do PR
4. Aguardar revisão

---

## Padrões de Commit

O projeto segue **Conventional Commits**.

### Estrutura

```
<tipo>(<escopo>): <descrição>

<corpo opcional>

<rodapé opcional>
```

### Tipos

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat(cars): adicionar filtro por ano` |
| `fix` | Correção de bug | `fix(auth): corrigir expiração de token` |
| `docs` | Documentação | `docs(readme): adicionar instruções` |
| `style` | Formatação (sem lógica) | `style: ajustar indentação` |
| `refactor` | Refatoração | `refactor(users): extrair validator` |
| `test` | Testes | `test(cars): adicionar testes de CRUD` |
| `chore` | Build/deps | `chore(deps): atualizar poetry` |

### Escopos

| Escopo | Área |
|--------|------|
| `auth` | Autenticação |
| `users` | Usuários |
| `cars` | Carros |
| `brands` | Marcas |
| `admin` | Admin |
| `db` | Banco de dados |
| `docs` | Documentação |
| `config` | Configuração |

### Exemplos Válidos

```bash
feat(cars): adicionar validação de placa Mercosul

fix(users): corrigir erro ao atualizar email

docs(api): atualizar documentação de endpoints

refactor(validator): extrair lógica de validação de ano

test(cars): adicionar testes para ownership

chore(deps): atualizar dependências de desenvolvimento
```

---

## Padrões de Código

### Estilo

- **Line length**: 92 caracteres
- **Quotes**: Single quotes (`'`)
- **Indentação**: 4 espaços

### Lint e Format

```bash
# Verificar lint
poetry run task lint

# Formatar código
poetry run task format
```

### Imports

Ordem de imports:

1. Biblioteca padrão Python
2. Bibliotecas de terceiros
3. Imports locais

```python
# Padrão
from datetime import datetime

import jwt
from fastapi import Depends

from car_api.core.settings import settings
```

### Type Hints

Sempre usar type hints:

```python
def get_user_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
    ...
```

---

## Pull Requests

### Template de PR

```markdown
## Descrição
<!-- Descreva as mudanças propostas -->

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## Checklist
- [ ] Código formatado
- [ ] Lint passando
- [ ] Tests adicionados/atualizados
- [ ] Documentação atualizada

## Issue relacionada
<!-- Link para issue, se aplicável -->
Fixes #123
```

### Critérios de Aceitação

| Critério | Descrição |
|----------|-----------|
| Código limpo | Sem código comentado ou dead code |
| Tests | Novas features têm testes |
| Docs | Mudanças documentadas |
| Lint | `poetry run task lint` passando |
| Format | `poetry run task format` executado |

### Processo de Revisão

1. **CI/CD**: Tests e lint devem passar
2. **Review**: Pelo menos 1 aprovação necessária
3. **Correções**: Resolver comentários do review
4. **Merge**: Merge via squash ou rebase

---

## Boas Práticas

### Antes de Commitar

- [ ] Executar `poetry run task lint`
- [ ] Executar `poetry run task format`
- [ ] Verificar `git diff` antes de commit
- [ ] Escrever mensagem de commit clara

### Ao Criar PR

- [ ] Branch atualizada com `main`
- [ ] Descrição clara do propósito
- [ ] Screenshots (se aplicável a UI)
- [ ] Link para issue relacionada

### Durante Review

- Responder comentários
- Fazer correções solicitadas
- Manter PR pequeno e focado
- Ser receptivo a feedback

---

## Reportar Bugs

### Template de Bug Report

```markdown
## Descrição
<!-- Descreva o bug claramente -->

## Passos para Reproduzir
1. Passo 1
2. Passo 2
3. Passo 3

## Comportamento Esperado
<!-- O que deveria acontecer -->

## Comportamento Atual
<!-- O que está acontecendo -->

## Ambiente
- OS: [ex: Ubuntu 22.04]
- Python: [ex: 3.13]
- Versão da API: [ex: 0.1.0]

## Logs
<!-- Cole logs relevantes, se aplicável -->

## Screenshots
<!-- Adicione screenshots, se aplicável -->
```

---

## Solicitar Features

### Template de Feature Request

```markdown
## Problema
<!-- Descreva o problema que a feature resolve -->

## Solução Proposta
<!-- Descreva a solução desejada -->

## Alternativas Consideradas
<!-- Outras soluções que você considerou -->

## Contexto Adicional
<!-- Qualquer outra informação relevante -->
```

---

## Código de Conduta

### Princípios

- **Respeito**: Tratar todos com respeito
- **Colaboração**: Ajudar outros contribuidores
- **Construtividade**: Feedback construtivo
- **Inclusão**: Ambiente acolhedor para todos

### Comportamentos Esperados

- Usar linguagem acolhedora
- Respeitar opiniões diferentes
- Aceitar críticas construtivas
- Focar no que é melhor para a comunidade

### Comportamentos Inaceitáveis

- Linguagem ofensiva
- Assédio de qualquer tipo
- Publicar informações privadas de outros
- Outras condutas antiéticas

---

## Reconhecimento

Contribuidores serão reconhecidos no:

- Arquivo `CONTRIBUTORS.md` (se criado)
- Release notes de versões relevantes
- README.md (para contribuições significativas)

---

## Dúvidas?

Para dúvidas sobre contribuição:

1. Abrir issue no GitHub
2. Discutir em discussions do GitHub
3. Contatar mantenedores

---

## Próximo Passo

Consulte [Release Notes](release-notes.md) para histórico de versões do projeto.
