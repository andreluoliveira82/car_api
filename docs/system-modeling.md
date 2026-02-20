# Modelagem do Sistema

Este documento apresenta a modelagem do **Car API** através de diagramas Mermaid, incluindo estrutura de dados, arquitetura geral e fluxos principais.

---

## Diagrama de Entidades (ERD)

```mermaid
erDiagram
    USER ||--o{ CAR : "possui"
    BRAND ||--o{ CAR : "classifica"

    USER {
        int id PK
        varchar username UK
        varchar full_name
        varchar email UK
        varchar password
        enum role "USER | ADMIN"
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    BRAND {
        int id PK
        varchar name UK
        text description
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    CAR {
        int id PK
        enum car_type
        varchar model
        int factory_year
        int model_year
        enum color
        enum fuel_type
        enum transmission
        enum condition
        enum status
        int mileage
        varchar plate UK
        decimal price
        text description
        int brand_id FK
        int owner_id FK
        datetime created_at
        datetime updated_at
    }
```

### Relacionamentos

| Relacionamento | Cardinalidade | Descrição |
|----------------|---------------|-----------|
| USER → CAR | 1:N | Um usuário pode possuir vários carros |
| BRAND → CAR | 1:N | Uma marca pode classificar vários carros |
| CAR → USER | N:1 | Cada carro pertence a um único usuário |
| CAR → BRAND | N:1 | Cada carro pertence a uma única marca |

### Integridade Referencial

- `CAR.brand_id` → `BRAND.id`: Cascade delete **desabilitado** (não excluir marca com carros)
- `CAR.owner_id` → `USER.id`: Cascade delete **habilitado** (carros são excluídos se usuário for removido)

---

## Arquitetura Geral do Sistema

```mermaid
flowchart TB
    subgraph Clientes
        WEB[Cliente Web]
        MOBILE[Cliente Mobile]
        THIRD[APIs de Terceiros]
    end

    subgraph "Car API"
        LB[Load Balancer / Proxy]
        
        subgraph "Camada de Apresentação"
            ROUTERS[Routers FastAPI]
            AUTH[Auth Router]
            USERS[Users Router]
            CARS[Cars Router]
            BRANDS[Brands Router]
            ADMIN[Admin Routers]
        end

        subgraph "Camada de Negócio"
            SECURITY[Security Module]
            VALIDATORS[Validators]
            SCHEMAS[Schemas Pydantic]
        end

        subgraph "Camada de Dados"
            ORM[SQLAlchemy Async ORM]
            MIGRATIONS[Alembic Migrations]
        end
    end

    subgraph Infraestrutura
        DB[(Banco de Dados)]
        ENV[Variáveis de Ambiente]
    end

    WEB --> LB
    MOBILE --> LB
    THIRD --> LB

    LB --> ROUTERS
    ROUTERS --> AUTH
    ROUTERS --> USERS
    ROUTERS --> CARS
    ROUTERS --> BRANDS
    ROUTERS --> ADMIN

    AUTH --> SECURITY
    USERS --> SECURITY
    CARS --> SECURITY
    ADMIN --> SECURITY

    ROUTERS --> SCHEMAS
    ROUTERS --> VALIDATORS

    ROUTERS --> ORM
    ORM --> DB

    SECURITY --> ENV
    ORM --> ENV
```

### Camadas da Arquitetura

| Camada | Componentes | Responsabilidade |
|--------|-------------|------------------|
| Apresentação | Routers | Receber requisições HTTP, validar schemas, retornar respostas |
| Negócio | Security, Validators | Autenticação, autorização, regras de domínio |
| Dados | ORM, Models, Migrations | Persistência e recuperação de dados |

---

## Fluxo de Autenticação

