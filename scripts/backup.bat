@echo off
REM Script para backup do MongoDB no Windows
REM Execute: scripts\backup.bat

setlocal

set BACKUP_DIR=.\backups
set CONTAINER_NAME=squad-mongodb-prod
set DATABASE_NAME=squad_treinamento_prod

REM Obter data e hora atual
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set DATE=%datetime:~0,8%_%datetime:~8,6%

REM Criar diretório de backup se não existir
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

echo 🔄 Iniciando backup do MongoDB...
echo 📅 Data: %date% %time%

REM Executar mongodump dentro do container
docker exec %CONTAINER_NAME% mongodump ^
    --db %DATABASE_NAME% ^
    --out /backups/backup_%DATE% ^
    --authenticationDatabase admin ^
    --username %MONGO_ROOT_USERNAME% ^
    --password %MONGO_ROOT_PASSWORD%

REM Copiar backup do container para o host
docker cp %CONTAINER_NAME%:/backups/backup_%DATE% %BACKUP_DIR%\

echo ✅ Backup concluído!
echo 📁 Localização: %BACKUP_DIR%\backup_%DATE%
echo 🎉 Processo de backup finalizado!

pause
