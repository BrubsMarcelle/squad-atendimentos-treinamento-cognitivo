@echo off
REM Script para deploy em produção no Windows
REM Execute: scripts\deploy.bat

echo 🚀 Iniciando deploy em produção...

REM Verificar se o arquivo .env existe
if not exist .env (
    echo ❌ Arquivo .env não encontrado!
    echo 📝 Copie .env.prod.example para .env e configure as variáveis
    pause
    exit /b 1
)

REM Parar containers existentes
echo ⏹️ Parando containers existentes...
docker-compose -f docker-compose.prod.yml down

REM Remover imagens antigas (opcional)
echo 🧹 Removendo imagens antigas...
docker image prune -f

REM Construir nova imagem
echo 🔨 Construindo nova imagem...
docker-compose -f docker-compose.prod.yml build --no-cache

REM Iniciar serviços
echo ▶️ Iniciando serviços...
docker-compose -f docker-compose.prod.yml up -d

REM Aguardar serviços ficarem prontos
echo ⏳ Aguardando serviços ficarem prontos...
timeout /t 30 /nobreak > nul

REM Verificar status dos containers
echo 📊 Status dos containers:
docker-compose -f docker-compose.prod.yml ps

echo 🎉 Deploy concluído!
echo 🌐 Aplicação disponível em: http://localhost:8002

pause
