#!/usr/bin/env python3

import requests
import json

# Configuração do servidor
BASE_URL = "http://localhost:8002"

def test_endpoint(method, endpoint, data=None, headers=None, is_json=True):
    """Testa um endpoint e mostra resultado detalhado"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🧪 TESTANDO: {method} {url}")
    
    if headers:
        print(f"   📄 Headers: {headers}")
    if data:
        print(f"   📦 Data: {data}")
    
    try:
        if method == "POST":
            if is_json:
                response = requests.post(url, json=data, headers=headers)
            else:
                response = requests.post(url, data=data, headers=headers)
        elif method == "GET":
            response = requests.get(url, headers=headers)
        
        print(f"   📊 Status Code: {response.status_code}")
        print(f"   📝 Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"   ✅ Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"   📄 Response Text: {response.text}")
            
        return response
        
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
        return None

def main():
    print("🚀 INICIANDO TESTES DOS ENDPOINTS DE LOGIN")
    
    # Dados de teste
    test_user = {
        "username": "testuser",
        "password": "testpass"
    }
    
    # Teste 1: Login via JSON no endpoint /login
    print("\n" + "="*60)
    print("📋 TESTE 1: POST /login (JSON)")
    response1 = test_endpoint(
        "POST", 
        "/login", 
        data=test_user,
        headers={"Content-Type": "application/json"}
    )
    
    # Teste 2: Login via JSON no endpoint /token  
    print("\n" + "="*60)
    print("📋 TESTE 2: POST /token (JSON)")
    response2 = test_endpoint(
        "POST", 
        "/token", 
        data=test_user,
        headers={"Content-Type": "application/json"}
    )
    
    # Teste 3: Login via form-data no endpoint /token
    print("\n" + "="*60)
    print("📋 TESTE 3: POST /token (Form-Data)")
    response3 = test_endpoint(
        "POST", 
        "/token", 
        data=test_user,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        is_json=False
    )
    
    # Teste 4: Listar usuários (sem auth)
    print("\n" + "="*60)
    print("📋 TESTE 4: GET /users")
    response4 = test_endpoint("GET", "/users")
    
    # Se conseguiu um token, teste endpoint protegido
    token = None
    for resp in [response1, response2, response3]:
        if resp and resp.status_code == 200:
            try:
                token_data = resp.json()
                token = token_data.get("access_token")
                if token:
                    break
            except:
                pass
    
    if token:
        print("\n" + "="*60)
        print("📋 TESTE 5: POST /checkin (com token)")
        test_endpoint(
            "POST", 
            "/checkin/", 
            headers={"Authorization": f"Bearer {token}"}
        )
    else:
        print("\n❌ Nenhum token válido obtido - não foi possível testar endpoint protegido")
    
    print("\n🏁 TESTES CONCLUÍDOS")

if __name__ == "__main__":
    main()
