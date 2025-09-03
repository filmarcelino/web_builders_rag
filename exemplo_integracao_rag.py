#!/usr/bin/env python3
"""
Exemplo Prático de Integração com RAG
URL: https://web-builders-rag.onrender.com

Este exemplo demonstra como conectar uma aplicação Python ao RAG
para buscar informações sobre desenvolvimento web.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RAGResult:
    """Estrutura de um resultado do RAG"""
    chunk: str
    score: float
    fonte: Dict[str, Any]
    licenca: str
    rationale: Optional[str] = None

class RAGClient:
    """Cliente para integração com o RAG Web Builders"""
    
    def __init__(self, base_url: str = "https://web-builders-rag.onrender.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'RAG-Client/1.0'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica se o serviço RAG está funcionando"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro no health check: {e}")
            return {"status": "error", "message": str(e)}
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        search_type: str = "hybrid",
        include_rationale: bool = True,
        filtros: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Realiza busca no RAG"""
        
        payload = {
            "query": query,
            "top_k": top_k,
            "search_type": search_type,
            "include_rationale": include_rationale
        }
        
        if filtros:
            payload["filtros"] = filtros
        
        try:
            print(f"🔍 Buscando: '{query}'...")
            response = self.session.post(
                f"{self.base_url}/search", 
                json=payload, 
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Encontrados {data.get('total_results', 0)} resultados em {data.get('search_time_ms', 0)}ms")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na busca: {e}")
            return None
    
    def search_with_context(self, query: str, context: str) -> Optional[Dict[str, Any]]:
        """Busca com contexto específico"""
        enhanced_query = f"Contexto: {context}\n\nPergunta: {query}"
        return self.search(enhanced_query, top_k=3)

def demonstrar_integracao():
    """Demonstração prática de como usar o RAG"""
    print("🚀 Demonstração de Integração com RAG Web Builders")
    print("=" * 50)
    
    # Inicializar cliente
    rag = RAGClient()
    
    # 1. Verificar saúde do serviço
    print("\n1️⃣ Verificando status do serviço...")
    health = rag.health_check()
    print(f"Status: {health.get('status', 'unknown')}")
    
    if health.get('status') != 'healthy':
        print("⚠️ Serviço não está saudável. Continuando mesmo assim...")
    
    # 2. Busca simples
    print("\n2️⃣ Busca simples sobre React...")
    results = rag.search(
        query="Como criar componentes React com hooks",
        top_k=3
    )
    
    if results and results.get('results'):
        for i, result in enumerate(results['results'][:2], 1):
            print(f"\n📄 Resultado {i}:")
            print(f"   Título: {result['fonte'].get('title', 'N/A')}")
            print(f"   Score: {result['score']:.2f}")
            print(f"   Conteúdo: {result['chunk'][:150]}...")
            if result.get('rationale'):
                print(f"   Explicação: {result['rationale']}")
    else:
        print("❌ Nenhum resultado encontrado (dados ainda sendo indexados)")
    
    # 3. Busca com filtros
    print("\n3️⃣ Busca com filtros específicos...")
    results_filtered = rag.search(
        query="autenticação e autorização",
        top_k=2,
        filtros={
            "stack": "nodejs",
            "categoria": "backend"
        }
    )
    
    if results_filtered and results_filtered.get('results'):
        print(f"Encontrados {len(results_filtered['results'])} resultados filtrados")
        for result in results_filtered['results']:
            print(f"   - {result['fonte'].get('title', 'N/A')} (Score: {result['score']:.2f})")
    else:
        print("❌ Nenhum resultado com filtros encontrado")
    
    # 4. Busca com contexto
    print("\n4️⃣ Busca com contexto específico...")
    context_results = rag.search_with_context(
        query="Como implementar autenticação?",
        context="Estou desenvolvendo uma API REST com Node.js e Express"
    )
    
    if context_results and context_results.get('results'):
        print("✅ Busca contextual realizada com sucesso")
        print(f"Query processada: {context_results.get('query_info', {}).get('processed_query', 'N/A')}")
    
    # 5. Estatísticas da busca
    if results:
        stats = results.get('search_stats', {})
        print("\n📊 Estatísticas da última busca:")
        print(f"   Total de chunks pesquisados: {stats.get('total_chunks_searched', 0)}")
        print(f"   Resultados vetoriais: {stats.get('vector_results', 0)}")
        print(f"   Resultados textuais: {stats.get('text_results', 0)}")
        print(f"   Tempo de busca: {results.get('search_time_ms', 0)}ms")
        print(f"   Cache utilizado: {'Sim' if results.get('cached') else 'Não'}")

