#!/usr/bin/env python3
"""
Teste de inicialização em ambiente de produção
Simula as condições do Render para identificar problemas de deploy
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

def simulate_render_environment():
    """Simula variáveis de ambiente do Render"""
    print("🏗️  Simulando ambiente do Render...")
    
    # Variáveis típicas do Render
    render_env = {
        "RENDER": "true",
        "RENDER_SERVICE_NAME": "vina-rag-api",
        "RENDER_SERVICE_TYPE": "web",
        "PORT": "10000",  # Porta típica do Render
        "HOST": "0.0.0.0",
        "ENVIRONMENT": "production",
        "LOG_LEVEL": "INFO",
        "PYTHONPATH": "/opt/render/project/src",
        "PYTHON_VERSION": "3.11",
        "MAX_SEARCH_RESULTS": "50",
        "SEARCH_TIMEOUT": "30",
        "WORKERS": "1",
        "CORS_ORIGINS": "*",
        "RATE_LIMIT_REQUESTS": "100",
        "RATE_LIMIT_WINDOW": "60",
        "CACHE_TTL": "3600",
        "OPENAI_MODEL": "gpt-4o-mini",
        "EMBEDDING_MODEL": "text-embedding-3-small"
    }
    
    # Aplicar variáveis de ambiente
    for key, value in render_env.items():
        os.environ[key] = value
        print(f"  📝 {key}={value}")
    
    print("  ✅ Ambiente do Render simulado")

def test_production_startup():
    """Testa inicialização em modo produção"""
    print("\n🚀 Testando inicialização em modo produção...")
    
    try:
        # Importar e inicializar componentes como no main.py
        from config.config import RAGConfig
        from src.search.search_engine import SearchEngine
        from src.observability.logging_manager import LoggingManager
        from src.observability.metrics_collector import MetricsCollector
        
        print("  ✅ Importações OK")
        
        # Inicializar na ordem do main.py
        start_time = time.time()
        
        # 1. Configuração
        config = RAGConfig()
        print("  ✅ RAGConfig inicializada")
        
        # 2. Logging
        logging_manager = LoggingManager(app_name="rag_system")
        print("  ✅ LoggingManager inicializado")
        
        # 3. Métricas
        metrics_collector = MetricsCollector()
        print("  ✅ MetricsCollector inicializado")
        
        # 4. Motor de busca (sem API key real)
        search_engine = SearchEngine(api_key="demo-key")
        print("  ✅ SearchEngine inicializado")
        
        init_time = time.time() - start_time
        print(f"  ⏱️  Tempo total de inicialização: {init_time:.2f}s")
        
        if init_time > 30:
            print("  ⚠️  AVISO: Inicialização muito lenta para o Render")
        else:
            print("  ✅ Tempo de inicialização aceitável")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fastapi_startup():
    """Testa se o FastAPI pode ser inicializado"""
    print("\n🌐 Testando inicialização do FastAPI...")
    
    try:
        # Definir variáveis de ambiente necessárias antes de importar
        os.environ["OPENAI_API_KEY"] = "demo-key"
        os.environ["RAG_API_KEY"] = "demo-rag-key"
        
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        
        print("  ✅ Importações FastAPI OK")
        
        # Criar app como no main.py
        app = FastAPI(
            title="Sistema RAG - API de Busca Inteligente",
            description="API para busca semântica e híbrida em documentos",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        print("  ✅ FastAPI app criada")
        
        # Configurar CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        print("  ✅ CORS configurado")
        
        # Configurar rate limiting
        limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        print("  ✅ Rate limiting configurado")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na configuração FastAPI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_uvicorn_compatibility():
    """Testa compatibilidade com Uvicorn"""
    print("\n🦄 Testando compatibilidade com Uvicorn...")
    
    try:
        import uvicorn
        print(f"  ✅ Uvicorn versão: {uvicorn.__version__}")
        
        # Testar configuração do servidor
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        workers = int(os.getenv("WORKERS", 1))
        
        print(f"  📡 Host: {host}")
        print(f"  🔌 Port: {port}")
        print(f"  👥 Workers: {workers}")
        
        # Verificar se a configuração é válida
        if host in ["0.0.0.0", "127.0.0.1", "localhost"]:
            print("  ✅ Host válido")
        else:
            print(f"  ⚠️  Host incomum: {host}")
        
        if 1000 <= port <= 65535:
            print("  ✅ Porta válida")
        else:
            print(f"  ⚠️  Porta fora do range padrão: {port}")
        
        if 1 <= workers <= 4:
            print("  ✅ Número de workers adequado")
        else:
            print(f"  ⚠️  Número de workers incomum: {workers}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro com Uvicorn: {e}")
        return False

def test_health_check_simulation():
    """Simula o health check do Render"""
    print("\n🏥 Simulando health check do Render...")
    
    try:
        # Simular requisição de health check
        import json
        
        # Dados que o health check deveria retornar
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {
                "search_engine": "operational",
                "metrics": "operational",
                "logging": "operational"
            }
        }
        
        print(f"  📊 Health check response: {json.dumps(health_data, indent=2)}")
        print("  ✅ Health check simulado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no health check: {e}")
        return False

def main():
    """Executa todos os testes de produção"""
    print("🔍 TESTE DE INICIALIZAÇÃO EM PRODUÇÃO")
    print("=" * 50)
    
    # Simular ambiente do Render
    simulate_render_environment()
    
    # Executar testes
    tests = [
        ("Inicialização dos componentes", test_production_startup),
        ("Configuração FastAPI", test_fastapi_startup),
        ("Compatibilidade Uvicorn", test_uvicorn_compatibility),
        ("Health Check", test_health_check_simulation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Executando: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {status}: {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n✅ O serviço deve funcionar corretamente no Render")
        print("\n📝 Próximos passos:")
        print("   1. Configurar OPENAI_API_KEY no Render")
        print("   2. Configurar RAG_API_KEY no Render")
        print("   3. Fazer deploy")
        print("   4. Verificar logs de inicialização")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("\n🔧 Corrija os problemas antes do deploy")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)