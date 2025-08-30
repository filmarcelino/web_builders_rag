from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
import logging
import time
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

from .search_engine import SearchEngine
from .query_processor import QueryProcessor
from .search_cache import SearchCache
from config.config import RAGConfig

# Modelos Pydantic para API
class SearchFilters(BaseModel):
    """Filtros de busca"""
    stack: Optional[str] = Field(None, description="Stack tecnológica (ex: nextjs, react)")
    categoria: Optional[str] = Field(None, description="Categoria do conteúdo")
    licenca: Optional[str] = Field(None, description="Tipo de licença")
    updated_after: Optional[str] = Field(None, description="Data mínima de atualização (YYYY-MM-DD)")
    idioma: Optional[str] = Field(None, description="Idioma do conteúdo")
    maturidade: Optional[str] = Field(None, description="Nível de maturidade")
    min_quality_score: Optional[float] = Field(None, ge=0, le=1, description="Score mínimo de qualidade")
    
    @validator('updated_after')
    def validate_date(cls, v):
        if v:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Data deve estar no formato YYYY-MM-DD')
        return v

class SearchRequest(BaseModel):
    """Requisição de busca"""
    query: str = Field(..., min_length=1, max_length=500, description="Consulta de busca")
    filtros: Optional[SearchFilters] = Field(None, description="Filtros opcionais")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Número máximo de resultados")
    search_type: Optional[str] = Field('hybrid', description="Tipo de busca: vector, text, hybrid")
    include_rationale: Optional[bool] = Field(True, description="Incluir explicação dos resultados")
    
    @validator('search_type')
    def validate_search_type(cls, v):
        if v not in ['vector', 'text', 'hybrid']:
            raise ValueError('search_type deve ser: vector, text ou hybrid')
        return v

class SearchResultItem(BaseModel):
    """Item de resultado de busca"""
    chunk: str = Field(..., description="Trecho de conteúdo")
    fonte: Dict[str, str] = Field(..., description="Informações da fonte")
    licenca: str = Field(..., description="Licença do conteúdo")
    score: float = Field(..., description="Score após reranking")
    rationale: Optional[str] = Field(None, description="Explicação do resultado")
    metadata: Dict[str, Any] = Field(..., description="Metadados adicionais")

class SearchResponse(BaseModel):
    """Resposta de busca"""
    results: List[SearchResultItem] = Field(..., description="Lista de resultados")
    query_info: Dict[str, Any] = Field(..., description="Informações sobre a consulta")
    search_stats: Dict[str, Any] = Field(..., description="Estatísticas da busca")
    total_results: int = Field(..., description="Total de resultados encontrados")
    search_time_ms: float = Field(..., description="Tempo de busca em milissegundos")
    cached: bool = Field(..., description="Se o resultado veio do cache")

class HealthResponse(BaseModel):
    """Resposta de health check"""
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]
    stats: Dict[str, Any]

# Gerenciador de contexto para inicialização
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Startup
    logger = logging.getLogger(__name__)
    logger.info("Iniciando RAG Search API...")
    
    try:
        # Inicializa componentes
        search_engine = SearchEngine()
        app.state.search_engine = search_engine
        
        logger.info("RAG Search API iniciada com sucesso")
        yield
        
    except Exception as e:
        logger.error(f"Erro na inicialização: {str(e)}")
        raise
    
    finally:
        # Shutdown
        logger.info("Finalizando RAG Search API...")
        
        if hasattr(app.state, 'search_engine'):
            # Fecha componentes
            if hasattr(app.state.search_engine, 'cache'):
                app.state.search_engine.cache.close()
        
        logger.info("RAG Search API finalizada")

