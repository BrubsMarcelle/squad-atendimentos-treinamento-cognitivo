# 📚 **API Documentation - Squad Atendimentos Treinamento Cognitivo**

## 🌐 **Base URL**
```
http://localhost:8002
```

## 🔐 **Autenticação**
A API utiliza JWT (JSON Web Tokens) para autenticação. Inclua o token no header:
```
Authorization: Bearer <seu_token_jwt>
```

---

## 📋 **Endpoints**

### 🔑 **AUTENTICAÇÃO**

#### **1. POST /login** (JSON)
Endpoint principal de login que aceita dados JSON.

**Request:**
```http
POST /login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123@"
}
```

**Response Success (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1NDI1ODM0NX0.wugNx0VvGokn_FUqxElJ_iyxmLfJrsY_ZbdaPDdfxiA",
  "token_type": "bearer"
}
```

**Response Error (401):**
```json
{
  "detail": "Incorrect username or password"
}
```

**Response Error (422):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "username"],
      "msg": "Field required",
      "input": null
    },
    {
      "type": "missing", 
      "loc": ["body", "password"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

#### **2. POST /token** (OAuth2 Form Data)
Endpoint de token compatível com OAuth2 para integração com Swagger e aplicações que usam form data.

**Request:**
```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123@
```

**Response Success (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1NDI1ODM0NX0.wugNx0VvGokn_FUqxElJ_iyxmLfJrsY_ZbdaPDdfxiA",
  "token_type": "bearer"
}
```

**Response Error (401):**
```json
{
  "detail": "Incorrect username or password"
}
```

---

### 👥 **USUÁRIOS**

#### **3. POST /users**
Cria um novo usuário no sistema.

**Request:**
```http
POST /users
Content-Type: application/json

{
  "username": "novo_usuario",
  "password": "senha123",
  "full_name": "Nome Completo",
  "email": "usuario@email.com"
}
```

**Response Success (201):**
```json
{
  "message": "User created successfully",
  "username": "novo_usuario"
}
```

**Response Error (400):**
```json
{
  "detail": "Username already exists"
}
```

**Response Error (422):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "username"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

---

#### **4. GET /users**
Lista todos os usuários cadastrados (sem mostrar as senhas).

**Request:**
```http
GET /users
Authorization: Bearer <token>
```

**Response Success (200):**
```json
[
  {
    "username": "Bruna.Marcelle",
    "full_name": "",
    "email": ""
  },
  {
    "username": "Lucas.Serpa",
    "full_name": "",
    "email": ""
  },
  {
    "username": "admin",
    "full_name": "",
    "email": ""
  }
]
```

**Response Error (401):**
```json
{
  "detail": "Not authenticated"
}
```

---

### ✅ **CHECK-IN**

#### **5. GET /checkin/status**
Verifica se o usuário pode fazer checkin hoje e retorna informações do último checkin.

**Request:**
```http
GET /checkin/status
Authorization: Bearer <token>
```

**Response Success (200) - Pode fazer checkin:**
```json
{
  "can_checkin": true,
  "last_checkin_date": "2025-08-02",
  "last_checkin_formatted": "02/08/2025",
  "is_weekend": false,
  "already_checked_today": false,
  "reason": "available",
  "message": "Você pode fazer checkin agora",
  "today": "2025-08-03"
}
```

**Response Success (200) - Final de semana:**
```json
{
  "can_checkin": false,
  "last_checkin_date": null,
  "last_checkin_formatted": null,
  "is_weekend": true,
  "already_checked_today": false,
  "reason": "Hoje é final de semana",
  "message": "Check-ins são permitidos apenas de Segunda a Sexta",
  "today": "2025-08-03"
}
```

**Response Success (200) - Já fez checkin hoje:**
```json
{
  "can_checkin": false,
  "reason": "Checkin já realizado hoje",
  "message": "Você já fez checkin hoje às 09:30",
  "today": "2025-08-03",
  "is_weekend": false,
  "already_checked_today": true,
  "last_checkin_date": "2025-08-03",
  "last_checkin_formatted": "03/08/2025"
}
```

