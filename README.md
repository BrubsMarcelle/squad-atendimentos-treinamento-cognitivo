# Squad Atendimentos - Treinamento Cognitivo 🧠

Sistema de gamificação para check-ins diários com ranking semanal, desenvolvido para motivar e engajar equipes através de um sistema de pontuação dinâmico.

## 🏆 Características Principais

- **Sistema de Check-in Gamificado**: Pontuação diferenciada para primeiro checkin do dia e streaks
- **Ranking Semanal**: Competição saudável entre membros da equipe
- **Autenticação JWT**: Sistema seguro de autenticação com tokens
- **API REST Completa**: Endpoints bem documentados com Swagger
- **Clean Code**: Arquitetura modular e bem estruturada
- **Timezone Brasileiro**: Suporte nativo ao fuso horário de São Paulo (UTC-3)

## 🎯 Sistema de Pontuação

| Ação                            | Pontos | Descrição                              |
| --------------------------------- | ------ | ---------------------------------------- |
| **Primeiro Checkin do Dia** | 10 pts | Primeiro usuário a fazer checkin no dia |
| **Checkin Regular**         | 5 pts  | Checkins subsequentes no mesmo dia       |
| **Streak Bonus**            | +2 pts | Checkin em dias consecutivos             |

## 🚀 Instalação Rápida

### 🐳 Método Recomendado: Docker (Mais Fácil)

#### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+

#### Desenvolvimento

```bash
# 1. Clone o repositório
git clone https://github.com/BrubsMarcelle/squad-atendimentos-treinamento-cognitivo.git
cd squad-atendimentos-treinamento-cognitivo

# 2. Configure variáveis de ambiente
cp .env.example .env

# 3. Inicie todos os serviços
docker-compose --profile development up -d

# 4. Acesse a aplicação
# API: http://localhost:8002
# Mongo Express: http://localhost:8081 (admin/admin123)
```

#### Produção

```bash
# 1. Configure variáveis de produção
cp .env.prod.example .env
# Edite .env com valores seguros

# 2. Execute deploy
./scripts/deploy.sh  # Linux/Mac
scripts\deploy.bat   # Windows

# 3. Verifique funcionamento
curl http://localhost:8002/health
```

### 📚 Documentação Completa

Para instruções detalhadas sobre produção, monitoramento, backup e troubleshooting, consulte: **[PROD.md](./PROD.md)**

---

### 🛠️ Método Tradicional: Instalação Local

#### Pré-requisitos

- Python 3.8+
- MongoDB
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/BrubsMarcelle/squad-atendimentos-treinamento-cognitivo.git
cd squad-atendimentos-treinamento-cognitivo
```

### 2. Configurar ambiente virtual

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=squad_atendimentos
SECRET_KEY=sua_chave_secreta_super_segura_aqui
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Executar aplicação

```bash
python run_server.py
```

A API estará disponível em: `http://localhost:8002`

## 📚 Documentação da API

### Swagger UI

Acesse `http://localhost:8002/swagger` para documentação interativa completa.

### Autenticação

1. Clique em **"Authorize"** no Swagger
2. Use suas credenciais de usuário
3. O token será aplicado automaticamente

### Principais Endpoints

#### 🔐 Autenticação

- `POST /token` - Obter token JWT (para Swagger)
- `POST /login` - Login com JSON (para aplicações)
- `POST /users` - Criar novo usuário
- `GET /users` - Listar usuários
- `PUT /users/reset-password` - Reset de senha

#### ✅ Check-in

- `GET /checkin/status` - Verificar se pode fazer checkin hoje
- `POST /checkin/` - Realizar checkin

#### 🏆 Ranking

- `GET /ranking/weekly` - Ranking da semana atual
- `GET /ranking/my-status` - Status pessoal (recomendado para frontend)

#### 🛠️ Administração

- `GET /health` - Health check do sistema
- `POST /admin/fix-data` - Corrigir inconsistências

## 🏗️ Arquitetura do Projeto

