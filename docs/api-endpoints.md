# API Endpoints

Visão geral dos endpoints da **Car API**, organizados por nível de acesso. Para detalhes completos de cada endpoint (parâmetros, schemas de request/response), consulte a documentação Swagger em `/docs`.

---

## Base URL

Todos os endpoints estão sob o prefixo:

```
/api/v1
```

**Exemplo:** `http://127.0.0.1:8000/api/v1/cars/`

---

## Endpoints Públicos

Acessíveis sem autenticação.

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/auth/login` | Autenticar usuário e obter tokens |
| `POST` | `/auth/refresh` | Renovar access token usando refresh token |

**Exemplo de login:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha123"}'
```

**Resposta:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### Usuários

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/users/` | Criar novo usuário (registro) |

**Observação:** Não há listagem pública de usuários para prevenir enumeração e vazamento de dados.

---

### Marcas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/brands/` | Listar marcas com paginação e filtros |
| `GET` | `/brands/{brand_id}` | Obter marca por ID |

**Parâmetros de listagem:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `offset` | int | Deslocamento (padrão: 0) |
| `limit` | int | Limite de resultados (1-100, padrão: 10) |
| `search` | string | Busca por nome |
| `is_active` | bool | Filtrar por status ativo |

---

### Carros

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/cars/` | Listar carros com paginação e filtros avançados |
| `GET` | `/cars/{car_id}` | Obter carro por ID (inclui marca e proprietário) |

**Parâmetros de listagem:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `offset` | int | Deslocamento |
| `limit` | int | Limite (1-100) |
| `search` | string | Busca por modelo, cor ou placa |
| `car_type` | enum | Tipo do carro (hatch, sedan, suv, etc.) |
| `color` | enum | Cor do carro |
| `fuel_type` | enum | Tipo de combustível |
| `transmission` | enum | Tipo de transmissão |
| `condition` | enum | Condição (new, used, certified pre-owned) |
| `status` | enum | Status (available, unavailable, sold, etc.) |
| `brand_id` | int | Filtrar por marca |
| `owner_id` | int | Filtrar por proprietário |
| `min_year` | int | Ano mínimo do modelo |
| `max_year` | int | Ano máximo do modelo |
| `min_price` | decimal | Preço mínimo |
| `max_price` | decimal | Preço máximo |

**Resposta paginada:**

```json
{
  "cars": [...],
  "offset": 0,
  "limit": 10,
  "total": 150
}
```

---

## Endpoints Autenticados

Requerem token JWT no header `Authorization: Bearer <token>`.

### Usuários (Self-Service)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/users/me` | Obter perfil do usuário autenticado |
| `PUT` | `/users/me` | Atualizar perfil (inclui troca de senha) |
| `DELETE` | `/users/me` | Excluir própria conta |

**Exemplo de requisição autenticada:**

```bash
curl -X GET http://127.0.0.1:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

---

### Carros (Ownership)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/cars/` | Criar novo carro (vinculado ao usuário autenticado) |
| `PUT` | `/cars/{car_id}` | Atualizar carro (apenas se for o proprietário) |
| `DELETE` | `/cars/{car_id}` | Excluir carro (apenas se for o proprietário) |

**Regras de Ownership:**

- O `owner_id` é automaticamente definido como o ID do usuário autenticado na criação
- Atualização e exclusão verificam se o usuário é o proprietário
- Usuários ADMIN podem contornar esta restrição (ver rotas administrativas)

**Exemplo de criação:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/cars/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "car_type": "suv",
    "model": "Corolla Cross",
    "factory_year": 2025,
    "model_year": 2026,
    "color": "white",
    "fuel_type": "flex",
    "transmission": "automatic",
    "condition": "new",
    "mileage": 0,
    "plate": "ABC0D12",
    "price": 105999.99,
    "brand_id": 1
  }'
```

---

## Endpoints Administrativos

Requerem token JWT com papel **ADMIN**. Prefixo adicional: `/admin`

### Usuários (Admin)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/admin/users/` | Listar todos os usuários |
| `GET` | `/admin/users/{user_id}` | Obter usuário por ID |
| `PATCH` | `/admin/users/{user_id}/activate` | Ativar conta de usuário |
| `PATCH` | `/admin/users/{user_id}/deactivate` | Desativar conta de usuário |
| `PATCH` | `/admin/users/{user_id}/role` | Alterar papel (USER/ADMIN) |

**Parâmetros de listagem:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `offset` | int | Deslocamento |
| `limit` | int | Limite (1-100) |
| `search` | string | Busca por username, nome ou email |

---

### Carros (Admin)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/admin/cars/` | Criar carro em nome de qualquer usuário |
| `GET` | `/admin/cars/` | Listar todos os carros (sem restrição de ownership) |
| `PATCH` | `/admin/cars/{car_id}/status` | Alterar status do carro |
| `PATCH` | `/admin/cars/{car_id}/deactivate` | Desativar anúncio |
| `DELETE` | `/admin/cars/{car_id}` | Excluir carro (qualquer proprietário) |

**Diferenças para rotas de usuário:**

- Admin pode criar carros para qualquer `owner_id`
- Admin pode listar todos os carros, não apenas os próprios
- Admin pode alterar status e desativar carros de terceiros
- Admin pode excluir qualquer carro

---

### Marcas (Admin)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/admin/brands/` | Criar nova marca |
| `PUT` | `/admin/brands/{brand_id}` | Atualizar marca |
| `PATCH` | `/admin/brands/{brand_id}/activate` | Ativar marca |
| `PATCH` | `/admin/brands/{brand_id}/deactivate` | Desativar marca |
| `DELETE` | `/admin/brands/{brand_id}` | Excluir marca (se não tiver carros vinculados) |

**Regra de exclusão:**

- Não é possível excluir marca com carros associados (integridade referencial)

---

## Health Check

Endpoint fora do prefixo `/api/v1`, usado para monitoramento de saúde da aplicação.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health-check` | Verificar status da aplicação |

**Resposta:**

```json
{
  "status": "healthy"
}
```

---

## Códigos de Status HTTP

| Código | Significado | Uso Comum |
|--------|-------------|-----------|
| `200 OK` | Sucesso | GET, PUT, PATCH bem-sucedidos |
| `201 Created` | Criado | POST de criação |
| `204 No Content` | Sem conteúdo | DELETE bem-sucedido |
| `400 Bad Request` | Requisição inválida | Validação de dados falhou |
| `401 Unauthorized` | Não autenticado | Token ausente ou inválido |
| `403 Forbidden` | Acesso negado | Permissão insuficiente |
| `404 Not Found` | Não encontrado | Recurso não existe |
| `409 Conflict` | Conflito | Recurso duplicado (ex: email, placa) |
| `500 Internal Server Error` | Erro interno | Exceção não tratada |

---

## Autenticação

### Como Autenticar

1. Faça login via `POST /auth/login`
2. Extraia o `access_token` da resposta
3. Inclua no header das requisições: `Authorization: Bearer <token>`

### Refresh de Token

Quando o access token expirar (30 minutos):

1. Use o `refresh_token` em `POST /auth/refresh`
2. Obtenha um novo `access_token`
3. Continue usando a API

---

## Documentação Interativa

Para explorar todos os endpoints com exemplos de request/response:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## Próximo Passo

Consulte [Modelagem do Sistema](system-modeling.md) para entender a arquitetura e os diagramas do sistema.
