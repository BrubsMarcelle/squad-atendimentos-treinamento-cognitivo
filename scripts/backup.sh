#!/bin/bash

# Script para backup do MongoDB
# Execute: ./scripts/backup.sh

set -e

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="squad-mongodb-prod"
DATABASE_NAME="squad_treinamento_prod"

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

echo "🔄 Iniciando backup do MongoDB..."
echo "📅 Data: $(date)"

# Executar mongodump dentro do container
docker exec $CONTAINER_NAME mongodump \
    --db $DATABASE_NAME \
    --out /backups/backup_$DATE \
    --authenticationDatabase admin \
    --username $MONGO_ROOT_USERNAME \
    --password $MONGO_ROOT_PASSWORD

# Copiar backup do container para o host
docker cp $CONTAINER_NAME:/backups/backup_$DATE $BACKUP_DIR/

echo "✅ Backup concluído!"
echo "📁 Localização: $BACKUP_DIR/backup_$DATE"

# Manter apenas os últimos 7 backups
echo "🧹 Limpando backups antigos..."
ls -t $BACKUP_DIR/ | tail -n +8 | xargs -r rm -rf

echo "🎉 Processo de backup finalizado!"
