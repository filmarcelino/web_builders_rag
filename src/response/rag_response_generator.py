import openai
import json
import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from config.config import RAGConfig
from src.prompts.animation_prompt_enhancer import AnimationPromptEnhancer

@dataclass
class RAGResponse:
    """Resposta completa do sistema RAG"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    query_info: Dict[str, Any]
    enhanced_prompt_used: bool
    animation_boost_applied: bool
    generated_at: str

class RAGResponseGenerator:
    """Gerador de respostas finais do sistema RAG"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuração OpenAI
        openai.api_key = RAGConfig.OPENAI_API_KEY
        
        # Componentes especializados
        self.animation_prompt_enhancer = AnimationPromptEnhancer()
        
        # Templates de prompt base
        self.base_system_prompt = """
Você é um assistente especializado em desenvolvimento web e programação.
Use APENAS as informações fornecidas no contexto para responder à pergunta.
Forneça uma resposta prática e detalhada, incluindo código quando apropriado.
Sempre cite as fontes quando possível.

INSTRUÇÕES IMPORTANTES:
1. Base sua resposta exclusivamente no contexto fornecido
2. Se as informações não forem suficientes, indique claramente essa limitação
3. Inclua exemplos de código práticos e funcionais
4. Mantenha a resposta organizada e fácil de seguir
5. Cite as fontes relevantes para cada informação
"""
        
        # Estatísticas
        self._stats = {
            'total_responses': 0,
            'animation_enhanced': 0,
            'avg_response_time': 0,
            'total_response_time': 0,
            'tokens_used': 0,
            'confidence_scores': []
        }
        
        self.logger.info("RAGResponseGenerator inicializado")
    
    def generate_response(self, 
                         query: str, 
                         relevant_chunks: List[Dict[str, Any]], 
                         query_info: Dict[str, Any] = None) -> RAGResponse:
        """Gera resposta final do RAG"""
        start_time = time.time()
        
        try:
            # 1. Detectar se é consulta sobre animação
            is_animation_query = self.animation_prompt_enhancer.is_animation_query(query)
            
            # 2. Construir contexto a partir dos chunks
            context = self._build_context(relevant_chunks, is_animation_query)
            
            # 3. Preparar prompts (sistema e usuário)
            system_prompt, user_prompt = self._prepare_prompts(
                query, context, is_animation_query
            )
            
            # 4. Gerar resposta com OpenAI
            response_content = self._call_openai(
                system_prompt, user_prompt
            )
            
            # 5. Calcular score de confiança
            confidence_score = self._calculate_confidence(
                query, relevant_chunks, response_content
            )
            
            # 6. Preparar resposta final
            processing_time = time.time() - start_time
            
            response = RAGResponse(
                answer=response_content,
                sources=self._extract_sources(relevant_chunks),
                confidence_score=confidence_score,
                processing_time=processing_time,
                query_info=query_info or {'original_query': query},
                enhanced_prompt_used=is_animation_query,
                animation_boost_applied=is_animation_query,
                generated_at=datetime.now().isoformat()
            )
            
            # 7. Atualizar estatísticas
            self._update_stats(processing_time, confidence_score, is_animation_query)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro na geração de resposta: {str(e)}")
            processing_time = time.time() - start_time
            
            # Resposta de erro
            return RAGResponse(
                answer=f"Desculpe, ocorreu um erro ao gerar a resposta: {str(e)}",
                sources=[],
                confidence_score=0.0,
                processing_time=processing_time,
                query_info=query_info or {'original_query': query, 'error': str(e)},
                enhanced_prompt_used=False,
                animation_boost_applied=False,
                generated_at=datetime.now().isoformat()
            )
    
    def _build_context(self, chunks: List[Dict[str, Any]], is_animation_query: bool) -> str:
        """Constrói contexto a partir dos chunks relevantes"""
        if is_animation_query:
            # Aplicar boost a chunks de animação
            chunks = self.animation_prompt_enhancer.boost_animation_chunks(chunks)
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get('source', 'Desconhecido')
            content = chunk.get('content', '')
            
            # Adicionar informações de boost se aplicável
            boost_info = ""
            if is_animation_query and chunk.get('animation_boost', 0) > 1.0:
                boost_info = f" [ANIMAÇÃO: {chunk.get('animation_elements', [])}]"
            
            context_parts.append(
                f"[Fonte {i}: {source}{boost_info}]\n{content}"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def _prepare_prompts(self, query: str, context: str, is_animation_query: bool) -> tuple:
        """Prepara prompts do sistema e usuário"""
        
        if is_animation_query:
            # Usar prompt especializado para animações
            system_prompt = self.animation_prompt_enhancer.enhance_system_prompt(
                self.base_system_prompt
            )
            user_prompt = self.animation_prompt_enhancer.enhance_user_prompt(
                query, context
            )
        else:
            # Usar prompt padrão
            system_prompt = self.base_system_prompt
            user_prompt = f"""
Contexto disponível:
{context}

---

Pergunta: {query}

Por favor, responda baseando-se exclusivamente no contexto fornecido.
Inclua exemplos de código e estrutura quando disponível.
"""
        
        return system_prompt, user_prompt
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Chama API OpenAI para gerar resposta"""
        try:
            response = openai.chat.completions.create(
                model=RAGConfig.GPT5_NANO_MODEL,  # Usar modelo mais eficiente para respostas
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                top_p=0.9
            )
            
            # Atualizar estatísticas de tokens
            if hasattr(response, 'usage'):
                self._stats['tokens_used'] += response.usage.total_tokens
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Erro na chamada OpenAI: {str(e)}")
            raise
    
    def _calculate_confidence(self, query: str, chunks: List[Dict], response: str) -> float:
        """Calcula score de confiança da resposta"""
        try:
            # Fatores para cálculo de confiança
            factors = {
                'chunk_quality': 0.0,
                'response_length': 0.0,
                'source_diversity': 0.0,
                'animation_relevance': 0.0
            }
            
            # 1. Qualidade dos chunks
            if chunks:
                avg_similarity = sum(c.get('similarity_score', 0) for c in chunks) / len(chunks)
                factors['chunk_quality'] = min(avg_similarity, 1.0)
            
            # 2. Comprimento da resposta (indicador de completude)
            response_words = len(response.split())
            factors['response_length'] = min(response_words / 500, 1.0)  # Normalizar para 500 palavras
            
            # 3. Diversidade de fontes
            unique_sources = len(set(c.get('source', '') for c in chunks))
            factors['source_diversity'] = min(unique_sources / 3, 1.0)  # Normalizar para 3 fontes
            
            # 4. Relevância para animação (se aplicável)
            if self.animation_prompt_enhancer.is_animation_query(query):
                animation_chunks = sum(1 for c in chunks if c.get('animation_boost', 1.0) > 1.0)
                factors['animation_relevance'] = min(animation_chunks / len(chunks), 1.0) if chunks else 0.0
            else:
                factors['animation_relevance'] = 0.5  # Neutro para consultas não-animação
            
            # Calcular score final (média ponderada)
            weights = {
                'chunk_quality': 0.4,
                'response_length': 0.2,
                'source_diversity': 0.2,
                'animation_relevance': 0.2
            }
            
            confidence = sum(
                factors[factor] * weights[factor] 
                for factor in factors
            )
            
            return round(confidence, 3)
            
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de confiança: {str(e)}")
            return 0.5  # Score neutro em caso de erro
    
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extrai informações das fontes dos chunks"""
        sources = []
        
        for chunk in chunks:
            source_info = {
                'title': chunk.get('source', 'Fonte Desconhecida'),
                'url': chunk.get('source_url', ''),
                'relevance_score': chunk.get('similarity_score', 0.0),
                'snippet': chunk.get('content', '')[:200] + '...',
                'animation_boost': chunk.get('animation_boost', 1.0)
            }
            sources.append(source_info)
        
        return sources
    
    def _update_stats(self, processing_time: float, confidence: float, is_animation: bool):
        """Atualiza estatísticas do gerador"""
        self._stats['total_responses'] += 1
        self._stats['total_response_time'] += processing_time
        self._stats['avg_response_time'] = (
            self._stats['total_response_time'] / self._stats['total_responses']
        )
        self._stats['confidence_scores'].append(confidence)
        
        if is_animation:
            self._stats['animation_enhanced'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do gerador"""
        stats = self._stats.copy()
        
        if stats['confidence_scores']:
            stats['avg_confidence'] = sum(stats['confidence_scores']) / len(stats['confidence_scores'])
        else:
            stats['avg_confidence'] = 0.0
        
        stats['animation_enhancement_rate'] = (
            stats['animation_enhanced'] / max(stats['total_responses'], 1)
        )
        
        return stats
    
    def reset_stats(self):
        """Reseta estatísticas"""
        self._stats = {
            'total_responses': 0,
            'animation_enhanced': 0,
            'avg_response_time': 0,
            'total_response_time': 0,
            'tokens_used': 0,
            'confidence_scores': []
        }
        
        self.logger.info("Estatísticas do RAGResponseGenerator resetadas")