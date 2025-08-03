#!/bin/bash

# Script para deploy em produção
# Execute: ./scripts/deploy.sh

set -e

echo "🚀 Iniciando deploy em produção..."

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "📝 Copie .env.prod.example para .env e configure as variáveis"
    exit 1
fi

# Parar containers existentes
echo "⏹️ Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down

# Remover imagens antigas (opcional)
echo "🧹 Removendo imagens antigas..."
docker image prune -f

# Construir nova imagem
echo "🔨 Construindo nova imagem..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Iniciar serviços
echo "▶️ Iniciando serviços..."
docker-compose -f docker-compose.prod.yml up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status dos containers
echo "📊 Status dos containers:"
docker-compose -f docker-compose.prod.yml ps

# Verificar health check da aplicação
echo "🏥 Verificando saúde da aplicação..."
if curl -f http://localhost:8002/health > /dev/null 2>&1; then
    echo "✅ Aplicação está funcionando!"
else
    echo "❌ Aplicação não está respondendo!"
    echo "📋 Logs da aplicação:"
    docker-compose -f docker-compose.prod.yml logs fastapi-app
    exit 1
fi

echo "🎉 Deploy concluído com sucesso!"
echo "🌐 Aplicação disponível em: http://localhost:8002"