```
squad-atendimentos-treinamento-cognitivo/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Configuração principal da aplicação
│   ├── auth.py                 # Sistema de autenticação JWT
│   ├── core/
│   │   └── config.py          # Configurações do sistema
│   ├── db/
│   │   └── database.py        # Conexão e operações de banco
│   ├── models/
│   │   ├── user.py           # Modelos de usuário
│   │   └── ranking.py        # Modelos de ranking
│   ├── routers/
│   │   ├── user_router.py    # Endpoints de usuários
│   │   ├── checkin_router.py # Endpoints de checkin
│   │   └── ranking_router.py # Endpoints de ranking
│   ├── services/
│   │   ├── checkin_service.py # Lógica de negócio (Clean Code)
│   │   └── logic.py          # Legacy service (compatibilidade)
│   ├── schemas/
│   │   └── responses.py      # DTOs para padronização de respostas
│   └── utils/
│       ├── constants.py      # Constantes do sistema
│       └── datetime_utils.py # Utilitários de data/hora
├── tests/                    # Testes automatizados
├── requirements.txt          # Dependências Python
├── run_server.py            # Script para executar servidor
└── README.md               # Esta documentação
```

## 🎮 Como Usar no Frontend

### Verificar Status do Usuário

```javascript
// Endpoint recomendado para controlar botão de checkin
const response = await fetch('/ranking/my-status', {
    headers: { 'Authorization': `Bearer ${token}` }
});
const status = await response.json();

// Controlar botão
button.disabled = !status.can_checkin;

// Exibir última data
if (status.last_checkin_formatted) {
    lastCheckinElement.textContent = `Último: ${status.last_checkin_formatted}`;
}
```

### Realizar Checkin

```javascript
// O endpoint já verifica tudo automaticamente
const response = await fetch('/checkin/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
});
const result = await response.json();

if (result.success) {
    showSuccess(`🎉 +${result.points_awarded} pontos!`);
    // Atualizar status do botão
    button.disabled = true;
} else {
    showInfo(result.message);
}
```

## 🔧 Funcionalidades Técnicas

### Sistema de Timezone

- **Timezone Fixo**: UTC-3 (São Paulo) sem horário de verão
- **Compatibilidade**: Funciona em Windows, Linux e Mac
- **Robustez**: Não depende de dados de timezone do sistema

### Otimizações de Performance

- **Login 60-80% mais rápido**: Projeções otimizadas e bcrypt tuned
- **Middleware Inteligente**: Logging detalhado apenas para endpoints críticos
- **Índices MongoDB**: Otimizados para consultas frequentes
- **Conexão Persistente**: Pool de conexões para melhor performance

### Segurança

- **JWT Tokens**: Autenticação stateless segura
- **Bcrypt**: Hash de senhas com 12 rounds
- **CORS Configurado**: Headers de segurança apropriados
- **Timing Attack Protection**: Prevenção de ataques de timing

### Clean Code Aplicado

- **Service Layer**: Lógica de negócio separada dos controllers
- **DTOs/Schemas**: Padronização de respostas da API
- **Constantes**: Eliminação de magic numbers e strings
- **Single Responsibility**: Cada classe/função tem uma responsabilidade
- **Dependency Injection**: Inversão de dependências com FastAPI

## 🧪 Testes

### Executar Testes

```bash
# Executar todos os testes
python -m pytest tests/

# Teste específico
python tests/test_login.py
```

### Tipos de Teste Disponíveis

- `test_login.py` - Testes de autenticação
- `test_login_performance.py` - Performance do login
- `test_ranking.py` - Sistema de ranking
- `test_timezone.py` - Manipulação de timezone

## 🔍 Monitoramento e Debug

### Health Check

```bash
curl http://localhost:8002/health
```

### Logs Detalhados

O sistema fornece logs detalhados para:

- Tentativas de login
- Processamento de checkins
- Atualizações de ranking
- Verificações de saúde do banco

### Correção Automática

O sistema verifica e corrige automaticamente:

- Inconsistências de username entre coleções
- Índices do banco de dados
- Saúde das conexões

## 🛠️ Desenvolvimento

### Estrutura de Branches

- `main` - Produção
- `develop` - Desenvolvimento
- `feature/*` - Novas funcionalidades

### Padrões de Código

- **PEP 8** - Style guide Python
- **Type Hints** - Tipagem em Python
- **Docstrings** - Documentação de funções
- **Clean Code** - Princípios de código limpo

### Contribuindo

1. Fork do projeto
2. Criar branch feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit das mudanças (`git commit -am 'Add nova funcionalidade'`)
4. Push da branch (`git push origin feature/nova-funcionalidade`)
5. Criar Pull Request

## 📦 Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **MongoDB** - Banco de dados NoSQL
- **Motor** - Driver assíncrono para MongoDB
- **JWT** - Autenticação baseada em tokens
- **Bcrypt** - Hash seguro de senhas
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI de alta performance

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
