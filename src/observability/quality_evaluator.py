import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import asyncio
import time
from collections import defaultdict

@dataclass
class QualityScores:
    """Scores de qualidade para uma resposta"""
    context_relevance: float  # 0-1: Quão relevante é o contexto para a query
    faithfulness: float       # 0-1: Quão fiel a resposta é ao contexto
    semantic_answer_similarity: float  # 0-1: Similaridade com resposta ideal
    
    # Scores detalhados
    context_precision: float = 0.0
    context_recall: float = 0.0
    answer_correctness: float = 0.0
    answer_completeness: float = 0.0
    
    # Metadados
    evaluation_timestamp: str = ""
    evaluation_method: str = "gpt5_full"
    confidence_score: float = 0.0
    
    def overall_score(self) -> float:
        """Score geral ponderado"""
        weights = {
            'context_relevance': 0.3,
            'faithfulness': 0.4,
            'semantic_answer_similarity': 0.3
        }
        
        return (
            weights['context_relevance'] * self.context_relevance +
            weights['faithfulness'] * self.faithfulness +
            weights['semantic_answer_similarity'] * self.semantic_answer_similarity
        )

@dataclass
class EvaluationResult:
    """Resultado completo de uma avaliação"""
    query_id: str
    scores: QualityScores
    detailed_feedback: Dict[str, Any]
    processing_time_ms: float
    cost_estimate: float

