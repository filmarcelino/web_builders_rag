import asyncio
import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import logging
from datetime import datetime

from config.config import RAGConfig
from src.indexing.index_manager import IndexManager, SearchResult as IndexSearchResult
from .query_processor import QueryProcessor, ProcessedQuery
from .search_cache import SearchCache
from .access_control import AccessController, AccessControlResult
from src.reranking.animation_reranker import AnimationReranker
from src.prompts.animation_prompt_enhancer import AnimationPromptEnhancer
from src.response.rag_response_generator import RAGResponseGenerator, RAGResponse

@dataclass
class SearchRequest:
    """Requisição de busca"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    top_k: int = 8
    search_type: str = "hybrid"  # 'vector', 'text', 'hybrid'
    include_rationale: bool = True
    context: Optional[Dict[str, Any]] = None
    use_cache: bool = True
    rerank: bool = True

@dataclass
class SearchResponse:
    """Resposta de busca formatada para API"""
    results: List[Dict[str, Any]]
    query_info: Dict[str, Any]
    search_stats: Dict[str, Any]
    total_results: int
    processing_time: float
    cache_hit: bool

class SearchEngine:
    """Motor de busca principal do RAG"""
    
    def __init__(self, api_key: str, index_dir: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Componentes principais
        self.index_manager = IndexManager(api_key, index_dir)
        self.query_processor = QueryProcessor(api_key)
        self.search_cache = SearchCache()
        self.access_controller = AccessController()
        self.animation_reranker = AnimationReranker()
        self.animation_prompt_enhancer = AnimationPromptEnhancer()
        self.rag_response_generator = RAGResponseGenerator()
        
        # Configurações
        self.api_key = api_key
        self.default_top_k = RAGConfig.SEARCH_TOP_K
        self.max_top_k = 50
        
        # Estatísticas
        self.search_stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'avg_processing_time': 0,
            'search_types': {
                'hybrid': 0,
                'vector': 0,
                'text': 0
            },
            'top_queries': {},
            'error_count': 0
        }
        
        self.logger.info("SearchEngine inicializado")
    
    async def search(self, request: SearchRequest) -> SearchResponse:
        """Executa busca completa"""
        start_time = time.time()
        cache_hit = False
        
        try:
            # Validação da requisição
            self._validate_request(request)
            
            # Verifica cache se habilitado
            if request.use_cache:
                cached_result = self.search_cache.get(
                    request.query, 
                    request.filters, 
                    request.top_k, 
                    request.search_type
                )
                
                if cached_result:
                    cache_hit = True
                    self.search_stats['cache_hits'] += 1
                    
                    processing_time = time.time() - start_time
                    
                    return SearchResponse(
                        results=cached_result['results'],
                        query_info=cached_result['query_info'],
                        search_stats=cached_result['search_stats'],
                        total_results=len(cached_result['results']),
                        processing_time=processing_time,
                        cache_hit=True
                    )
            
            # 1. Processamento da query
            self.logger.debug(f"Processando query: {request.query}")
            processed_query = await self.query_processor.process_query(
                request.query, 
                request.context
            )
            
            # 2. Executa busca no índice
            search_results = await self._execute_search(
                processed_query, 
                request.filters, 
                request.top_k, 
                request.search_type
            )
            
            # 3. Formata resultados
            formatted_results = self._format_results(search_results, processed_query)
            
            # 3.1. Aplica controle de acesso
            access_result = self.access_controller.check_access(
                processed_query.original_query,
                formatted_results,
                request.context
            )
            
            # Filtra resultados baseado no controle de acesso
            formatted_results = access_result.filtered_chunks
            
            # Log de controle de acesso
            if access_result.restricted_count > 0:
                access_message = self.access_controller.get_access_message(access_result)
                self.logger.info(f"Controle de acesso aplicado: {access_message}")
            
            # 3.5. Aplica re-ranking especializado para animações
            if request.rerank and self.animation_reranker.is_animation_query(processed_query.original_query):
                self.logger.info("Aplicando re-ranking especializado para animações")
                formatted_results = self.animation_reranker.rerank_for_animations(
                    processed_query.original_query, 
                    formatted_results
                )
            
            # 4. Calcula estatísticas
            processing_time = time.time() - start_time
            search_stats = self._calculate_search_stats(
                processed_query, 
                search_results, 
                processing_time
            )
            
            # Adiciona estatísticas de re-ranking de animação
            if request.rerank and self.animation_reranker.is_animation_query(processed_query.original_query):
                search_stats['animation_reranking'] = {
                    'applied': True,
                    'results_reranked': len(formatted_results)
                }
            else:
                search_stats['animation_reranking'] = {'applied': False}
            
            # Adiciona estatísticas de controle de acesso
            search_stats['access_control'] = {
                'access_granted': access_result.access_granted,
                'access_level': access_result.access_level,
                'restricted_count': access_result.restricted_count,
                'authorization_found': access_result.authorization_found,
                'message': access_result.message
            }
            
            # 5. Monta resposta
            response = SearchResponse(
                results=formatted_results,
                query_info={
                    'original_query': processed_query.original_query,
                    'rewritten_query': processed_query.rewritten_query,
                    'intent': processed_query.intent,
                    'stack_context': processed_query.stack_context,
                    'category_context': processed_query.category_context,
                    'used_rewriting': processed_query.used_rewriting,
                    'confidence': processed_query.confidence
                },
                search_stats=search_stats,
                total_results=len(formatted_results),
                processing_time=processing_time,
                cache_hit=cache_hit
            )
            
            # 6. Armazena no cache
            if request.use_cache and formatted_results:
                self.search_cache.set(
                    request.query,
                    request.filters,
                    request.top_k,
                    request.search_type,
                    {
                        'results': formatted_results,
                        'query_info': response.query_info,
                        'search_stats': search_stats
                    }
                )
            
            # 7. Atualiza estatísticas globais
            self._update_global_stats(request, processing_time)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro na busca: {str(e)}")
            self.search_stats['error_count'] += 1
            
            # Retorna resposta de erro
            processing_time = time.time() - start_time
            return SearchResponse(
                results=[],
                query_info={'original_query': request.query, 'error': str(e)},
                search_stats={'error': True, 'error_message': str(e)},
                total_results=0,
                processing_time=processing_time,
                cache_hit=False
            )
    
    def generate_rag_response(self, query: str, max_results: int = 10) -> RAGResponse:
        """Gera resposta completa do RAG para uma consulta"""
        try:
            # 1. Realizar busca
            search_request = SearchRequest(
                query=query,
                top_k=max_results,
                filters={}
            )
            
            search_response = self.search(search_request)
            
            # 2. Converter resultados para chunks
            relevant_chunks = []
            for result in search_response.results:
                chunk = {
                    'content': result['chunk'],
                    'source': result['fonte']['title'],
                    'source_url': result['fonte']['url'],
                    'similarity_score': result['score'],
                    'metadata': result['metadata']
                }
                
                # Adicionar informações de boost de animação se aplicável
                if 'animation_boost' in result:
                    chunk['animation_boost'] = result['animation_boost']
                if 'animation_elements' in result:
                    chunk['animation_elements'] = result['animation_elements']
                
                relevant_chunks.append(chunk)
            
            # 3. Gerar resposta final
            query_info = {
                'original_query': query,
                'search_time': search_response.processing_time,
                'total_chunks_found': search_response.total_results,
                'chunks_used': len(relevant_chunks)
            }
            
            return self.rag_response_generator.generate_response(
                query=query,
                relevant_chunks=relevant_chunks,
                query_info=query_info
            )
            
        except Exception as e:
            self.logger.error(f"Erro na geração de resposta RAG: {str(e)}")
            # Retornar resposta de erro
            return RAGResponse(
                answer=f"Desculpe, ocorreu um erro ao processar sua consulta: {str(e)}",
                sources=[],
                confidence_score=0.0,
                processing_time=0.0,
                query_info={'original_query': query, 'error': str(e)},
                enhanced_prompt_used=False,
                animation_boost_applied=False,
                generated_at=datetime.now().isoformat()
            )
    
    def _validate_request(self, request: SearchRequest):
        """Valida requisição de busca"""
        if not request.query or not request.query.strip():
            raise ValueError("Query não pode estar vazia")
        
        if request.top_k <= 0 or request.top_k > self.max_top_k:
            raise ValueError(f"top_k deve estar entre 1 e {self.max_top_k}")
        
        if request.search_type not in ['vector', 'text', 'hybrid']:
            raise ValueError("search_type deve ser 'vector', 'text' ou 'hybrid'")
    
    async def _execute_search(self, processed_query: ProcessedQuery, 
                             filters: Optional[Dict[str, Any]], 
                             top_k: int, 
                             search_type: str) -> List[IndexSearchResult]:
        """Executa busca no índice"""
        # Usa query reescrita se disponível
        search_query = processed_query.rewritten_query
        
        # Adiciona filtros baseados no contexto da query
        enhanced_filters = self._enhance_filters(filters, processed_query)
        
        # Executa busca
        results = await self.index_manager.search(
            search_query, 
            top_k, 
            search_type, 
            enhanced_filters
        )
        
        # Se poucos resultados e há termos expandidos, tenta busca expandida
        if len(results) < top_k // 2 and processed_query.expanded_terms:
            self.logger.debug("Poucos resultados, tentando busca expandida")
            
            # Cria query expandida
            expanded_query = f"{search_query} {' '.join(processed_query.expanded_terms[:3])}"
            
            expanded_results = await self.index_manager.search(
                expanded_query,
                top_k - len(results),
                search_type,
                enhanced_filters
            )
            
            # Combina resultados, evitando duplicatas
            existing_ids = {r.chunk_id for r in results}
            for result in expanded_results:
                if result.chunk_id not in existing_ids:
                    results.append(result)
        
        return results
    
    def _enhance_filters(self, filters: Optional[Dict[str, Any]], 
                        processed_query: ProcessedQuery) -> Dict[str, Any]:
        """Adiciona filtros baseados no contexto da query"""
        enhanced = filters.copy() if filters else {}
        
        # Adiciona filtro de stack se detectado na query
        if processed_query.stack_context and 'stack' not in enhanced:
            # Usa a primeira stack detectada como filtro preferencial
            enhanced['stack_preference'] = processed_query.stack_context[0]
        
        # Adiciona filtro de categoria se detectado
        if processed_query.category_context and 'category' not in enhanced:
            enhanced['category_preference'] = processed_query.category_context[0]
        
        # Filtros específicos para consultas de animação
        if self.animation_reranker.is_animation_query(processed_query.original_query):
            # Prioriza chunks com animation_score alto
            enhanced['animation_score_min'] = 0.1  # Score mínimo para animações
            enhanced['prefer_animation_content'] = True
            
            # Para consultas de animação, reduz requisito de qualidade geral
            # mas exige relevância específica de animação
            if 'quality_score_min' not in enhanced:
                enhanced['quality_score_min'] = 0.3  # Mais permissivo para animações
        
        # Filtro de qualidade baseado na intenção
        elif processed_query.intent in ['implementation', 'example']:
            enhanced['quality_score_min'] = 0.7  # Exige alta qualidade para implementações
        
        return enhanced
    
    def _format_results(self, search_results: List[IndexSearchResult], 
                       processed_query: ProcessedQuery) -> List[Dict[str, Any]]:
        """Formata resultados para resposta da API"""
        formatted = []
        
        for result in search_results:
            # Extrai informações da fonte
            metadata = result.metadata
            
            formatted_result = {
                'chunk': result.content,
                'fonte': {
                    'title': metadata.get('source_title', 'Título não disponível'),
                    'url': metadata.get('source_url', '')
                },
                'licenca': metadata.get('license', 'Não especificada'),
                'score': round(result.score, 4),
                'rationale': result.rationale or self._generate_basic_rationale(
                    result, processed_query
                ),
                'metadata': {
                    'stack': metadata.get('stack', ''),
                    'category': metadata.get('category', ''),
                    'language': metadata.get('language', 'pt'),
                    'maturity_level': metadata.get('maturity_level', ''),
                    'quality_score': metadata.get('quality_score', 0),
                    'updated_at': metadata.get('updated_at', ''),
                    'search_source': result.source
                },
                'highlights': result.highlights[:3] if result.highlights else []
            }
            
            formatted.append(formatted_result)
        
        return formatted
    
    def _generate_basic_rationale(self, result: IndexSearchResult, 
                                 processed_query: ProcessedQuery) -> str:
        """Gera rationale básico quando não há reranking"""
        reasons = []
        
        # Razão baseada no tipo de busca
        if result.source == 'vector':
            reasons.append("semanticamente relevante")
        elif result.source == 'text':
            reasons.append("contém termos-chave")
        elif result.source == 'hybrid':
            reasons.append("relevante semanticamente e por palavras-chave")
        
        # Razão baseada no contexto
        metadata = result.metadata
        if processed_query.stack_context:
            stack = metadata.get('stack', '')
            if stack in processed_query.stack_context:
                reasons.append(f"específico para {stack}")
        
        if processed_query.intent != 'general':
            reasons.append(f"adequado para {processed_query.intent}")
        
        # Razão baseada na qualidade
        quality = metadata.get('quality_score', 0)
        if quality >= 0.8:
            reasons.append("alta qualidade")
        
        return f"Relevante porque é {', '.join(reasons)}."
    
    def _calculate_search_stats(self, processed_query: ProcessedQuery, 
                               search_results: List[IndexSearchResult], 
                               processing_time: float) -> Dict[str, Any]:
        """Calcula estatísticas da busca"""
        return {
            'query_processing_time': processed_query.processing_time,
            'search_time': processing_time - processed_query.processing_time,
            'total_processing_time': processing_time,
            'results_found': len(search_results),
            'used_query_rewriting': processed_query.used_rewriting,
            'query_confidence': processed_query.confidence,
            'search_sources': {
                source: len([r for r in search_results if r.source == source])
                for source in ['vector', 'text', 'hybrid']
            },
            'avg_result_score': (
                sum(r.score for r in search_results) / len(search_results)
                if search_results else 0
            ),
            'stack_distribution': self._get_stack_distribution(search_results),
            'category_distribution': self._get_category_distribution(search_results)
        }
    
    def _get_stack_distribution(self, results: List[IndexSearchResult]) -> Dict[str, int]:
        """Calcula distribuição de stacks nos resultados"""
        distribution = {}
        for result in results:
            stack = result.metadata.get('stack', 'unknown')
            distribution[stack] = distribution.get(stack, 0) + 1
        return distribution
    
    def _get_category_distribution(self, results: List[IndexSearchResult]) -> Dict[str, int]:
        """Calcula distribuição de categorias nos resultados"""
        distribution = {}
        for result in results:
            category = result.metadata.get('category', 'unknown')
            distribution[category] = distribution.get(category, 0) + 1
        return distribution
    
    def _update_global_stats(self, request: SearchRequest, processing_time: float):
        """Atualiza estatísticas globais"""
        self.search_stats['total_searches'] += 1
        
        # Atualiza tempo médio
        total = self.search_stats['total_searches']
        current_avg = self.search_stats['avg_processing_time']
        self.search_stats['avg_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Atualiza contadores por tipo
        self.search_stats['search_types'][request.search_type] += 1
        
        # Atualiza top queries
        query_key = request.query.lower().strip()
        self.search_stats['top_queries'][query_key] = (
            self.search_stats['top_queries'].get(query_key, 0) + 1
        )
        
        # Mantém apenas top 100 queries
        if len(self.search_stats['top_queries']) > 100:
            sorted_queries = sorted(
                self.search_stats['top_queries'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.search_stats['top_queries'] = dict(sorted_queries[:100])
    
    async def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Recupera chunk específico por ID"""
        try:
            indexed_chunk = self.index_manager.get_chunk_by_id(chunk_id)
            if indexed_chunk:
                return {
                    'chunk_id': indexed_chunk.chunk_id,
                    'content': indexed_chunk.content,
                    'metadata': indexed_chunk.metadata
                }
            return None
        except Exception as e:
            self.logger.error(f"Erro ao recuperar chunk {chunk_id}: {str(e)}")
            return None
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de busca"""
        query_processor_stats = self.query_processor.get_processing_stats()
        cache_stats = self.search_cache.get_cache_stats()
        index_stats = self.index_manager.get_comprehensive_stats()
        
        return {
            'search_engine_stats': self.search_stats,
            'query_processor_stats': query_processor_stats,
            'cache_stats': cache_stats,
            'index_stats': index_stats
        }
    
    def clear_cache(self):
        """Limpa todos os caches"""
        self.search_cache.clear()
        self.query_processor.clear_cache()
        self.logger.info("Caches de busca limpos")
    
    def close(self):
        """Fecha motor de busca e libera recursos"""
        try:
            self.index_manager.close()
            self.search_cache.close()
            self.logger.info("SearchEngine fechado")
        except Exception as e:
            self.logger.error(f"Erro ao fechar SearchEngine: {str(e)}")