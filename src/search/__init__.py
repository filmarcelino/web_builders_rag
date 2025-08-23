"""Módulo de busca RAG

Este módulo implementa a API de busca híbrida (vetorial + textual) com:
- Query rewriting com GPT-5 Full
- Filtros por metadados
- Busca híbrida otimizada
- Cache de resultados
- Métricas de performance
"""

from .search_engine import SearchEngine, SearchRequest, SearchResponse
from .query_processor import QueryProcessor, ProcessedQuery
# from .result_ranker import ResultRanker, RankedResult  # Module not implemented yet
from .search_cache import SearchCache
from .search_api import app as SearchAPI

__all__ = [
    'SearchEngine',
    'SearchRequest', 
    'SearchResponse',
    'QueryProcessor',
    'ProcessedQuery',
    'SearchCache',
    'SearchAPI'
]