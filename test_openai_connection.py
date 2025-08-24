#!/usr/bin/env python3
"""
Script de teste para verificar a conexão com a API da OpenAI
Use este script para diagnosticar problemas de configuração antes do deploy
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

def test_openai_connection():
    """Testa a conexão com a API da OpenAI"""
    print("🔍 Testando conexão com OpenAI...")
    
    # Verifica se a API key está configurada
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        return False
    
    if api_key == "sk-your-openai-api-key-here":
        print("❌ OPENAI_API_KEY ainda está com valor padrão")
        return False
    
    print(f"✅ API Key encontrada: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Teste simples de embedding
        print("🧪 Testando geração de embedding...")
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input="teste de conexão"
        )
        
        if response.data and len(response.data) > 0:
            embedding_size = len(response.data[0].embedding)
            print(f"✅ Embedding gerado com sucesso! Dimensões: {embedding_size}")
            return True
        else:
            print("❌ Resposta da API inválida")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar com OpenAI: {str(e)}")
        return False

def test_environment_variables():
    """Testa se todas as variáveis de ambiente necessárias estão configuradas"""
    print("\n🔍 Verificando variáveis de ambiente...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "PORT",
        "HOST"
    ]
    
    optional_vars = [
        "RAG_API_KEY",
        "OPENAI_MODEL",
        "ENVIRONMENT",
        "LOG_LEVEL"
    ]
    
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            print(f"❌ Variável obrigatória {var} não encontrada")
            all_good = False
        else:
            print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
    
    print("\n📋 Variáveis opcionais:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: não configurada (usando padrão)")
    
    return all_good

def test_imports():
    """Testa se todos os módulos necessários podem ser importados"""
    print("\n🔍 Testando imports...")
    
    modules_to_test = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "uvicorn"),
        ("openai", "openai"),
        ("numpy", "numpy"),
        ("config.config", "RAGConfig"),
        ("src.search.search_engine", "SearchEngine"),
        ("src.indexing.index_manager", "IndexManager"),
        ("src.observability.logging_manager", "LoggingManager")
    ]
    
    all_imports_ok = True
    
    for module_name, import_name in modules_to_test:
        try:
            if "." in module_name:
                # Import from submodule
                parts = module_name.split(".")
                module = __import__(module_name, fromlist=[import_name])
                getattr(module, import_name)
            else:
                # Simple import
                __import__(module_name)
            print(f"✅ {module_name} importado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao importar {module_name}: {str(e)}")
            all_imports_ok = False
    
    return all_imports_ok

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de diagnóstico do RAG System")
    print("=" * 50)
    
    # Teste 1: Variáveis de ambiente
    env_ok = test_environment_variables()
    
    # Teste 2: Imports
    imports_ok = test_imports()
    
    # Teste 3: Conexão OpenAI
    openai_ok = test_openai_connection()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print(f"Variáveis de ambiente: {'✅' if env_ok else '❌'}")
    print(f"Imports de módulos: {'✅' if imports_ok else '❌'}")
    print(f"Conexão OpenAI: {'✅' if openai_ok else '❌'}")
    
    if env_ok and imports_ok and openai_ok:
        print("\n🎉 Todos os testes passaram! O sistema deve funcionar corretamente.")
        return 0
    else:
        print("\n⚠️  Alguns testes falharam. Verifique as configurações antes do deploy.")
        return 1

if __name__ == "__main__":
    sys.exit(main())