```mermaid
sequenceDiagram
    participant C as Cliente
    participant API as Car API
    participant DB as Banco de Dados
    participant JWT as Módulo JWT

    C->>API: POST /auth/login (email, password)
    API->>DB: SELECT user WHERE email = ?
    DB-->>API: User (hashed password)
    
    API->>API: verify_password(plain, hashed)
    
    alt Senha inválida ou usuário inativo
        API-->>C: 401 Unauthorized
    else Autenticação bem-sucedida
        API->>JWT: create_access_token(user.id, user.role)
        API->>JWT: create_refresh_token(user.id)
        JWT-->>API: access_token, refresh_token
        API-->>C: 200 OK (token pair)
    end

    Note over C,JWT: Uso da API com token
    C->>API: GET /cars/ (Authorization: Bearer token)
    API->>JWT: verify_token(token)
    JWT-->>API: payload (user.id, role, exp)
    API->>DB: SELECT user WHERE id = ?
    DB-->>API: User
    API-->>C: 200 OK (cars list)

    Note over C,JWT: Refresh de token expirado
    C->>API: POST /auth/refresh (refresh_token)
    API->>JWT: verify_token(refresh_token, type='refresh')
    JWT-->>API: payload (user.id)
    API->>DB: SELECT user WHERE id = ?
    DB-->>API: User ativo
    API->>JWT: create_access_token(user.id, user.role)
    JWT-->>API: new_access_token
    API-->>C: 200 OK (new access token)
```

### Componentes do Fluxo

| Etapa | Descrição |
|-------|-----------|
| Login | Valida credenciais e gera token pair |
| Acesso | Verifica token em cada requisição protegida |
| Refresh | Renova access token sem exigir nova autenticação |

---

## Fluxo CRUD de Carros

```mermaid
flowchart TD
    subgraph Criação
        C1[Cliente autenticado] --> C2[POST /cars/]
        C2 --> C3{Validar schema}
        C3 -->|Inválido| C4[400 Bad Request]
        C3 -->|Válido| C5{Marca existe?}
        C5 -->|Não| C4
        C5 -->|Sim| C6{Placa duplicada?}
        C6 -->|Sim| C4
        C6 -->|Não| C7[Salvar carro owner_id = user.id]
        C7 --> C8[201 Created]
    end

    subgraph Leitura
        L1[Cliente] --> L2{GET /cars/ ou /cars/{id}?}
        L2 -->|Lista| L3[GET /cars/?filters]
        L2 -->|Detalhe| L4[GET /cars/{id}]
        L3 --> L5[Aplicar filtros e paginação]
        L4 --> L6[Buscar carro + relações]
        L5 --> L7[200 OK cars list]
        L6 --> L8{Carro existe?}
        L8 -->|Não| L9[404 Not Found]
        L8 -->|Sim| L10[200 OK car detail]
    end

    subgraph Atualização
        U1[Cliente autenticado] --> U2[PUT /cars/{id}]
        U2 --> U3{Carro existe?}
        U3 -->|Não| U4[404 Not Found]
        U3 -->|Sim| U5{É proprietário?}
        U5 -->|Não| U6[403 Forbidden]
        U5 -->|Sim| U7{Placa alterada e duplicada?}
        U7 -->|Sim| U8[400 Bad Request]
        U7 -->|Não| U9[Aplicar atualizações]
        U9 --> U10[200 OK updated car]
    end

    subgraph Exclusão
        D1[Cliente autenticado] --> D2[DELETE /cars/{id}]
        D2 --> D3{Carro existe?}
        D3 -->|Não| D4[404 Not Found]
        D3 -->|Sim| D5{É proprietário?}
        D5 -->|Não| D6[403 Forbidden]
        D5 -->|Sim| D7[Excluir carro]
        D7 --> D8[204 No Content]
    end
```

### Regras de Negócio

| Operação | Regra |
|----------|-------|
| Criar | Marca deve existir, placa deve ser única, owner_id é o usuário autenticado |
| Listar | Público, com filtros e paginação |
| Obter | Público, inclui marca e proprietário |
| Atualizar | Apenas proprietário ou ADMIN |
| Excluir | Apenas proprietário ou ADMIN |

---

## Fluxo de Segurança e Controle de Acesso