def exemplo_integracao_web_app():
    """Exemplo de como integrar em uma aplicação web"""
    print("\n🌐 Exemplo de Integração em Aplicação Web")
    print("=" * 45)
    
    # Simulação de uma função de busca para chatbot
    def chatbot_search(user_question: str, user_context: str = "") -> str:
        rag = RAGClient()
        
        # Construir query contextual
        if user_context:
            query = f"Contexto do usuário: {user_context}\n\nPergunta: {user_question}"
        else:
            query = user_question
        
        results = rag.search(query, top_k=3, include_rationale=True)
        
        if not results or not results.get('results'):
            return "Desculpe, não encontrei informações relevantes sobre isso. O sistema ainda está indexando dados."
        
        # Construir resposta baseada nos resultados
        response_parts = []
        for result in results['results'][:2]:
            if result['score'] > 0.7:  # Apenas resultados relevantes
                response_parts.append(f"📚 {result['fonte'].get('title', 'Fonte')}: {result['chunk'][:200]}...")
                if result.get('rationale'):
                    response_parts.append(f"💡 {result['rationale']}")
        
        if response_parts:
            return "\n\n".join(response_parts)
        else:
            return "Encontrei algumas informações, mas não são muito relevantes para sua pergunta específica."
    
    # Teste do chatbot
    print("\n🤖 Testando chatbot com RAG:")
    
    perguntas = [
        "Como fazer deploy de uma aplicação React?",
        "Qual a diferença entre useState e useEffect?",
        "Como configurar um banco de dados PostgreSQL?"
    ]
    
    for pergunta in perguntas:
        print(f"\n👤 Usuário: {pergunta}")
        resposta = chatbot_search(pergunta, "Desenvolvedor iniciante em React")
        print(f"🤖 Bot: {resposta[:300]}{'...' if len(resposta) > 300 else ''}")

def exemplo_cache_local():
    """Exemplo de implementação de cache local"""
    print("\n💾 Exemplo com Cache Local")
    print("=" * 30)
    
    import hashlib
    import time
    
    class RAGClientWithCache(RAGClient):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cache = {}
            self.cache_ttl = 300  # 5 minutos
        
        def _get_cache_key(self, query: str, **kwargs) -> str:
            cache_data = f"{query}_{json.dumps(kwargs, sort_keys=True)}"
            return hashlib.md5(cache_data.encode()).hexdigest()
        
        def search(self, query: str, **kwargs):
            cache_key = self._get_cache_key(query, **kwargs)
            now = time.time()
            
            # Verificar cache
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if now - timestamp < self.cache_ttl:
                    print("💾 Resultado do cache local")
                    return cached_data
            
            # Buscar no RAG
            result = super().search(query, **kwargs)
            
            # Salvar no cache
            if result:
                self.cache[cache_key] = (result, now)
            
            return result
    
    # Teste do cache
    rag_cached = RAGClientWithCache()
    
    print("Primeira busca (vai para o servidor):")
    start_time = time.time()
    result1 = rag_cached.search("React components best practices")
    time1 = time.time() - start_time
    print(f"Tempo: {time1:.2f}s")
    
    print("\nSegunda busca (do cache):")
    start_time = time.time()
    result2 = rag_cached.search("React components best practices")
    time2 = time.time() - start_time
    print(f"Tempo: {time2:.2f}s")
    
    print(f"\n⚡ Aceleração com cache: {time1/time2 if time2 > 0 else 'N/A'}x")

if __name__ == "__main__":
    try:
        demonstrar_integracao()
        exemplo_integracao_web_app()
        exemplo_cache_local()
        
        print("\n" + "=" * 50)
        print("✅ Demonstração concluída com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Aguarde a indexação completa dos dados")
        print("2. Teste com suas próprias queries")
        print("3. Implemente cache para melhor performance")
        print("4. Adicione tratamento de erros robusto")
        print("\n🔗 URL do RAG: https://web-builders-rag.onrender.com")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante a demonstração: {e}")