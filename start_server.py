#!/usr/bin/env python3

import uvicorn
import sys
import os

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Tenta importar diretamente
try:
    from app.main import app
    print("✅ App importado com sucesso!")
    
    if __name__ == "__main__":
        print("🚀 Iniciando servidor...")
        uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
        
except Exception as e:
    print(f"❌ Erro ao importar app: {e}")
    sys.exit(1)