```mermaid
flowchart TD
    R[Requisição HTTP] --> H{Endpoint requer auth?}
    
    H -->|Não| P[Processar normalmente]
    H -->|Sim| T{Token presente?}
    
    T -->|Não| E1[401 Unauthorized]
    T -->|Sim| V[Verificar token JWT]
    
    V --> V1{Token válido?}
    V1 -->|Não| E2[401 Unauthorized]
    V1 -->|Sim| V2{Token expirado?}
    V2 -->|Sim| E3[401 Token Expired]
    V2 -->|Não| V3[Extrair user.id do payload]
    
    V3 --> U[Buscar usuário no DB]
    U --> U1{Usuário existe e ativo?}
    U1 -->|Não| E4[401 Unauthorized]
    U1 -->|Sim| A[Usuário autenticado]
    
    A --> P{Endpoint requer ADMIN?}
    P -->|Não| O[Verificar ownership]
    P -->|Sim| AD{user.role == ADMIN?}
    
    AD -->|Não| E5[403 Forbidden]
    AD -->|Sim| X[Executar operação admin]
    
    O --> O1{Recurso pertence ao usuário?}
    O1 -->|Não| E6[403 Forbidden]
    O1 -->|Sim| Y[Executar operação]
    
    X --> Z[Retornar resposta]
    Y --> Z
    P --> Z
```

### Níveis de Acesso

| Nível | Descrição | Endpoints |
|-------|-----------|-----------|
| Público | Sem autenticação | Login, registro, listagem de carros/marcas |
| Autenticado | Token JWT válido | Perfil do usuário, CRUD de carros próprios |
| Admin | Token + role ADMIN | Gestão de usuários, carros e marcas |

### Validações de Segurança

1. **Token JWT**: Assinado com chave secreta, validação de expiração e tipo
2. **Usuário ativo**: Verificação de `is_active = true`
3. **Ownership**: Validação de propriedade de recursos
4. **Role-based access**: Verificação de papel para rotas administrativas

---

## Ciclo de Vida de um Carro

```mermaid
stateDiagram-v2
    [*] --> Rascunho: Criação
    Rascunho --> Disponível: Publicar
    Disponível --> Reservado: Reservar
    Disponível --> Indisponível: Tornar indisponível
    Disponível --> Vendido: Vender
    Disponível --> Manutenção: Enviar para manutenção
    Reservado --> Disponível: Cancelar reserva
    Reservado --> Vendido: Confirmar venda
    Indisponível --> Disponível: Reativar
    Manutenção --> Disponível: Manutenção concluída
    Vendido --> [*]: Arquivado
    
    note right of Disponível
        Estado padrão
        Visível nas listagens
    end note
    
    note right of Vendido
        Estado final
        Não pode ser alterado
    end note
```

### Estados do Carro

| Status | Descrição |
|--------|-----------|
| `available` | Carro disponível para venda |
| `unavailable` | Temporariamente indisponível |
| `sold` | Vendido (estado final) |
| `maintenance` | Em manutenção |
| `reserved` | Reservado por comprador |

---

## Hierarquia de Papéis (RBAC)

```mermaid
classDiagram
    class UserRole {
        <<enumeration>>
        USER
        ADMIN
    }

    class User {
        +int id
        +string username
        +string email
        +UserRole role
        +bool is_active
        +List~Car~ cars
    }

    class Car {
        +int id
        +string model
        +int owner_id
        +CarStatus status
    }

    User "1" -- "1" UserRole : possui
    User "1" -- "N" Car : possui

    note for User "ADMIN pode:\n- Gerenciar todos os usuários\n- Criar/editar/excluir qualquer carro\n- Gerenciar marcas\n\nUSER pode:\n- Gerenciar apenas seus carros\n- Atualizar próprio perfil"
```

### Permissões por Papel

| Permissão | USER | ADMIN |
|-----------|------|-------|
| Listar carros públicos | ✅ | ✅ |
| Criar carros próprios | ✅ | ✅ |
| Editar carros próprios | ✅ | ✅ |
| Excluir carros próprios | ✅ | ✅ |
| Listar todos os usuários | ❌ | ✅ |
| Ativar/desativar usuários | ❌ | ✅ |
| Alterar papel de usuário | ❌ | ✅ |
| Criar carros para terceiros | ❌ | ✅ |
| Editar qualquer carro | ❌ | ✅ |
| Excluir qualquer carro | ❌ | ✅ |
| Gerenciar marcas | ❌ | ✅ |

---

## Próximo Passo

Consulte [Autenticação e Segurança](authentication.md) para detalhes sobre o funcionamento do JWT e controle de acesso.
