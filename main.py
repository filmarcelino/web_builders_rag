#!/usr/bin/env python3
"""
Ponto de entrada principal para a API do Sistema RAG
Configurações otimizadas para produção no Render.com
"""

import os
import sys
import asyncio
import logging
import time
from pathlib import Path
from contextlib import asynccontextmanager

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Imports do sistema RAG
from src.search.search_engine import SearchEngine
from src.observability.logging_manager import LoggingManager
from src.observability.metrics_collector import MetricsCollector
from config.config import RAGConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variáveis globais para componentes do sistema
search_engine = None
metrics_collector = None
logging_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    global search_api, metrics_collector, logging_manager
    
    try:
        # Inicializar componentes
        logger.info("🚀 Inicializando Sistema RAG...")
        
        # Configurar logging
        logging_manager = LoggingManager()
        
        # Configurar métricas
        metrics_collector = MetricsCollector()
        
        # Inicializar motor de busca
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("⚠️ OPENAI_API_KEY não encontrada, usando modo demo")
            api_key = "demo-key"
        
        search_engine = SearchEngine(api_key=api_key)
        
        logger.info("✅ Sistema RAG inicializado com sucesso")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🔄 Finalizando Sistema RAG...")
        logger.info("✅ Sistema RAG finalizado")

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema RAG - Vina Base Agent",
    description="API para busca inteligente com RAG (Retrieval-Augmented Generation)",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para métricas
@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Coleta métricas de requisições"""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Métricas básicas sem usar o MetricsCollector por enquanto
    duration = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    
    return response

# Rotas de saúde
@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    try:
        status = {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "components": {
                "search_engine": search_engine is not None,
                "metrics": metrics_collector is not None,
                "logging": logging_manager is not None
            }
        }
        
        # Verificar se todos os componentes estão funcionando
        if all(status["components"].values()):
            return JSONResponse(content=status, status_code=200)
        else:
            status["status"] = "degraded"
            return JSONResponse(content=status, status_code=503)
            
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        )

@app.get("/")
async def root():
    """Rota raiz com informações da API"""
    return {
        "message": "Sistema RAG - Vina Base Agent",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "search": "/search",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }

# Rotas de busca
@app.get("/search")
async def search_endpoint(
    query: str,
    limit: int = 10,
    category: str = None,
    source_type: str = None
):
    """Endpoint principal de busca"""
    try:
        if not search_engine:
            raise HTTPException(status_code=503, detail="Search Engine não inicializado")
        
        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Query deve ter pelo menos 2 caracteres")
        
        # Executar busca
        from src.search.search_engine import SearchRequest
        search_request = SearchRequest(
            query=query.strip(),
            top_k=min(limit, 50),
            filters={
                "categoria": category,
                "stack": source_type
            }
        )
        
        search_response = await search_engine.search(search_request)
        results = search_response.results
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# Rota de métricas
@app.get("/metrics")
async def metrics_endpoint():
    """Endpoint para métricas do sistema"""
    try:
        if not metrics_collector:
            raise HTTPException(status_code=503, detail="Metrics collector não inicializado")
        
        metrics = await metrics_collector.get_current_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter métricas")

# Rota de status detalhado
@app.get("/status")
async def status_endpoint():
    """Status detalhado do sistema"""
    try:
        status = {
            "system": "RAG API",
            "version": "1.0.0",
            "uptime": asyncio.get_event_loop().time(),
            "environment": os.getenv("ENVIRONMENT", "production"),
            "components": {
                "search_engine": {
                    "status": "active" if search_engine else "inactive",
                    "initialized": search_engine is not None
                },
                "metrics_collector": {
                    "status": "active" if metrics_collector else "inactive",
                    "initialized": metrics_collector is not None
                },
                "logging_manager": {
                    "status": "active" if logging_manager else "inactive",
                    "initialized": logging_manager is not None
                }
            },
            "configuration": {
                "max_results": 50,
                "timeout": 30,
                "cors_enabled": True
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter status")

def main():
    """Função principal para executar o servidor"""
    # Configurações do servidor
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    workers = int(os.getenv("WORKERS", 1))
    
    logger.info(f"🚀 Iniciando servidor RAG em {host}:{port}")
    
    # Configurações para produção
    config = {
        "app": "main:app",
        "host": host,
        "port": port,
        "workers": workers,
        "log_level": "info",
        "access_log": True,
        "use_colors": False,
        "loop": "asyncio"
    }
    
    # Executar servidor
    uvicorn.run(**config)

if __name__ == "__main__":
    main()