# Criação da aplicação FastAPI
app = FastAPI(
    title="RAG Search API",
    description="API de busca híbrida para sistema RAG do agente de desenvolvimento",
    version="1.0.0",
    lifespan=lifespan
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger
logger = logging.getLogger(__name__)

# Dependency para obter search engine
def get_search_engine() -> SearchEngine:
    """Dependency para obter instância do SearchEngine"""
    if not hasattr(app.state, 'search_engine'):
        raise HTTPException(status_code=503, detail="Search engine não inicializado")
    return app.state.search_engine

@app.get("/health", response_model=HealthResponse)
async def health_check(search_engine: SearchEngine = Depends(get_search_engine)):
    """Health check da API"""
    try:
        # Verifica componentes
        components_status = {
            "search_engine": "ok",
            "index_manager": "ok" if search_engine.index_manager else "error",
            "query_processor": "ok" if search_engine.query_processor else "error",
            "cache": "ok" if search_engine.cache else "error"
        }
        
        # Obtém estatísticas
        stats = {}
        try:
            if search_engine.index_manager:
                index_stats = search_engine.index_manager.get_stats()
                stats["index"] = {
                    "total_chunks": index_stats.get("total_chunks", 0),
                    "total_sources": index_stats.get("total_sources", 0)
                }
            
            if search_engine.cache:
                cache_stats = search_engine.cache.get_cache_stats()
                stats["cache"] = {
                    "total_entries": cache_stats.total_entries,
                    "hit_rate": cache_stats.hit_rate,
                    "total_size_mb": cache_stats.total_size_bytes / (1024 * 1024)
                }
            
            search_stats = search_engine.get_search_stats()
            stats["search"] = search_stats
            
        except Exception as e:
            logger.warning(f"Erro ao obter estatísticas: {str(e)}")
            stats["error"] = str(e)
        
        # Determina status geral
        overall_status = "ok" if all(status == "ok" for status in components_status.values()) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            components=components_status,
            stats=stats
        )
    
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    search_engine: SearchEngine = Depends(get_search_engine)
):
    """Endpoint principal de busca"""
    start_time = time.time()
    
    print(f"[DEBUG API ENTRY] Endpoint /search chamado com query: {request.query}")
    
    try:
        logger.info(f"Busca recebida: '{request.query}' (tipo: {request.search_type})")
        
        # Converte filtros para dict
        filters_dict = None
        if request.filtros:
            filters_dict = request.filtros.dict(exclude_none=True)
        
        # Cria SearchRequest para o engine
        from src.search.search_engine import SearchRequest as EngineSearchRequest
        
        engine_request = EngineSearchRequest(
            query=request.query,
            filters=filters_dict,
            top_k=request.top_k,
            search_type=request.search_type,
            include_rationale=request.include_rationale,
            use_cache=True,
            rerank=True
        )
        
        # Executa busca
        search_result = await search_engine.search(engine_request)
        
        search_time = (time.time() - start_time) * 1000  # Converte para ms
        
        # Debug: verificar o tipo e conteúdo da resposta do SearchEngine
        logger.warning(f"[DEBUG API] Tipo de search_result: {type(search_result)}")
        logger.warning(f"[DEBUG API] Total de resultados: {len(search_result.results)}")
        
        for i, result in enumerate(search_result.results[:3]):
            logger.warning(f"[DEBUG API] Resultado {i} tipo: {type(result)}")
            logger.warning(f"[DEBUG API] Resultado {i} keys: {list(result.keys()) if hasattr(result, 'keys') else 'N/A'}")
            chunk_content = result.get("chunk", "")
            logger.warning(f"[DEBUG API] Resultado {i}: chunk_length={len(chunk_content)}, chunk_preview='{chunk_content[:50] if chunk_content else 'VAZIO'}'")
        
        # Formata resposta
        response = SearchResponse(
            results=[
                SearchResultItem(
                    chunk=result["chunk"],
                    fonte=result["fonte"] if isinstance(result["fonte"], dict) else {"title": str(result["fonte"]), "url": ""},
                    licenca=result["licenca"],
                    score=result["score"],
                    rationale=result.get("rationale"),
                    metadata=result.get("metadata", {})
                )
                for result in search_result.results
            ],
            query_info=search_result.query_info,
            search_stats=search_result.search_stats,
            total_results=len(search_result.results),
            search_time_ms=search_time,
            cached=search_result.get("cached", False)
        )
        
        logger.info(
            f"Busca concluída: {len(response.results)} resultados em {search_time:.1f}ms "
            f"(cached: {response.cached})"
        )
        
        return response
    
    except ValueError as e:
        logger.warning(f"Erro de validação na busca: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Erro interno na busca: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/search/stats")
async def get_search_stats(search_engine: SearchEngine = Depends(get_search_engine)):
    """Obtém estatísticas detalhadas do sistema de busca"""
    try:
        stats = {
            "search": search_engine.get_search_stats(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Adiciona estatísticas do índice
        if search_engine.index_manager:
            stats["index"] = search_engine.index_manager.get_stats()
        
        # Adiciona estatísticas do cache
        if search_engine.cache:
            cache_stats = search_engine.cache.get_cache_stats()
            stats["cache"] = {
                "total_entries": cache_stats.total_entries,
                "total_size_bytes": cache_stats.total_size_bytes,
                "hit_count": cache_stats.hit_count,
                "miss_count": cache_stats.miss_count,
                "hit_rate": cache_stats.hit_rate,
                "avg_access_time": cache_stats.avg_access_time
            }
            
            # Top queries
            stats["top_queries"] = search_engine.cache.get_top_queries(10)
        
        return stats
    
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/search/cache/invalidate")
async def invalidate_cache(
    pattern: Optional[str] = Query(None, description="Padrão para invalidar"),
    source_url: Optional[str] = Query(None, description="URL da fonte para invalidar"),
    clear_all: Optional[bool] = Query(False, description="Limpar todo o cache"),
    search_engine: SearchEngine = Depends(get_search_engine)
):
    """Invalida entradas do cache"""
    try:
        if clear_all:
            search_engine.cache.clear()
            message = "Cache completamente limpo"
        elif pattern:
            search_engine.cache.invalidate_by_pattern(pattern)
            message = f"Cache invalidado para padrão: {pattern}"
        elif source_url:
            search_engine.cache.invalidate_by_source(source_url)
            message = f"Cache invalidado para fonte: {source_url}"
        else:
            raise HTTPException(status_code=400, detail="Especifique pattern, source_url ou clear_all")
        
        logger.info(message)
        return {"message": message, "timestamp": datetime.now().isoformat()}
    
    except Exception as e:
        logger.error(f"Erro ao invalidar cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="Consulta parcial"),
    limit: int = Query(5, ge=1, le=10, description="Número máximo de sugestões"),
    search_engine: SearchEngine = Depends(get_search_engine)
):
    """Obtém sugestões de busca baseadas em queries anteriores"""
    try:
        # Obtém top queries do cache
        top_queries = search_engine.cache.get_top_queries(50)
        
        # Filtra queries que contêm a consulta parcial
        suggestions = []
        query_lower = query.lower()
        
        for cached_query, count in top_queries:
            if query_lower in cached_query.lower() and cached_query.lower() != query_lower:
                suggestions.append({
                    "query": cached_query,
                    "usage_count": count
                })
                
                if len(suggestions) >= limit:
                    break
        
        return {
            "suggestions": suggestions,
            "query": query,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter sugestões: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Endpoint para teste rápido
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "RAG Search API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicia servidor
    uvicorn.run(
        "search_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )