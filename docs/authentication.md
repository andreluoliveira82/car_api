# Autenticação e Segurança

Este documento descreve o funcionamento da autenticação JWT, controle de acesso por papel (RBAC) e validações de segurança implementadas no **Car API**.

---

## Visão Geral

O sistema utiliza **JWT (JSON Web Tokens)** para autenticação stateless, combinado com **RBAC (Role-Based Access Control)** para autorização.

**Componentes principais:**

- **Access Token**: Token de curta duração para acesso à API
- **Refresh Token**: Token de longa duração para renovar o access token
- **Papeis**: `USER` e `ADMIN`
- **Ownership**: Validação de propriedade de recursos

---

## JWT (JSON Web Tokens)

### Estrutura do Token

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwicm9sZSI6InVzZXIiLCJleHAiOjE1MTYyMzkwMjJ9.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

| Parte | Descrição |
|-------|-----------|
| Header | Algoritmo e tipo de token |
| Payload | Dados do usuário (sub, role, exp, iat, type) |
| Signature | Assinatura HMAC-SHA256 |

### Payload do Access Token

```json
{
  "sub": "1",
  "role": "user",
  "exp": 1708456789,
  "iat": 1708454989,
  "type": "access"
}
```

| Claim | Descrição |
|-------|-----------|
| `sub` | ID do usuário (subject) |
| `role` | Papel do usuário (`user` ou `admin`) |
| `exp` | Timestamp de expiração |
| `iat` | Timestamp de emissão |
| `type` | Tipo de token (`access` ou `refresh`) |

### Payload do Refresh Token

```json
{
  "sub": "1",
  "exp": 1708541389,
  "iat": 1708454989,
  "type": "refresh"
}
```

**Diferenças:**

- Não inclui `role` (não necessário para refresh)
- `type` = `refresh`
- Expiração mais longa (1 dia vs 30 minutos)

---

## Fluxo de Autenticação

### 1. Login

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Senha123"
}
```

**Processo:**

1. Busca usuário pelo email no banco de dados
2. Verifica se usuário existe e está ativo
3. Valida senha com hash Argon2
4. Gera access token e refresh token
5. Retorna token pair

**Resposta de sucesso:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Respostas de erro:**

| Código | Motivo |
|--------|--------|
| `401 Unauthorized` | Email ou senha inválidos |

---

### 2. Acesso a Endpoints Protegidos

```bash
GET /api/v1/cars/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Processo:**

1. Extrai token do header `Authorization`
2. Verifica assinatura JWT
3. Valida expiração
4. Verifica tipo do token (`access`)
5. Busca usuário no banco de dados pelo `sub`
6. Verifica se usuário está ativo
7. Injeta `current_user` no endpoint

**Respostas de erro:**

| Código | Motivo |
|--------|--------|
| `401 Unauthorized` | Token ausente |
| `401 Unauthorized` | Token inválido |
| `401 Unauthorized` | Token expirado |
| `401 Unauthorized` | Usuário inativo ou não encontrado |

---

### 3. Refresh de Token

```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Processo:**

1. Verifica assinatura do refresh token
2. Valida tipo do token (`refresh`)
3. Verifica expiração
4. Busca usuário no banco de dados
5. Gera novo access token com o mesmo role
6. Retorna novo access token

**Resposta de sucesso:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Importante:**

- O refresh token **não é rotacionado** (mesmo token pode ser usado múltiplas vezes até expirar)
- Não há blacklist de tokens (logout é feito apenas descartando tokens no cliente)

---

## Controle de Acesso por Papel (RBAC)

### Papeis Disponíveis

| Papel | Descrição |
|-------|-----------|
| `USER` | Usuário padrão, acesso limitado aos próprios recursos |
| `ADMIN` | Administrador, acesso total ao sistema |

### Atribuição de Papel

- **Registro**: Novo usuário recebe papel `USER` automaticamente
- **Elevação**: Apenas ADMIN pode alterar papel de usuário via `/admin/users/{id}/role`

### Verificação de Papel

```python
# car_api/core/security.py
def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Acesso restrito a administradores.',
        )
    return current_user
```

**Uso em endpoints:**

```python
@router.get('/admin/users/')
async def list_users(admin: User = Depends(require_admin), ...):
    # Apenas ADMIN acessa este endpoint