class QualityEvaluator:
    """Avaliador de qualidade usando GPT-5 Full e métricas automáticas"""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-5-full"):
        self.logger = logging.getLogger(__name__)
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        
        # Cache de embeddings para SAS
        self._embedding_cache = {}
        
        # Estatísticas
        self._evaluation_stats = {
            'total_evaluations': 0,
            'avg_processing_time': 0,
            'total_cost': 0,
            'score_distribution': defaultdict(list)
        }
        
        # Templates de prompts
        self._init_prompt_templates()
        
        self.logger.info(f"QualityEvaluator inicializado (model: {model})")
    
    async def evaluate_quality(self, query: str, context_chunks: List[str], 
                             generated_answer: str, 
                             ideal_answer: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> EvaluationResult:
        """Avalia qualidade completa de uma resposta"""
        start_time = time.time()
        query_id = metadata.get('query_id', f"eval_{int(time.time())}")
        
        try:
            # Avalia Context Relevance
            context_relevance = await self._evaluate_context_relevance(query, context_chunks)
            
            # Avalia Faithfulness
            faithfulness = await self._evaluate_faithfulness(context_chunks, generated_answer)
            
            # Avalia SAS (se resposta ideal disponível)
            sas = 0.0
            if ideal_answer:
                sas = await self._evaluate_semantic_similarity(generated_answer, ideal_answer)
            
            # Avaliações detalhadas
            context_precision = await self._evaluate_context_precision(query, context_chunks)
            context_recall = await self._evaluate_context_recall(query, context_chunks)
            answer_correctness = await self._evaluate_answer_correctness(context_chunks, generated_answer)
            answer_completeness = await self._evaluate_answer_completeness(query, generated_answer)
            
            # Calcula confiança baseada na consistência dos scores
            confidence = self._calculate_confidence([
                context_relevance, faithfulness, sas,
                context_precision, context_recall,
                answer_correctness, answer_completeness
            ])
            
            # Cria scores
            scores = QualityScores(
                context_relevance=context_relevance,
                faithfulness=faithfulness,
                semantic_answer_similarity=sas,
                context_precision=context_precision,
                context_recall=context_recall,
                answer_correctness=answer_correctness,
                answer_completeness=answer_completeness,
                evaluation_timestamp=datetime.now().isoformat(),
                evaluation_method=self.model,
                confidence_score=confidence
            )
            
            # Feedback detalhado
            detailed_feedback = await self._generate_detailed_feedback(
                query, context_chunks, generated_answer, scores
            )
            
            processing_time = (time.time() - start_time) * 1000
            cost_estimate = self._estimate_cost(query, context_chunks, generated_answer)
            
            # Atualiza estatísticas
            self._update_stats(scores, processing_time, cost_estimate)
            
            result = EvaluationResult(
                query_id=query_id,
                scores=scores,
                detailed_feedback=detailed_feedback,
                processing_time_ms=processing_time,
                cost_estimate=cost_estimate
            )
            
            self.logger.info(
                f"Quality evaluation completed",
                extra={
                    'query_id': query_id,
                    'overall_score': scores.overall_score(),
                    'context_relevance': context_relevance,
                    'faithfulness': faithfulness,
                    'sas': sas,
                    'processing_time_ms': processing_time
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação de qualidade: {str(e)}")
            # Retorna scores padrão em caso de erro
            return EvaluationResult(
                query_id=query_id,
                scores=QualityScores(
                    context_relevance=0.0,
                    faithfulness=0.0,
                    semantic_answer_similarity=0.0,
                    evaluation_timestamp=datetime.now().isoformat(),
                    confidence_score=0.0
                ),
                detailed_feedback={'error': str(e)},
                processing_time_ms=(time.time() - start_time) * 1000,
                cost_estimate=0.0
            )
    
    async def _evaluate_context_relevance(self, query: str, context_chunks: List[str]) -> float:
        """Avalia relevância do contexto para a query (0-1)"""
        try:
            # Prompt para avaliar relevância de cada chunk
            prompt = self._prompts['context_relevance'].format(
                query=query,
                context_chunks=self._format_chunks_for_prompt(context_chunks)
            )
            
            response = await self._call_gpt5(prompt, max_tokens=500)
            
            # Parse da resposta JSON
            result = json.loads(response)
            
            # Calcula score médio ponderado
            total_score = 0
            total_weight = 0
            
            for chunk_eval in result.get('chunk_evaluations', []):
                relevance = chunk_eval.get('relevance_score', 0)
                importance = chunk_eval.get('importance_weight', 1)
                total_score += relevance * importance
                total_weight += importance
            
            return total_score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação de context relevance: {str(e)}")
            return 0.0
    
    async def _evaluate_faithfulness(self, context_chunks: List[str], answer: str) -> float:
        """Avalia fidelidade da resposta ao contexto (0-1)"""
        try:
            prompt = self._prompts['faithfulness'].format(
                context_chunks=self._format_chunks_for_prompt(context_chunks),
                answer=answer
            )
            
            response = await self._call_gpt5(prompt, max_tokens=800)
            result = json.loads(response)
            
            # Analisa claims e verificações
            claims = result.get('claims', [])
            if not claims:
                return 0.0
            
            supported_claims = sum(1 for claim in claims if claim.get('supported', False))
            total_claims = len(claims)
            
            faithfulness_score = supported_claims / total_claims
            
            # Penaliza contradições
            contradictions = result.get('contradictions', [])
            if contradictions:
                penalty = min(0.3, len(contradictions) * 0.1)
                faithfulness_score = max(0, faithfulness_score - penalty)
            
            return faithfulness_score
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação de faithfulness: {str(e)}")
            return 0.0
    
    async def _evaluate_semantic_similarity(self, answer: str, ideal_answer: str) -> float:
        """Avalia similaridade semântica com resposta ideal (0-1)"""
        try:
            # Usa embeddings para calcular similaridade
            answer_embedding = await self._get_embedding(answer)
            ideal_embedding = await self._get_embedding(ideal_answer)
            
            # Similaridade coseno
            similarity = cosine_similarity(
                [answer_embedding], [ideal_embedding]
            )[0][0]
            
            # Normaliza para 0-1
            normalized_similarity = (similarity + 1) / 2
            
            # Complementa com avaliação GPT-5 para nuances semânticas
            prompt = self._prompts['semantic_similarity'].format(
                answer=answer,
                ideal_answer=ideal_answer
            )
            
            response = await self._call_gpt5(prompt, max_tokens=300)
            result = json.loads(response)
            
            gpt_similarity = result.get('similarity_score', 0.5)
            
            # Combina embeddings (70%) + GPT-5 (30%)
            final_score = 0.7 * normalized_similarity + 0.3 * gpt_similarity
            
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação de SAS: {str(e)}")
            return 0.0
    
    async def _evaluate_context_precision(self, query: str, context_chunks: List[str]) -> float:
        """Avalia precisão do contexto (chunks relevantes / total chunks)"""
        try:
            prompt = self._prompts['context_precision'].format(
                query=query,
                context_chunks=self._format_chunks_for_prompt(context_chunks)
            )
            
            response = await self._call_gpt5(prompt, max_tokens=400)
            result = json.loads(response)
            
            relevant_chunks = sum(1 for chunk in result.get('chunk_relevance', []) 
                                if chunk.get('is_relevant', False))
            total_chunks = len(context_chunks)
            
            return relevant_chunks / total_chunks if total_chunks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação de context precision: {str(e)}")
            return 0.0
    
    async def _evaluate_context_recall(self, query: str, context_chunks: List[str]) -> float:
        """Avalia recall do contexto (informação necessária presente)"""
        try:
            prompt = self._prompts['context_recall'].format(
                query=query,
                context_chunks=self._format_chunks_for_prompt(context_chunks)
            )
            
            response = await self._call_gpt5(prompt, max_tokens=500)
            result = json.loads(response)
            
            # Analisa aspectos necessários cobertos
            required_aspects = result.get('required_aspects', [])
            covered_aspects = result.get('covered_aspects', [])
            
            if not required_aspects:
                return 1.0  # Se não há aspectos requeridos, recall é perfeito
            
            coverage = len(covered_aspects) / len(required_aspects)
            return min(1.0, coverage)
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação de context recall: {str(e)}")
            return 0.0
    
    async def _evaluate_answer_correctness(self, context_chunks: List[str], answer: str) -> float:
        """Avalia correção factual da resposta"""
        try:
            prompt = self._prompts['answer_correctness'].format(
                context_chunks=self._format_chunks_for_prompt(context_chunks),
                answer=answer
            )
            
            response = await self._call_gpt5(prompt, max_tokens=600)
            result = json.loads(response)
            
            # Analisa statements factuais
            factual_statements = result.get('factual_statements', [])
            if not factual_statements:
                return 0.5  # Neutro se não há statements factuais
            
            correct_statements = sum(1 for stmt in factual_statements 
                                   if stmt.get('is_correct', False))
            
            correctness = correct_statements / len(factual_statements)
            
            # Penaliza erros graves
            serious_errors = result.get('serious_errors', [])
            if serious_errors:
                penalty = min(0.5, len(serious_errors) * 0.2)
                correctness = max(0, correctness - penalty)
            
            return correctness
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação de answer correctness: {str(e)}")
            return 0.0
    
    async def _evaluate_answer_completeness(self, query: str, answer: str) -> float:
        """Avalia completude da resposta"""
        try:
            prompt = self._prompts['answer_completeness'].format(
                query=query,
                answer=answer
            )
            
            response = await self._call_gpt5(prompt, max_tokens=400)
            result = json.loads(response)
            
            completeness_score = result.get('completeness_score', 0.5)
            
            # Ajusta baseado em aspectos específicos
            aspects_covered = result.get('aspects_covered', [])
            aspects_missing = result.get('aspects_missing', [])
            
            if aspects_covered and aspects_missing:
                coverage_ratio = len(aspects_covered) / (len(aspects_covered) + len(aspects_missing))
                completeness_score = (completeness_score + coverage_ratio) / 2
            
            return min(1.0, max(0.0, completeness_score))
            
        except Exception as e:
            self.logger.error(f"Erro na avaliação de answer completeness: {str(e)}")
            return 0.0
    
    async def _generate_detailed_feedback(self, query: str, context_chunks: List[str], 
                                        answer: str, scores: QualityScores) -> Dict[str, Any]:
        """Gera feedback detalhado sobre a qualidade"""
        try:
            prompt = self._prompts['detailed_feedback'].format(
                query=query,
                context_chunks=self._format_chunks_for_prompt(context_chunks),
                answer=answer,
                scores=json.dumps({
                    'context_relevance': scores.context_relevance,
                    'faithfulness': scores.faithfulness,
                    'sas': scores.semantic_answer_similarity,
                    'overall': scores.overall_score()
                })
            )
            
            response = await self._call_gpt5(prompt, max_tokens=800)
            result = json.loads(response)
            
            return {
                'strengths': result.get('strengths', []),
                'weaknesses': result.get('weaknesses', []),
                'suggestions': result.get('suggestions', []),
                'quality_assessment': result.get('quality_assessment', ''),
                'improvement_areas': result.get('improvement_areas', [])
            }
            
        except Exception as e:
            self.logger.error(f"Erro na geração de feedback detalhado: {str(e)}")
            return {'error': str(e)}
    
    async def _call_gpt5(self, prompt: str, max_tokens: int = 1000) -> str:
        """Chama GPT-5 Full"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator of RAG system quality. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Erro na chamada GPT-5: {str(e)}")
            raise
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Obtém embedding para texto (com cache)"""
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        try:
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                model="text-embedding-3-large",
                input=text
            )
            
            embedding = response.data[0].embedding
            self._embedding_cache[text] = embedding
            
            # Limita cache
            if len(self._embedding_cache) > 1000:
                # Remove 20% dos mais antigos
                items_to_remove = list(self._embedding_cache.keys())[:200]
                for key in items_to_remove:
                    del self._embedding_cache[key]
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Erro ao obter embedding: {str(e)}")
            return [0.0] * 3072  # Dimensão padrão
    
    def _format_chunks_for_prompt(self, chunks: List[str]) -> str:
        """Formata chunks para uso em prompts"""
        formatted = []
        for i, chunk in enumerate(chunks, 1):
            # Limita tamanho do chunk no prompt
            truncated_chunk = chunk[:500] + "..." if len(chunk) > 500 else chunk
            formatted.append(f"Chunk {i}:\n{truncated_chunk}")
        
        return "\n\n".join(formatted)
    
    def _calculate_confidence(self, scores: List[float]) -> float:
        """Calcula confiança baseada na consistência dos scores"""
        try:
            # Remove scores zero (não avaliados)
            valid_scores = [s for s in scores if s > 0]
            
            if len(valid_scores) < 2:
                return 0.5
            
            # Calcula desvio padrão
            mean_score = np.mean(valid_scores)
            std_score = np.std(valid_scores)
            
            # Confiança inversamente proporcional ao desvio
            # Normaliza para 0-1
            confidence = max(0, 1 - (std_score / mean_score) if mean_score > 0 else 0)
            
            return min(1.0, confidence)
            
        except Exception:
            return 0.5
    
    def _estimate_cost(self, query: str, context_chunks: List[str], answer: str) -> float:
        """Estima custo da avaliação em USD"""
        try:
            # Conta tokens aproximadamente
            total_text = query + " ".join(context_chunks) + answer
            estimated_tokens = len(total_text.split()) * 1.3  # Fator de conversão aproximado
            
            # Múltiplas chamadas para diferentes métricas
            total_tokens = estimated_tokens * 6  # ~6 chamadas GPT-5
            
            # Preço estimado GPT-5 Full (hipotético)
            cost_per_1k_tokens = 0.10  # USD
            
            return (total_tokens / 1000) * cost_per_1k_tokens
            
        except Exception:
            return 0.0
    
    def _update_stats(self, scores: QualityScores, processing_time: float, cost: float):
        """Atualiza estatísticas internas"""
        try:
            self._evaluation_stats['total_evaluations'] += 1
            
            # Atualiza tempo médio
            current_avg = self._evaluation_stats['avg_processing_time']
            total_evals = self._evaluation_stats['total_evaluations']
            new_avg = ((current_avg * (total_evals - 1)) + processing_time) / total_evals
            self._evaluation_stats['avg_processing_time'] = new_avg
            
            # Atualiza custo total
            self._evaluation_stats['total_cost'] += cost
            
            # Atualiza distribuição de scores
            self._evaluation_stats['score_distribution']['context_relevance'].append(scores.context_relevance)
            self._evaluation_stats['score_distribution']['faithfulness'].append(scores.faithfulness)
            self._evaluation_stats['score_distribution']['sas'].append(scores.semantic_answer_similarity)
            self._evaluation_stats['score_distribution']['overall'].append(scores.overall_score())
            
            # Mantém apenas últimos 1000 scores
            for metric in self._evaluation_stats['score_distribution']:
                if len(self._evaluation_stats['score_distribution'][metric]) > 1000:
                    self._evaluation_stats['score_distribution'][metric] = \
                        self._evaluation_stats['score_distribution'][metric][-1000:]
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar estatísticas: {str(e)}")
    
    def get_evaluation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de avaliação"""
        try:
            stats = self._evaluation_stats.copy()
            
            # Calcula médias e distribuições
            for metric, scores in stats['score_distribution'].items():
                if scores:
                    stats[f'avg_{metric}'] = np.mean(scores)
                    stats[f'std_{metric}'] = np.std(scores)
                    stats[f'min_{metric}'] = np.min(scores)
                    stats[f'max_{metric}'] = np.max(scores)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}
    
    def _init_prompt_templates(self):
        """Inicializa templates de prompts"""
        self._prompts = {
            'context_relevance': """
Evaluate the relevance of the provided context chunks to the given query.

Query: {query}

Context Chunks:
{context_chunks}

For each chunk, evaluate:
1. How relevant is it to answering the query? (0-1 score)
2. What is its importance weight for this query? (0-1 weight)
3. What specific aspects make it relevant or irrelevant?

Respond with JSON:
{{
  "chunk_evaluations": [
    {{
      "chunk_id": 1,
      "relevance_score": 0.8,
      "importance_weight": 0.9,
      "relevance_explanation": "explanation"
    }}
  ],
  "overall_relevance": 0.75
}}
""",
            
            'faithfulness': """
Evaluate how faithful the answer is to the provided context. Check if the answer makes claims that are supported by the context.

Context Chunks:
{context_chunks}

Answer: {answer}

Analyze:
1. Extract all factual claims from the answer
2. For each claim, check if it's supported by the context
3. Identify any contradictions with the context
4. Identify any unsupported claims

Respond with JSON:
{{
  "claims": [
    {{
      "claim": "specific claim text",
      "supported": true/false,
      "evidence": "supporting text from context or null"
    }}
  ],
  "contradictions": ["contradiction descriptions"],
  "unsupported_claims": ["unsupported claim descriptions"],
  "faithfulness_score": 0.85
}}
""",
            
            'semantic_similarity': """
Evaluate the semantic similarity between the generated answer and the ideal answer.

Generated Answer: {answer}

Ideal Answer: {ideal_answer}

Consider:
1. Semantic meaning and intent
2. Completeness of information
3. Accuracy of details
4. Overall helpfulness

Respond with JSON:
{{
  "similarity_score": 0.8,
  "semantic_alignment": "high/medium/low",
  "key_differences": ["difference descriptions"],
  "missing_information": ["missing info descriptions"],
  "extra_information": ["extra info descriptions"]
}}
""",
            
            'context_precision': """
Evaluate the precision of the context chunks - how many of the provided chunks are actually relevant to the query?

Query: {query}

Context Chunks:
{context_chunks}

For each chunk, determine if it's relevant to answering the query.

Respond with JSON:
{{
  "chunk_relevance": [
    {{
      "chunk_id": 1,
      "is_relevant": true/false,
      "relevance_reason": "explanation"
    }}
  ],
  "precision_score": 0.75
}}
""",
            
            'context_recall': """
Evaluate the recall of the context - does it contain all the necessary information to answer the query comprehensively?

Query: {query}

Context Chunks:
{context_chunks}

Analyze what information is required to fully answer the query and what is actually provided.

Respond with JSON:
{{
  "required_aspects": ["aspect1", "aspect2"],
  "covered_aspects": ["aspect1"],
  "missing_aspects": ["aspect2"],
  "recall_score": 0.5
}}
""",
            
            'answer_correctness': """
Evaluate the factual correctness of the answer based on the provided context.

Context Chunks:
{context_chunks}

Answer: {answer}

Analyze all factual statements in the answer for correctness.

Respond with JSON:
{{
  "factual_statements": [
    {{
      "statement": "factual statement",
      "is_correct": true/false,
      "confidence": 0.9
    }}
  ],
  "serious_errors": ["error descriptions"],
  "minor_inaccuracies": ["inaccuracy descriptions"],
  "correctness_score": 0.85
}}
""",
            
            'answer_completeness': """
Evaluate how complete the answer is in addressing the query.

Query: {query}

Answer: {answer}

Analyze if the answer fully addresses all aspects of the query.

Respond with JSON:
{{
  "aspects_covered": ["covered aspects"],
  "aspects_missing": ["missing aspects"],
  "completeness_score": 0.8,
  "depth_assessment": "superficial/adequate/comprehensive"
}}
""",
            
            'detailed_feedback': """
Provide detailed feedback on the overall quality of this RAG response.

Query: {query}
Context: {context_chunks}
Answer: {answer}
Scores: {scores}

Provide comprehensive feedback covering strengths, weaknesses, and suggestions for improvement.

Respond with JSON:
{{
  "strengths": ["strength descriptions"],
  "weaknesses": ["weakness descriptions"],
  "suggestions": ["improvement suggestions"],
  "quality_assessment": "overall assessment",
  "improvement_areas": ["specific areas to improve"]
}}
"""
        }