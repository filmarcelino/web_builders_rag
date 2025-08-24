#!/usr/bin/env python3
"""
Script para testar a inicialização do servidor RAG localmente
Simula o ambiente de produção para identificar problemas
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

def test_server_components():
    """Testa a inicialização de todos os componentes do servidor"""
    print("🔍 Testando inicialização dos componentes...")
    
    try:
        # Teste 1: Configuração
        print("📋 Testando configuração...")
        from config.config import RAGConfig
        print(f"✅ Configuração carregada: {RAGConfig.EMBEDDING_MODEL}")
        
        # Teste 2: LoggingManager
        print("📝 Testando LoggingManager...")
        from src.observability.logging_manager import LoggingManager
        logging_manager = LoggingManager()
        print("✅ LoggingManager inicializado")
        
        # Teste 3: MetricsCollector
        print("📊 Testando MetricsCollector...")
        from src.observability.metrics_collector import MetricsCollector
        metrics_collector = MetricsCollector()
        print("✅ MetricsCollector inicializado")
        
        # Teste 4: SearchEngine
        print("🔍 Testando SearchEngine...")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY não encontrada")
            return False
            
        from src.search.search_engine import SearchEngine
        search_engine = SearchEngine(api_key)
        print("✅ SearchEngine inicializado")
        
        # Teste 5: FastAPI App
        print("🚀 Testando FastAPI App...")
        
        # Simula a inicialização do main.py
        import main
        print("✅ Módulo main importado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_lifespan_simulation():
    """Simula o lifespan do FastAPI para testar inicialização"""
    print("\n🔄 Simulando lifespan do FastAPI...")
    
    try:
        # Simula as variáveis globais
        search_engine = None
        metrics_collector = None
        logging_manager = None
        
        # Simula a inicialização do lifespan
        from src.observability.logging_manager import LoggingManager
        from src.observability.metrics_collector import MetricsCollector
        from src.search.search_engine import SearchEngine
        
        print("📝 Inicializando LoggingManager...")
        logging_manager = LoggingManager()
        
        print("📊 Inicializando MetricsCollector...")
        metrics_collector = MetricsCollector()
        
        print("🔍 Inicializando SearchEngine...")
        api_key = os.getenv("OPENAI_API_KEY", "demo-key")
        search_engine = SearchEngine(api_key)
        
        print("✅ Todos os componentes inicializados com sucesso!")
        
        # Teste básico de funcionamento
        print("\n🧪 Testando funcionalidades básicas...")
        
        # Testa se o search_engine está funcionando
        if hasattr(search_engine, 'get_search_stats'):
            stats = search_engine.get_search_stats()
            print(f"✅ SearchEngine stats: {len(stats)} métricas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no lifespan: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_health_check_logic():
    """Testa a lógica do health check"""
    print("\n🏥 Testando lógica do health check...")
    
    try:
        # Simula as condições do health check
        search_engine = None
        metrics = None
        logging_manager = None
        
        # Inicializa componentes
        from src.observability.logging_manager import LoggingManager
        from src.observability.metrics_collector import MetricsCollector
        from src.search.search_engine import SearchEngine
        
        logging_manager = LoggingManager()
        metrics = MetricsCollector()
        api_key = os.getenv("OPENAI_API_KEY", "demo-key")
        search_engine = SearchEngine(api_key)
        
        # Simula a lógica do health check
        components = {
            "search_engine": "healthy" if search_engine else "unhealthy",
            "metrics": "healthy" if metrics else "unhealthy",
            "logging": "healthy" if logging_manager else "unhealthy"
        }
        
        print(f"📊 Status dos componentes: {components}")
        
        all_healthy = all(status == "healthy" for status in components.values())
        
        if all_healthy:
            print("✅ Health check passaria (status 200)")
            return True
        else:
            print("❌ Health check falharia (status 503)")
            return False
            
    except Exception as e:
        print(f"❌ Erro no health check: {str(e)}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Testando inicialização do servidor RAG")
    print("=" * 50)
    
    # Teste 1: Componentes individuais
    components_ok = test_server_components()
    
    # Teste 2: Lifespan simulation
    lifespan_ok = asyncio.run(test_lifespan_simulation())
    
    # Teste 3: Health check logic
    health_ok = test_health_check_logic()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES DE SERVIDOR:")
    print(f"Componentes individuais: {'✅' if components_ok else '❌'}")
    print(f"Simulação lifespan: {'✅' if lifespan_ok else '❌'}")
    print(f"Lógica health check: {'✅' if health_ok else '❌'}")
    
    if components_ok and lifespan_ok and health_ok:
        print("\n🎉 Servidor deve inicializar corretamente!")
        print("💡 Se ainda há problemas no Render, verifique:")
        print("   - Variáveis de ambiente no Render")
        print("   - Logs de deploy no Render")
        print("   - Configurações de porta e host")
        return 0
    else:
        print("\n⚠️  Problemas identificados na inicialização local.")
        print("🔧 Corrija estes problemas antes do deploy.")
        return 1

if __name__ == "__main__":
    sys.exit(main())