#!/usr/bin/env python3

"""
Teste rápido do ranking após as correções
"""

import requests
import json

BASE_URL = "http://localhost:8002"

def test_ranking():
    """Testa o endpoint de ranking"""
    print("🏆 TESTANDO ENDPOINT DE RANKING")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/ranking/weekly")
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            ranking = data.get("ranking", [])
            print(f"\n📊 RANKING:")
            for i, user in enumerate(ranking, 1):
                print(f"   {i}º lugar: {user.get('username')} - {user.get('points')} pontos")
                
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_ranking()