```

---

## Validação de Ownership

### Conceito

Ownership (propriedade) garante que usuários só possam modificar ou excluir recursos que possuem.

### Implementação

```python
# car_api/core/security.py
def verify_car_ownership(current_user: User, car_owner_id: int) -> None:
    if current_user.id != car_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Permissões insuficientes para acessar este carro.',
        )
```

**Uso em endpoints:**

```python
@router.put('/cars/{car_id}')
async def update_car(
    car_id: int,
    car_data: CarUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    db_car = await db.get(Car, car_id)
    
    # Valida ownership
    verify_car_ownership(current_user, db_car.owner_id)
    
    # Prossegue com atualização
```

### Comportamento por Papel

| Operação | USER (dono) | USER (não-dono) | ADMIN |
|----------|-------------|-----------------|-------|
| Ver carro | ✅ | ✅ | ✅ |
| Editar carro | ✅ | ❌ (403) | ✅ (via rotas administrativas) |
| Excluir carro | ✅ | ❌ (403) | ✅ |

---

## Hash de Senhas

### Algoritmo

O projeto utiliza **Argon2** (via `pwdlib`), recomendado pelo OWASP para armazenamento de senhas.

### Implementação

```python
# car_api/core/security.py
from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Validações de Senha

| Regra | Descrição |
|-------|-----------|
| Mínimo 6 caracteres | Evita senhas muito curtas |
| Máximo 15 caracteres | Limite superior (pode ser ajustado) |
| Pelo menos 1 número | Exige caractere numérico |
| Pelo menos 1 letra | Exige caractere alfabético |

---

## Configurações de Segurança

### Variáveis de Ambiente

```env
JWT_SECRET_KEY=sua-chave-secreta-forte-aqui
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
JWT_REFRESH_EXPIRATION_DAYS=1
```

### Recomendações de Produção

| Configuração | Desenvolvimento | Produção |
|--------------|-----------------|----------|
| `JWT_SECRET_KEY` | Chave simples | Mínimo 32 bytes aleatórios |
| `JWT_EXPIRATION_MINUTES` | 60 | 15-30 |
| `JWT_REFRESH_EXPIRATION_DAYS` | 7 | 1-3 |
| `JWT_ALGORITHM` | HS256 | HS256 ou RS256 |

### Geração de Chave Segura

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Considerações de Segurança

### Tokens

1. **Nunca armazenar tokens no localStorage** (preferir httpOnly cookies em produção)
2. **Usar HTTPS** em produção (tokens trafegam em claro no HTTP)
3. **Implementar logout** descartando tokens no cliente
4. **Considerar blacklist** para logout antecipado (requer armazenamento)

### Senhas

1. **Nunca logar senhas** em produção
2. **Exigir complexidade mínima** (implementado)
3. **Considerar rate limiting** no endpoint de login
4. **Considerar 2FA** para administradores

### Controle de Acesso

1. **Sempre validar ownership** em operações de escrita
2. **Usar require_admin** apenas quando necessário
3. **Logar tentativas de acesso não autorizado** (auditoria)

---

## Tratamento de Erros de Autenticação

### Códigos HTTP

| Código | Cenário |
|--------|---------|
| `401 Unauthorized` | Token ausente, inválido ou expirado |
| `403 Forbidden` | Permissão insuficiente (role ou ownership) |

### Headers de Erro

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer
Content-Type: application/json

{
  "detail": "Token has expired"
}
```

---

## Exemplo Completo: Fluxo no Cliente

```javascript
// 1. Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'Senha123' })
});

const { access_token, refresh_token } = await loginResponse.json();

// 2. Armazenar tokens (em produção, usar httpOnly cookie)
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);

// 3. Fazer requisição autenticada
const carsResponse = await fetch('/api/v1/cars/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});

// 4. Lidar com token expirado
if (carsResponse.status === 401) {
  // Tentar refresh
  const refreshResponse = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token })
  });
  
  const { access_token: newToken } = await refreshResponse.json();
  localStorage.setItem('access_token', newToken);
  
  // Refazer requisição original
}
```

---

## Próximo Passo

Consulte [Desenvolvimento](development.md) para informações sobre como contribuir com o projeto.
