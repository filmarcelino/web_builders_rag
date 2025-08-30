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

# Carregar variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
load_dotenv()

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
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
    global search_engine, metrics_collector, logging_manager
    
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

        index_path = os.getenv("INDEX_PATH", "./data/index")
        search_engine = SearchEngine(api_key=api_key, index_dir=index_path)
        
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
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Configurar segurança
RAG_API_KEY = os.getenv("RAG_API_KEY")

# Rate limiting simples (em produção usar Redis)
from collections import defaultdict
rate_limit_storage = defaultdict(list)

def verify_api_key(request):
    """Verifica a chave de API via cabeçalho X-API-Key"""
    if not RAG_API_KEY:
        # Se não há chave configurada, permite acesso (modo desenvolvimento)
        return True
    
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != RAG_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Chave de API inválida ou ausente. Use o cabeçalho X-API-Key.",
        )
    return True

def check_rate_limit(client_ip: str, limit: int = 60, window: int = 60):
    """Verifica rate limit simples"""
    now = time.time()
    client_requests = rate_limit_storage[client_ip]
    
    # Remove requisições antigas
    client_requests[:] = [req_time for req_time in client_requests if now - req_time < window]
    
    if len(client_requests) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Rate limit excedido. Tente novamente em alguns segundos."
        )
    
    client_requests.append(now)
    return True

# Middleware para métricas e segurança
@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Coleta métricas de requisições e verifica rate limit"""
    start_time = time.time()
    
    # Verificar rate limit para endpoints protegidos
    if request.url.path not in ["/health", "/", "/docs", "/openapi.json"]:
        client_ip = request.client.host if request.client else "unknown"
        try:
            check_rate_limit(client_ip)
        except HTTPException as e:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
    
    response = await call_next(request)
    
    # Métricas básicas sem usar o MetricsCollector por enquanto
    duration = time.time() - start_time
    response.headers["X-Process-Time"] = str(duration)
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
    request: Request,
    query: str,
    limit: int = 10,
    category: str = None,
    source_type: str = None
):
    """Endpoint principal de busca com autenticação"""
    verify_api_key(request)
    return await _search_logic(query, limit, category, source_type)

@app.post("/search")
async def search_post_endpoint(
    request: Request
):
    """Endpoint POST de busca conforme especificação do roteiro"""
    verify_api_key(request)
    
    body = await request.json()
    query = body.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Campo 'query' é obrigatório")
    
    filtros = body.get("filtros", {})
    top_k = body.get("top_k", 6)
    
    return await _search_logic(
        query=query,
        limit=top_k,
        category=filtros.get("categoria"),
        source_type=filtros.get("stack")
    )

async def _search_logic(
    query: str,
    limit: int = 10,
    category: str = None,
    source_type: str = None
):
    """Lógica comum de busca"""
    try:
        if not search_engine:
            raise HTTPException(status_code=503, detail="BACKEND_UNAVAILABLE")
        
        if not query or len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="INVALID_ARGS: Query deve ter pelo menos 2 caracteres")
        
        # Gerar trace_id único
        import uuid
        trace_id = str(uuid.uuid4())
        
        # Executar busca real usando SearchEngine
        results = []
        try:
            from src.search.search_engine import SearchRequest
            
            # Criar requisição de busca
            search_request = SearchRequest(
                query=query,
                filters={
                    'category': category,
                    'source_type': source_type
                } if category or source_type else None,
                top_k=limit,
                search_type="hybrid",
                include_rationale=True,
                use_cache=True,
                rerank=True
            )
            
            # Executar busca real
            search_response = await search_engine.search(search_request)
            
            # Converter formato da resposta
            results = [
                {
                    "chunk": result.get("chunk", result.get("content", "")),
                    "fonte": result.get("fonte", result.get("source", "")),
                    "licenca": result.get("licenca", result.get("license", "MIT")),
                    "score": result.get("score", 0.0),
                    "rationale": result.get("rationale", "Resultado relevante")
                }
                for result in search_response.results
            ]
            
        except Exception as e:
            logger.error(f"Erro na busca real: {e}")
            # Fallback para dados mock apenas em caso de erro
            results = [
                {
                    "chunk": f"[ERRO] Busca falhou para '{query}'. Verifique logs.",
                    "fonte": {
                        "title": "Sistema de Busca",
                        "url": "#error"
                    },
                    "licenca": "N/A",
                    "score": 0.0,
                    "rationale": f"Erro no sistema: {str(e)}"
                }
            ]
        
        return {
            "items": results,
            "trace_id": trace_id,
            "query": query,
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
async def metrics_endpoint(request: Request):
    """Endpoint para métricas do sistema"""
    verify_api_key(request)
    
    try:
        # Métricas básicas do sistema
        metrics = {
            "system": {
                "status": "healthy",
                "uptime": asyncio.get_event_loop().time(),
                "version": "1.0.0"
            },
            "api": {
                "total_requests": len(rate_limit_storage),
                "active_connections": 1
            },
            "search": {
                "total_searches": 0,
                "avg_response_time": 0.0
            }
        }
        
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