**Response Success (200) - Erro interno:**
```json
{
  "can_checkin": false,
  "reason": "Erro interno",
  "message": "Ocorreu um erro ao verificar o status. Tente novamente.",
  "today": "2025-08-03",
  "is_weekend": false,
  "already_checked_today": false,
  "last_checkin_date": null,
  "last_checkin_formatted": null
}
```

**Response Error (401):**
```json
{
  "detail": "Not authenticated"
}
```

---

#### **6. POST /checkin**
Realiza o check-in do usuário autenticado.

**Request:**
```http
POST /checkin
Authorization: Bearer <token>
Content-Type: application/json

{}
```
*(Corpo vazio)*

**Response Success (200):**
```json
{
  "message": "Check-in realizado com sucesso!",
  "timestamp": "2025-08-03T09:30:00",
  "points_earned": 10,
  "total_points": 150
}
```

**Response Error (400) - Final de semana:**
```json
{
  "detail": "Check-ins são permitidos apenas de Segunda a Sexta"
}
```

**Response Error (409) - Já fez checkin:**
```json
{
  "detail": "Usuário já realizou check-in hoje às 09:30"
}
```

**Response Error (401):**
```json
{
  "detail": "Not authenticated"
}
```

---

### 🏆 **RANKING**

#### **7. GET /ranking/weekly**
Retorna o ranking da semana atual, ordenado por pontos.

**Request:**
```http
GET /ranking/weekly
Authorization: Bearer <token>
```

**Response Success (200):**
```json
{
  "week_id": "2025-W31",
  "ranking": [
    {
      "username": "Bruna.Marcelle",
      "points": 10
    },
    {
      "username": "Lucas.Serpa",
      "points": 5
    }
  ]
}
```

**Response Error (401):**
```json
{
  "detail": "Not authenticated"
}
```

**Response Error (500):**
```json
{
  "detail": "Falha ao consultar ranking semanal"
}
```

---

#### **8. GET /ranking/my-status**
Retorna status simplificado do usuário para o frontend.

**Request:**
```http
GET /ranking/my-status
Authorization: Bearer <token>
```

**Response Success (200) - Final de semana:**
```json
{
  "can_checkin": false,
  "last_checkin_date": null,
  "last_checkin_formatted": null,
  "is_weekend": true,
  "already_checked_today": false,
  "reason": "weekend",
  "message": "Fim de semana",
  "today": "03/08/2025"
}
```

**Response Success (200) - Pode fazer checkin:**
```json
{
  "can_checkin": true,
  "last_checkin_date": "2025-08-02",
  "last_checkin_formatted": "02/08/2025",
  "is_weekend": false,
  "already_checked_today": false,
  "reason": "available",
  "message": "Você pode fazer checkin agora",
  "today": "03/08/2025"
}
```

**Response Success (200) - Já fez checkin:**
```json
{
  "can_checkin": false,
  "last_checkin_date": "2025-08-03",
  "last_checkin_formatted": "03/08/2025",
  "is_weekend": false,
  "already_checked_today": true,
  "reason": "already_checked",
  "message": "Já fez checkin hoje",
  "today": "03/08/2025"
}
```

**Response Error (401):**
```json
{
  "detail": "Not authenticated"
}
```

**Response Error (500):**
```json
{
  "detail": "Falha ao consultar status do usuário"
}
```

---

#### **9. GET /ranking/all-time**
Retorna o ranking geral de todos os tempos.

**Request:**
```http
GET /ranking/all-time
Authorization: Bearer <token>
```

**Response Success (200):**
```json
{
  "type": "all_time",
  "date": "2025-08-03",
  "total_participants": 2,
  "ranking": [
    {
      "username": "Bruna.Marcelle",
      "points": 10
    },
    {
      "username": "Lucas.Serpa",
      "points": 5
    }
  ],
  "user_position": null
}
```

**Response Error (401):**
```json
{
  "detail": "Not authenticated"
}
```

---

## 🚨 **Códigos de Status HTTP**

| Código | Significado | Descrição |
|--------|-------------|-----------|
| **200** | OK | Requisição bem-sucedida |
| **201** | Created | Recurso criado com sucesso |
| **400** | Bad Request | Dados da requisição inválidos |
| **401** | Unauthorized | Token de autenticação inválido ou ausente |
| **404** | Not Found | Endpoint não encontrado |
| **409** | Conflict | Conflito (ex: usuário já existe, checkin duplicado) |
| **422** | Unprocessable Entity | Dados da requisição mal formados |
| **500** | Internal Server Error | Erro interno do servidor |

---

## 📝 **Modelos de Dados**

### **LoginRequest**
```json
{
  "username": "string",
  "password": "string"
}
```

### **UserCreate** 
```json
{
  "username": "string",
  "password": "string", 
  "full_name": "string",
  "email": "string"
}
```

### **Token**
```json
{
  "access_token": "string",
  "token_type": "string"
}
```

### **UserResponse**
```json
{
  "username": "string",
  "full_name": "string", 
  "email": "string"
}
```

### **CheckinStatusResponse**
```json
{
  "can_checkin": "boolean",
  "last_checkin_date": "string | null",
  "last_checkin_formatted": "string | null",
  "is_weekend": "boolean",
  "already_checked_today": "boolean",
  "reason": "string",
  "message": "string",
  "today": "string"
}
```

### **CheckinResponse**
```json
{
  "message": "string",
  "timestamp": "string",
  "points_earned": "number",
  "total_points": "number"
}
```

### **RankingEntry**
```json
{
  "username": "string",
  "points": "number"
}
```

### **WeeklyRankingResponse**
```json
{
  "week_id": "string",
  "ranking": ["RankingEntry"]
}
```

### **AllTimeRankingResponse**
```json
{
  "type": "string",
  "date": "string", 
  "total_participants": "number",
  "ranking": ["RankingEntry"],
  "user_position": "number | null"
}
```

---

## 🔧 **Configurações**

### **Headers Obrigatórios**
- **Content-Type**: `application/json` (para endpoints JSON)
- **Content-Type**: `application/x-www-form-urlencoded` (para OAuth2)
- **Authorization**: `Bearer <token>` (para endpoints autenticados)

### **CORS**
A API permite requisições de qualquer origem para desenvolvimento.

### **Rate Limiting**
Não há limitação de taxa implementada atualmente.

---

## 📊 **Exemplos de Uso**

### **Fluxo Completo de Autenticação e Checkin**

1. **Login:**
```bash
curl -X POST http://localhost:8002/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123@"}'
```

2. **Verificar Status:**
```bash
curl -X GET http://localhost:8002/checkin/status \
  -H "Authorization: Bearer <seu_token>"
```

3. **Fazer Checkin:**
```bash
curl -X POST http://localhost:8002/checkin \
  -H "Authorization: Bearer <seu_token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

4. **Ver Ranking:**
```bash
curl -X GET http://localhost:8002/ranking/weekly \
  -H "Authorization: Bearer <seu_token>"
```

---

## ⚠️ **Observações Importantes**

1. **Endpoint Inexistente**: O frontend pode estar tentando acessar `/checkin/history` que **não existe** e retorna 404.

2. **Encoding**: Algumas respostas podem ter problemas de encoding (Ã© em vez de é). Isso pode ser resolvido configurando UTF-8 no frontend.

3. **Tokens JWT**: Os tokens têm expiração. Verifique se o frontend está tratando tokens expirados adequadamente.

4. **Final de Semana**: Checkins são bloqueados aos fins de semana, mas retornam status 200 com `can_checkin: false`.

5. **Logs**: O servidor registra todas as requisições de autenticação e operações importantes nos logs.

---

## 🐛 **Troubleshooting**

### **Problema: Loading infinito no ranking**
- **Causa**: Frontend tentando acessar `/checkin/history` (404)
- **Solução**: Remover chamada para endpoint inexistente

### **Problema: Caracteres especiais**
- **Causa**: Encoding UTF-8
- **Solução**: Configurar charset=utf-8 no frontend

### **Problema: Token inválido**
- **Causa**: Token expirado ou malformado
- **Solução**: Renovar token via login

### **Problema: 422 no login**
- **Causa**: Enviando form data para endpoint JSON ou vice-versa
- **Solução**: Usar `/login` para JSON e `/token` para form data

---

*Documentação gerada em: 3 de agosto de 2025*
