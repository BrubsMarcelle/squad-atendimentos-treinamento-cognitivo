#!/usr/bin/env python3

import requests
import json
import time
import statistics

# Configuração do servidor
BASE_URL = "http://localhost:8002"

def test_login_performance(endpoint, data, headers=None, iterations=10):
    """Testa performance do endpoint de login"""
    url = f"{BASE_URL}{endpoint}"
    times = []
    
    print(f"\n🚀 TESTANDO PERFORMANCE: {endpoint}")
    print(f"   📊 Realizando {iterations} tentativas...")
    
    for i in range(iterations):
        start_time = time.time()
        
        try:
            response = requests.post(url, json=data, headers=headers)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # em ms
            times.append(response_time)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {i+1:2d}. {status} {response.status_code} - {response_time:.0f}ms")
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            times.append(response_time)
            print(f"   {i+1:2d}. ❌ ERRO - {response_time:.0f}ms - {e}")
    
    # Estatísticas
    if times:
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        
        print(f"\n📈 ESTATÍSTICAS DE PERFORMANCE:")
        print(f"   ⏱️  Tempo médio: {avg_time:.0f}ms")
        print(f"   🚀 Mais rápido: {min_time:.0f}ms")
        print(f"   🐌 Mais lento: {max_time:.0f}ms")
        print(f"   📊 Mediana: {median_time:.0f}ms")
        
        return {
            "avg": avg_time,
            "min": min_time,
            "max": max_time,
            "median": median_time
        }
    
    return None

def create_test_user():
    """Cria um usuário de teste se não existir"""
    test_user = {
        "username": "perftest",
        "password": "testpass123",
        "full_name": "Performance Test User",
        "email": "perftest@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users", json=test_user)
        if response.status_code == 201:
            print("✅ Usuário de teste criado com sucesso")
        elif response.status_code == 400:
            print("ℹ️  Usuário de teste já existe")
        else:
            print(f"⚠️ Resposta inesperada ao criar usuário: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao criar usuário de teste: {e}")

def main():
    print("🔬 TESTE DE PERFORMANCE DO LOGIN")
    print("=" * 50)
    
    # Criar usuário de teste
    create_test_user()
    
    # Dados de login
    login_data = {
        "username": "perftest",
        "password": "testpass123"
    }
    
    # Testar endpoint /login
    print(f"\n🎯 TESTANDO ENDPOINT /login")
    login_stats = test_login_performance("/login", login_data, iterations=10)
    
    # Resultados
    if login_stats:
        print(f"\n📊 RESULTADO FINAL:")
        print(f"   🎯 /login - Tempo médio: {login_stats['avg']:.0f}ms")
        print(f"   🚀 Mais rápido: {login_stats['min']:.0f}ms")
        print(f"   🐌 Mais lento: {login_stats['max']:.0f}ms")
        print(f"   📊 Mediana: {login_stats['median']:.0f}ms")
    
    print(f"\n✅ TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
