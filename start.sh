#!/bin/bash

# Script de inicialização para o Sistema RAG
# Otimizado para produção no Render.com

set -e  # Parar em caso de erro

echo "🚀 Iniciando Sistema RAG - Vina Base Agent"
echo "================================================"

# Verificar Python
echo "📋 Verificando versão do Python..."
python --version

# Verificar variáveis de ambiente essenciais
echo "🔧 Verificando configurações..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  AVISO: OPENAI_API_KEY não configurada - usando modo demo"
else
    echo "✅ OPENAI_API_KEY configurada"
fi

# Configurar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/index/vector
mkdir -p data/index/text
mkdir -p data/index/cache
mkdir -p logs
mkdir -p src/logs
mkdir -p data/governance
mkdir -p dashboards
mkdir -p backups

echo "✅ Diretórios criados"

# Verificar dependências críticas
echo "📦 Verificando dependências..."
python -c "import fastapi, uvicorn, openai, numpy, pandas" 2>/dev/null && echo "✅ Dependências principais OK" || echo "❌ Erro nas dependências"

# Configurar variáveis de ambiente padrão
export PYTHONPATH="${PYTHONPATH}:/app/src"
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Configurações do servidor
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export WORKERS=${WORKERS:-1}
export ENVIRONMENT=${ENVIRONMENT:-production}

echo "🌐 Configurações do servidor:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Workers: $WORKERS"
echo "   Environment: $ENVIRONMENT"

# Verificar saúde do sistema antes de iniciar
echo "🔍 Verificação pré-inicialização..."
python -c "
import sys
sys.path.append('/app/src')
try:
    from config.config import RAGConfig
    print('✅ Configuração RAG OK')
except Exception as e:
    print(f'⚠️  Aviso na configuração: {e}')

try:
    from src.search.search_api import SearchAPI
    print('✅ SearchAPI importada OK')
except Exception as e:
    print(f'⚠️  Aviso na SearchAPI: {e}')
" 2>/dev/null || echo "⚠️  Alguns módulos podem não estar disponíveis"

echo "================================================"
echo "🎯 Iniciando servidor principal..."
echo "📡 API estará disponível em: http://$HOST:$PORT"
echo "🏥 Health check: http://$HOST:$PORT/health"
echo "📚 Documentação: http://$HOST:$PORT/docs"
echo "================================================"

# Iniciar o servidor
exec python main.py