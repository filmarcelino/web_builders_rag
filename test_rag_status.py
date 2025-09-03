#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo do status do RAG online
"""

import requests
import json
import time
from datetime import datetime

class RAGTester:
    def __init__(self):
        self.base_url = "https://web-builders-rag.onrender.com"
        self.session = requests.Session()
        self.session.timeout = 30
    
    def health_check(self):
        """Verifica se o serviço está online"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Serviço ONLINE - Status: {data.get('status', 'unknown')}")
                print(f"   Componentes: {data.get('components', {})}")
                return True
            else:
                print(f"❌ Serviço com problemas - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False
    
    def test_search(self, query, search_type="hybrid", top_k=5):
        """Testa uma busca específica"""
        payload = {
            "query": query,
            "top_k": top_k,
            "search_type": search_type,
            "include_rationale": True
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/search",
                json=payload
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get('total', 0)
                items = data.get('items', [])
                search_time = round((end_time - start_time) * 1000, 2)
                
                print(f"🔍 Query: '{query}' ({search_type})")
                print(f"   Resultados: {total_results} em {search_time}ms")
                
                if total_results > 0:
                    print(f"   ✅ DADOS ENCONTRADOS!")
                    for i, item in enumerate(items[:2], 1):
                        print(f"   [{i}] Score: {item.get('score', 'N/A')}")
                        print(f"       Fonte: {item.get('fonte', {}).get('title', 'N/A')}")
                        content = item.get('chunk', '')[:100]
                        print(f"       Conteúdo: {content}...")
                else:
                    print(f"   ⚠️  Nenhum resultado (indexação em andamento)")
                
                return data
            else:
                print(f"❌ Erro na busca: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return None
    
    def comprehensive_test(self):
        """Teste completo do RAG"""
        print("="*60)
        print(f"🧪 TESTE COMPLETO DO RAG - {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        # 1. Health Check
        print("\n1️⃣ Verificando Status do Serviço...")
        if not self.health_check():
            print("❌ Serviço offline - abortando testes")
            return
        
        # 2. Testes de busca variados
        print("\n2️⃣ Testando Diferentes Tipos de Busca...")
        
        queries_test = [
            ("React hooks", "hybrid"),
            ("JavaScript", "vector"),
            ("Python", "text"),
            ("HTML CSS", "hybrid"),
            ("Node.js", "vector"),
            ("database", "text"),
            ("API REST", "hybrid"),
            ("frontend", "vector"),
            ("backend", "text"),
            ("web development", "hybrid")
        ]
        
        results_found = 0
        total_tests = len(queries_test)
        
        for query, search_type in queries_test:
            result = self.test_search(query, search_type, top_k=3)
            if result and result.get('total', 0) > 0:
                results_found += 1
            time.sleep(0.5)  # Evitar rate limiting
        
        # 3. Resumo
        print("\n3️⃣ Resumo dos Testes")
        print("="*40)
        print(f"📊 Testes realizados: {total_tests}")
        print(f"✅ Buscas com resultados: {results_found}")
        print(f"⚠️  Buscas sem resultados: {total_tests - results_found}")
        
        if results_found > 0:
            print(f"\n🎉 RAG FUNCIONANDO! {results_found}/{total_tests} buscas retornaram dados")
            print("✅ O sistema está indexado e operacional")
        else:
            print(f"\n⚠️  RAG ONLINE mas SEM DADOS")
            print("🔄 Indexação ainda em andamento")
            print("⏳ Aguarde alguns minutos e teste novamente")
        
        print(f"\n🔗 URL do RAG: {self.base_url}")
        print("="*60)

if __name__ == "__main__":
    tester = RAGTester()
    tester.comprehensive_test()