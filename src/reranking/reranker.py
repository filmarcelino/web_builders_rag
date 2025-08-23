import openai
import json
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
from datetime import datetime

from config.config import RAGConfig

@dataclass
class RerankingResult:
    """Resultado do reranking"""
    original_index: int
    new_score: float
    rationale: str
    relevance_score: float
    confidence: float
    reasoning_steps: List[str]

@dataclass
class RerankingStats:
    """Estatísticas do reranking"""
    total_requests: int
    total_items_processed: int
    avg_processing_time: float
    avg_score_change: float
    gpt5_api_calls: int
    gpt5_tokens_used: int
    error_count: int
    cache_hits: int

class GPTReranker:
    """Reranker inteligente usando GPT-5 Full"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuração OpenAI
        openai.api_key = RAGConfig.OPENAI_API_KEY
        
        # Estatísticas
        self._stats = {
            'total_requests': 0,
            'total_items_processed': 0,
            'total_processing_time': 0,
            'total_score_change': 0,
            'gpt5_api_calls': 0,
            'gpt5_tokens_used': 0,
            'error_count': 0,
            'cache_hits': 0
        }
        
        # Cache simples para evitar reprocessamento
        self._reranking_cache = {}
        
        self.logger.info("GPTReranker inicializado")
    
    def rerank_results(self, query: str, results: List[Dict[str, Any]], 
                      context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Reranqueia resultados usando GPT-5 Full"""
        start_time = time.time()
        
        try:
            if not results:
                return results
            
            self.logger.info(f"Iniciando reranking de {len(results)} resultados para query: '{query}'")
            
            # Gera chave de cache
            cache_key = self._generate_cache_key(query, results)
            
            # Verifica cache
            if cache_key in self._reranking_cache:
                self._stats['cache_hits'] += 1
                self.logger.debug("Resultado do reranking obtido do cache")
                return self._reranking_cache[cache_key]
            
            # Executa reranking
            reranked_results = self._perform_reranking(query, results, context)
            
            # Atualiza cache
            self._reranking_cache[cache_key] = reranked_results
            
            # Atualiza estatísticas
            processing_time = time.time() - start_time
            self._update_stats(len(results), processing_time)
            
            self.logger.info(f"Reranking concluído em {processing_time:.2f}s")
            
            return reranked_results
        
        except Exception as e:
            self._stats['error_count'] += 1
            self.logger.error(f"Erro no reranking: {str(e)}")
            # Retorna resultados originais em caso de erro
            return results
    
    def _perform_reranking(self, query: str, results: List[Dict[str, Any]], 
                          context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Executa o reranking usando GPT-5 Full"""
        try:
            # Prepara prompt para GPT-5
            prompt = self._build_reranking_prompt(query, results, context)
            
            # Chama GPT-5 Full
            response = self._call_gpt5_full(prompt)
            
            # Processa resposta
            reranking_data = self._parse_gpt5_response(response)
            
            # Aplica reranking aos resultados
            reranked_results = self._apply_reranking(results, reranking_data)
            
            return reranked_results
        
        except Exception as e:
            self.logger.error(f"Erro na execução do reranking: {str(e)}")
            raise
    
    def _build_reranking_prompt(self, query: str, results: List[Dict[str, Any]], 
                               context: Optional[Dict[str, Any]]) -> str:
        """Constrói prompt para GPT-5 Full"""
        # Contexto adicional
        context_info = ""
        if context:
            stack = context.get('stack', '')
            categoria = context.get('categoria', '')
            if stack or categoria:
                context_info = f"\nContexto: Stack={stack}, Categoria={categoria}"
        
        # Prepara resultados para o prompt
        results_text = ""
        for i, result in enumerate(results):
            chunk = result.get('chunk', '')[:500]  # Limita tamanho
            fonte = result.get('fonte', {})
            score = result.get('score', 0)
            metadata = result.get('metadata', {})
            
            results_text += f"\n[{i}] Score: {score:.3f}\n"
            results_text += f"Fonte: {fonte.get('title', 'N/A')} ({fonte.get('url', 'N/A')})\n"
            results_text += f"Stack: {metadata.get('stack', 'N/A')}, Categoria: {metadata.get('categoria', 'N/A')}\n"
            results_text += f"Conteúdo: {chunk}\n"
        
        prompt = f"""Você é um especialista em desenvolvimento de aplicações web e precisa reranquear resultados de busca para maximizar a utilidade para um desenvolvedor.

QUERY DO USUÁRIO: "{query}"{context_info}

RESULTADOS PARA RERANQUEAR:{results_text}

TAREFA:
1. Analise cada resultado considerando:
   - Relevância direta para a query
   - Qualidade e completude da informação
   - Aplicabilidade prática para desenvolvimento
   - Atualidade e maturidade da fonte
   - Complementaridade com outros resultados

2. Para cada resultado, forneça:
   - Novo score (0.0 a 1.0)
   - Rationale explicativo (máximo 100 palavras)
   - Nível de confiança (0.0 a 1.0)

3. Ordene os resultados do mais relevante para o menos relevante.

RESPONDA EM JSON:
{{
  "reranked_results": [
    {{
      "original_index": 0,
      "new_score": 0.95,
      "rationale": "Explicação concisa do porquê este resultado é relevante",
      "confidence": 0.9,
      "reasoning_steps": ["Passo 1", "Passo 2"]
    }}
  ],
  "overall_assessment": "Avaliação geral da qualidade dos resultados"
}}

IMPORTANTE:
- Seja objetivo e prático
- Priorize informações acionáveis
- Considere o contexto de desenvolvimento de apps
- Mantenha rationales concisos mas informativos"""
        
        return prompt
    
    def _call_gpt5_full(self, prompt: str) -> str:
        """Chama GPT-5 Full para reranking"""
        try:
            self._stats['gpt5_api_calls'] += 1
            
            response = openai.chat.completions.create(
                model=RAGConfig.GPT5_FULL_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em desenvolvimento web e sistemas RAG. Forneça respostas precisas e estruturadas em JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Baixa temperatura para consistência
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Atualiza estatísticas de tokens
            if hasattr(response, 'usage'):
                self._stats['gpt5_tokens_used'] += response.usage.total_tokens
            
            return response.choices[0].message.content
        
        except Exception as e:
            self.logger.error(f"Erro na chamada GPT-5 Full: {str(e)}")
            raise
    
    def _parse_gpt5_response(self, response: str) -> Dict[str, Any]:
        """Processa resposta do GPT-5"""
        try:
            data = json.loads(response)
            
            # Valida estrutura
            if 'reranked_results' not in data:
                raise ValueError("Resposta não contém 'reranked_results'")
            
            reranked_results = data['reranked_results']
            
            # Valida cada resultado
            for result in reranked_results:
                required_fields = ['original_index', 'new_score', 'rationale', 'confidence']
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Campo obrigatório '{field}' ausente")
                
                # Valida ranges
                if not (0 <= result['new_score'] <= 1):
                    result['new_score'] = max(0, min(1, result['new_score']))
                
                if not (0 <= result['confidence'] <= 1):
                    result['confidence'] = max(0, min(1, result['confidence']))
            
            return data
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao parsear JSON do GPT-5: {str(e)}")
            raise ValueError(f"Resposta inválida do GPT-5: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Erro ao processar resposta do GPT-5: {str(e)}")
            raise
    
    def _apply_reranking(self, original_results: List[Dict[str, Any]], 
                        reranking_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aplica reranking aos resultados originais"""
        try:
            reranked_items = reranking_data['reranked_results']
            
            # Cria mapeamento de índices
            reranking_map = {}
            for item in reranked_items:
                original_idx = item['original_index']
                if 0 <= original_idx < len(original_results):
                    reranking_map[original_idx] = item
            
            # Aplica reranking
            reranked_results = []
            
            # Ordena por novo score (decrescente)
            sorted_items = sorted(
                reranking_map.items(),
                key=lambda x: x[1]['new_score'],
                reverse=True
            )
            
            for original_idx, rerank_info in sorted_items:
                result = original_results[original_idx].copy()
                
                # Atualiza score
                old_score = result.get('score', 0)
                new_score = rerank_info['new_score']
                result['score'] = new_score
                
                # Adiciona informações do reranking
                result['rationale'] = rerank_info['rationale']
                result['reranking_info'] = {
                    'original_score': old_score,
                    'new_score': new_score,
                    'score_change': new_score - old_score,
                    'confidence': rerank_info['confidence'],
                    'reasoning_steps': rerank_info.get('reasoning_steps', []),
                    'reranked_at': datetime.now().isoformat()
                }
                
                reranked_results.append(result)
                
                # Atualiza estatística de mudança de score
                self._stats['total_score_change'] += abs(new_score - old_score)
            
            # Adiciona resultados que não foram reranqueados (se houver)
            processed_indices = set(reranking_map.keys())
            for i, result in enumerate(original_results):
                if i not in processed_indices:
                    result_copy = result.copy()
                    result_copy['rationale'] = "Resultado não processado pelo reranking"
                    reranked_results.append(result_copy)
            
            return reranked_results
        
        except Exception as e:
            self.logger.error(f"Erro ao aplicar reranking: {str(e)}")
            raise
    
    def _generate_cache_key(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Gera chave de cache para reranking"""
        import hashlib
        
        # Cria string única baseada na query e nos IDs dos resultados
        cache_string = query.lower().strip()
        
        for result in results:
            chunk_id = result.get('metadata', {}).get('chunk_id', '')
            score = result.get('score', 0)
            cache_string += f"|{chunk_id}:{score:.3f}"
        
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()[:16]
    
    def _update_stats(self, num_items: int, processing_time: float):
        """Atualiza estatísticas"""
        self._stats['total_requests'] += 1
        self._stats['total_items_processed'] += num_items
        self._stats['total_processing_time'] += processing_time
    
    def get_reranking_stats(self) -> RerankingStats:
        """Retorna estatísticas do reranking"""
        total_requests = self._stats['total_requests']
        total_items = self._stats['total_items_processed']
        total_time = self._stats['total_processing_time']
        
        return RerankingStats(
            total_requests=total_requests,
            total_items_processed=total_items,
            avg_processing_time=total_time / max(1, total_requests),
            avg_score_change=self._stats['total_score_change'] / max(1, total_items),
            gpt5_api_calls=self._stats['gpt5_api_calls'],
            gpt5_tokens_used=self._stats['gpt5_tokens_used'],
            error_count=self._stats['error_count'],
            cache_hits=self._stats['cache_hits']
        )
    
    def clear_cache(self):
        """Limpa cache de reranking"""
        self._reranking_cache.clear()
        self.logger.info("Cache de reranking limpo")
    
    def get_cache_size(self) -> int:
        """Retorna tamanho do cache"""
        return len(self._reranking_cache)