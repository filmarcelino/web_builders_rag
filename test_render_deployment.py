#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de deploy no Render
Testa configurações específicas que podem causar erro 503
"""

import os
import sys
import time
import requests
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

def test_environment_variables():
    """Testa se todas as variáveis de ambiente necessárias estão configuradas"""
    print("🔧 Testando variáveis de ambiente...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "RAG_API_KEY"
    ]
    
    optional_vars = [
        "PORT",
        "HOST",
        "ENVIRONMENT",
        "LOG_LEVEL",
        "PYTHONPATH"
    ]
    
    print("\n📋 Variáveis obrigatórias:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * 10}...{value[-4:] if len(value) > 4 else value}")
        else:
            print(f"  ❌ {var}: NÃO CONFIGURADA")
    
    print("\n📋 Variáveis opcionais:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: usando padrão")
    
    # Verificar PORT específica do Render
    port = os.getenv("PORT")
    if port:
        print(f"\n🚢 Render PORT detectada: {port}")
    else:
        print("\n⚠️  PORT não definida - usando padrão 8000")

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("\n📦 Testando importações...")
    
    modules_to_test = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "uvicorn"),
        ("openai", "OpenAI"),
        ("config.config", "RAGConfig"),
        ("src.search.search_engine", "SearchEngine"),
        ("src.observability.logging_manager", "LoggingManager"),
        ("src.observability.metrics_collector", "MetricsCollector")
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name}: {e}")

def test_server_startup():
    """Testa se o servidor pode ser iniciado sem erros"""
    print("\n🚀 Testando inicialização do servidor...")
    
    try:
        # Importar componentes principais
        from config.config import RAGConfig
        from src.search.search_engine import SearchEngine
        from src.observability.logging_manager import LoggingManager
        from src.observability.metrics_collector import MetricsCollector
        
        print("  ✅ Importações principais OK")
        
        # Testar configuração
        config = RAGConfig()
        print("  ✅ RAGConfig inicializada")
        
        # Testar componentes
        logging_manager = LoggingManager(app_name="rag_system")
        print("  ✅ LoggingManager inicializado")
        
        metrics_collector = MetricsCollector()
        print("  ✅ MetricsCollector inicializado")
        
        search_engine = SearchEngine(config)
        print("  ✅ SearchEngine inicializado")
        
        print("\n🎉 Todos os componentes inicializaram com sucesso!")
        
    except Exception as e:
        print(f"  ❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()

def test_network_configuration():
    """Testa configurações de rede que podem causar erro 503"""
    print("\n🌐 Testando configurações de rede...")
    
    # Verificar HOST e PORT
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"  📡 HOST configurado: {host}")
    print(f"  🔌 PORT configurada: {port}")
    
    # Verificar se a porta está disponível
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.close()
        print(f"  ✅ Porta {port} disponível")
    except Exception as e:
        print(f"  ⚠️  Porta {port} pode estar em uso: {e}")
    
    # Verificar CORS
    cors_origins = os.getenv("CORS_ORIGINS", "*")
    print(f"  🔗 CORS Origins: {cors_origins}")

def test_render_specific_issues():
    """Testa problemas específicos do Render que podem causar erro 503"""
    print("\n🏗️  Testando problemas específicos do Render...")
    
    # Verificar se está rodando no Render
    render_service = os.getenv("RENDER_SERVICE_NAME")
    if render_service:
        print(f"  🚢 Rodando no Render: {render_service}")
    else:
        print("  🏠 Rodando localmente")
    
    # Verificar timeout de inicialização
    print("  ⏱️  Simulando tempo de inicialização...")
    start_time = time.time()
    
    # Simular inicialização pesada
    time.sleep(2)
    
    init_time = time.time() - start_time
    print(f"  📊 Tempo de inicialização simulado: {init_time:.2f}s")
    
    if init_time > 60:
        print("  ⚠️  AVISO: Inicialização muito lenta pode causar timeout no Render")
    else:
        print("  ✅ Tempo de inicialização aceitável")
    
    # Verificar memória
    try:
        import psutil
        memory_mb = psutil.virtual_memory().total / (1024 * 1024)
        print(f"  💾 Memória disponível: {memory_mb:.0f}MB")
        
        if memory_mb < 512:
            print("  ⚠️  AVISO: Pouca memória disponível")
        else:
            print("  ✅ Memória suficiente")
    except ImportError:
        print("  ⚠️  psutil não disponível - não foi possível verificar memória")

def main():
    """Executa todos os testes de diagnóstico"""
    print("🔍 DIAGNÓSTICO DE DEPLOY NO RENDER")
    print("=" * 50)
    
    test_environment_variables()
    test_imports()
    test_server_startup()
    test_network_configuration()
    test_render_specific_issues()
    
    print("\n" + "=" * 50)
    print("🏁 Diagnóstico concluído!")
    print("\n💡 Se todos os testes passaram mas ainda há erro 503:")
    print("   1. Verifique os logs do Render")
    print("   2. Confirme se o health check está respondendo")
    print("   3. Verifique se o serviço está escutando na porta correta")
    print("   4. Confirme se não há timeout de inicialização")

if __name__ == "__main__":
    main()