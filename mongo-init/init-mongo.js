// Script de inicialização do MongoDB
// Este script será executado quando o container MongoDB for criado pela primeira vez

// Selecionar ou criar o banco de dados
db = db.getSiblingDB('squad_treinamento');

// Criar usuário específico para a aplicação (se necessário)
db.createUser({
  user: 'app_user',
  pwd: 'app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'squad_treinamento'
    }
  ]
});

// Criar índices para melhor performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": 1 });

db.checkins.createIndex({ "user_id": 1 });
db.checkins.createIndex({ "date": 1 });
db.checkins.createIndex({ "user_id": 1, "date": 1 });

db.weekly_rankings.createIndex({ "week_start": 1 });
db.weekly_rankings.createIndex({ "week_start": 1, "user_id": 1 });

print('Database initialized successfully!');
