import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import math
from collections import Counter

@dataclass
class RelevanceScore:
    """Score de relevância detalhado"""
    overall_score: float
    semantic_score: float
    keyword_score: float
    context_score: float
    quality_score: float
    freshness_score: float
    authority_score: float
    breakdown: Dict[str, float]
    confidence: float

@dataclass
class RelevanceAnalysis:
    """Análise completa de relevância"""
    query: str
    result_id: str
    relevance_score: RelevanceScore
    matching_terms: List[str]
    missing_terms: List[str]
    context_matches: List[str]
    quality_indicators: List[str]
    relevance_explanation: str
    analyzed_at: str

class RelevanceEvaluator:
    """Avaliador de relevância para resultados de busca"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pesos para diferentes aspectos da relevância
        self.relevance_weights = {
            'semantic': 0.30,
            'keyword': 0.25,
            'context': 0.20,
            'quality': 0.15,
            'freshness': 0.05,
            'authority': 0.05
        }
        
        # Termos técnicos importantes por categoria
        self.technical_terms = {
            'ui': ['component', 'props', 'styling', 'theme', 'design', 'accessibility', 'responsive'],
            'react': ['hook', 'state', 'effect', 'component', 'jsx', 'props', 'context'],
            'nextjs': ['page', 'route', 'api', 'middleware', 'server', 'client', 'build'],
            'tailwind': ['class', 'utility', 'responsive', 'variant', 'modifier', 'config'],
            'auth': ['login', 'session', 'token', 'oauth', 'jwt', 'security', 'permission'],
            'database': ['query', 'schema', 'migration', 'relation', 'model', 'orm']
        }
        
        # Indicadores de qualidade
        self.quality_indicators = {
            'positive': [
                'example', 'tutorial', 'guide', 'documentation', 'official',
                'best practice', 'recommended', 'updated', 'latest', 'stable'
            ],
            'negative': [
                'deprecated', 'outdated', 'experimental', 'alpha', 'beta',
                'unstable', 'legacy', 'old version'
            ]
        }
        
        # Fontes autoritativas
        self.authoritative_sources = {
            'official': ['docs.', 'documentation', 'github.com', 'npmjs.com'],
            'community': ['stackoverflow.com', 'dev.to', 'medium.com'],
            'tutorial': ['tutorial', 'guide', 'learn', 'course']
        }
        
        # Estatísticas
        self._stats = {
            'total_evaluations': 0,
            'avg_evaluation_time': 0,
            'total_evaluation_time': 0,
            'score_distribution': {
                'high': 0,    # > 0.8
                'medium': 0,  # 0.5 - 0.8
                'low': 0      # < 0.5
            }
        }
        
        self.logger.info("RelevanceEvaluator inicializado")
    
    def evaluate_relevance(self, query: str, result: Dict[str, Any], 
                          context: Optional[Dict[str, Any]] = None) -> RelevanceAnalysis:
        """Avalia relevância de um resultado para uma query"""
        start_time = time.time()
        
        try:
            # Extrai informações do resultado
            chunk = result.get('chunk', '')
            metadata = result.get('metadata', {})
            fonte = result.get('fonte', {})
            
            # Calcula scores individuais
            semantic_score = self._calculate_semantic_score(query, chunk, metadata)
            keyword_score = self._calculate_keyword_score(query, chunk)
            context_score = self._calculate_context_score(query, metadata, context)
            quality_score = self._calculate_quality_score(chunk, fonte, metadata)
            freshness_score = self._calculate_freshness_score(metadata)
            authority_score = self._calculate_authority_score(fonte)
            
            # Calcula score geral
            overall_score = (
                semantic_score * self.relevance_weights['semantic'] +
                keyword_score * self.relevance_weights['keyword'] +
                context_score * self.relevance_weights['context'] +
                quality_score * self.relevance_weights['quality'] +
                freshness_score * self.relevance_weights['freshness'] +
                authority_score * self.relevance_weights['authority']
            )
            
            # Cria breakdown detalhado
            breakdown = {
                'semantic': semantic_score,
                'keyword': keyword_score,
                'context': context_score,
                'quality': quality_score,
                'freshness': freshness_score,
                'authority': authority_score
            }
            
            # Calcula confiança
            confidence = self._calculate_confidence(breakdown)
            
            # Cria score de relevância
            relevance_score = RelevanceScore(
                overall_score=overall_score,
                semantic_score=semantic_score,
                keyword_score=keyword_score,
                context_score=context_score,
                quality_score=quality_score,
                freshness_score=freshness_score,
                authority_score=authority_score,
                breakdown=breakdown,
                confidence=confidence
            )
            
            # Análise de termos
            matching_terms = self._find_matching_terms(query, chunk)
            missing_terms = self._find_missing_terms(query, chunk)
            context_matches = self._find_context_matches(query, metadata, context)
            quality_indicators = self._find_quality_indicators(chunk, fonte)
            
            # Gera explicação
            explanation = self._generate_explanation(
                relevance_score, matching_terms, missing_terms, context_matches
            )
            
            # Cria análise completa
            analysis = RelevanceAnalysis(
                query=query,
                result_id=metadata.get('chunk_id', 'unknown'),
                relevance_score=relevance_score,
                matching_terms=matching_terms,
                missing_terms=missing_terms,
                context_matches=context_matches,
                quality_indicators=quality_indicators,
                relevance_explanation=explanation,
                analyzed_at=datetime.now().isoformat()
            )
            
            # Atualiza estatísticas
            evaluation_time = time.time() - start_time
            self._update_stats(overall_score, evaluation_time)
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"Erro na avaliação de relevância: {str(e)}")
            # Retorna análise básica em caso de erro
            return self._create_fallback_analysis(query, result)
    
    def evaluate_batch_relevance(self, query: str, results: List[Dict[str, Any]],
                               context: Optional[Dict[str, Any]] = None) -> List[RelevanceAnalysis]:
        """Avalia relevância para múltiplos resultados"""
        try:
            self.logger.info(f"Avaliando relevância para {len(results)} resultados")
            
            analyses = []
            for result in results:
                analysis = self.evaluate_relevance(query, result, context)
                analyses.append(analysis)
            
            return analyses
        
        except Exception as e:
            self.logger.error(f"Erro na avaliação em lote: {str(e)}")
            return [
                self._create_fallback_analysis(query, result)
                for result in results
            ]
    
    def _calculate_semantic_score(self, query: str, chunk: str, metadata: Dict[str, Any]) -> float:
        """Calcula score semântico baseado em correspondência conceitual"""
        try:
            # Normaliza textos
            query_lower = query.lower()
            chunk_lower = chunk.lower()
            
            # Extrai conceitos principais da query
            query_concepts = self._extract_concepts(query_lower)
            chunk_concepts = self._extract_concepts(chunk_lower)
            
            # Calcula sobreposição conceitual
            if not query_concepts:
                return 0.5
            
            concept_overlap = len(query_concepts.intersection(chunk_concepts)) / len(query_concepts)
            
            # Considera metadados
            metadata_boost = 0
            stack = metadata.get('stack', '').lower()
            categoria = metadata.get('categoria', '').lower()
            
            if stack in query_lower:
                metadata_boost += 0.2
            if categoria in query_lower:
                metadata_boost += 0.1
            
            # Score final
            semantic_score = min(1.0, concept_overlap + metadata_boost)
            
            return semantic_score
        
        except Exception as e:
            self.logger.warning(f"Erro no cálculo semântico: {str(e)}")
            return 0.5
    
    def _calculate_keyword_score(self, query: str, chunk: str) -> float:
        """Calcula score baseado em correspondência de palavras-chave"""
        try:
            # Normaliza e tokeniza
            query_words = set(re.findall(r'\b\w+\b', query.lower()))
            chunk_words = set(re.findall(r'\b\w+\b', chunk.lower()))
            
            # Remove stop words comuns
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            query_words -= stop_words
            chunk_words -= stop_words
            
            if not query_words:
                return 0.5
            
            # Calcula correspondência exata
            exact_matches = len(query_words.intersection(chunk_words))
            exact_score = exact_matches / len(query_words)
            
            # Calcula correspondência parcial (substring)
            partial_matches = 0
            for query_word in query_words:
                if any(query_word in chunk_word or chunk_word in query_word 
                      for chunk_word in chunk_words):
                    partial_matches += 1
            
            partial_score = partial_matches / len(query_words)
            
            # Combina scores (peso maior para correspondência exata)
            keyword_score = 0.7 * exact_score + 0.3 * partial_score
            
            return min(1.0, keyword_score)
        
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de keywords: {str(e)}")
            return 0.5
    
    def _calculate_context_score(self, query: str, metadata: Dict[str, Any], 
                               context: Optional[Dict[str, Any]]) -> float:
        """Calcula score baseado no contexto do projeto"""
        try:
            score = 0.5  # Score base
            
            # Contexto da query
            query_lower = query.lower()
            
            # Verifica stack
            stack = metadata.get('stack', '').lower()
            if context and context.get('stack'):
                target_stack = context['stack'].lower()
                if stack == target_stack:
                    score += 0.3
                elif stack in target_stack or target_stack in stack:
                    score += 0.2
            
            # Verifica categoria
            categoria = metadata.get('categoria', '').lower()
            if context and context.get('categoria'):
                target_categoria = context['categoria'].lower()
                if categoria == target_categoria:
                    score += 0.2
                elif categoria in target_categoria or target_categoria in categoria:
                    score += 0.1
            
            # Verifica termos técnicos relevantes
            for tech_area, terms in self.technical_terms.items():
                if tech_area in query_lower or tech_area in stack:
                    chunk_text = metadata.get('chunk', '').lower()
                    matching_terms = sum(1 for term in terms if term in chunk_text)
                    if matching_terms > 0:
                        score += min(0.2, matching_terms * 0.05)
            
            return min(1.0, score)
        
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de contexto: {str(e)}")
            return 0.5
    
    def _calculate_quality_score(self, chunk: str, fonte: Dict[str, Any], 
                               metadata: Dict[str, Any]) -> float:
        """Calcula score de qualidade do conteúdo"""
        try:
            score = 0.5  # Score base
            
            chunk_lower = chunk.lower()
            
            # Indicadores positivos
            positive_count = sum(
                1 for indicator in self.quality_indicators['positive']
                if indicator in chunk_lower
            )
            score += min(0.3, positive_count * 0.1)
            
            # Indicadores negativos
            negative_count = sum(
                1 for indicator in self.quality_indicators['negative']
                if indicator in chunk_lower
            )
            score -= min(0.3, negative_count * 0.15)
            
            # Qualidade da fonte
            fonte_title = fonte.get('title', '').lower()
            if 'official' in fonte_title or 'documentation' in fonte_title:
                score += 0.2
            
            # Score de qualidade dos metadados
            quality_score = metadata.get('quality_score', 0.5)
            score += (quality_score - 0.5) * 0.2
            
            # Comprimento do conteúdo (nem muito curto nem muito longo)
            content_length = len(chunk)
            if 200 <= content_length <= 1000:
                score += 0.1
            elif content_length < 100:
                score -= 0.1
            
            return max(0.0, min(1.0, score))
        
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de qualidade: {str(e)}")
            return 0.5
    
    def _calculate_freshness_score(self, metadata: Dict[str, Any]) -> float:
        """Calcula score baseado na atualidade do conteúdo"""
        try:
            updated_at = metadata.get('updated_at')
            if not updated_at:
                return 0.5
            
            # Converte para datetime se for string
            if isinstance(updated_at, str):
                try:
                    from datetime import datetime
                    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                except:
                    return 0.5
            else:
                updated_date = updated_at
            
            # Calcula idade em dias
            now = datetime.now(updated_date.tzinfo) if updated_date.tzinfo else datetime.now()
            age_days = (now - updated_date).days
            
            # Score baseado na idade
            if age_days <= 30:      # Muito recente
                return 1.0
            elif age_days <= 90:    # Recente
                return 0.8
            elif age_days <= 180:   # Moderadamente recente
                return 0.6
            elif age_days <= 365:   # Um ano
                return 0.4
            else:                   # Antigo
                return 0.2
        
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de freshness: {str(e)}")
            return 0.5
    
    def _calculate_authority_score(self, fonte: Dict[str, Any]) -> float:
        """Calcula score baseado na autoridade da fonte"""
        try:
            url = fonte.get('url', '').lower()
            title = fonte.get('title', '').lower()
            
            score = 0.5  # Score base
            
            # Fontes oficiais
            for pattern in self.authoritative_sources['official']:
                if pattern in url or pattern in title:
                    score += 0.3
                    break
            
            # Fontes da comunidade
            for pattern in self.authoritative_sources['community']:
                if pattern in url:
                    score += 0.2
                    break
            
            # Tutoriais e guias
            for pattern in self.authoritative_sources['tutorial']:
                if pattern in title:
                    score += 0.1
                    break
            
            return min(1.0, score)
        
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de autoridade: {str(e)}")
            return 0.5
    
    def _extract_concepts(self, text: str) -> set:
        """Extrai conceitos principais do texto"""
        # Palavras técnicas importantes
        technical_words = set()
        for terms in self.technical_terms.values():
            technical_words.update(terms)
        
        # Encontra palavras técnicas no texto
        words = set(re.findall(r'\b\w+\b', text.lower()))
        concepts = words.intersection(technical_words)
        
        # Adiciona palavras importantes (substantivos técnicos)
        important_patterns = [
            r'\b\w*component\w*\b', r'\b\w*hook\w*\b', r'\b\w*api\w*\b',
            r'\b\w*config\w*\b', r'\b\w*style\w*\b', r'\b\w*theme\w*\b'
        ]
        
        for pattern in important_patterns:
            matches = re.findall(pattern, text)
            concepts.update(matches)
        
        return concepts
    
    def _find_matching_terms(self, query: str, chunk: str) -> List[str]:
        """Encontra termos da query que aparecem no chunk"""
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        chunk_words = set(re.findall(r'\b\w+\b', chunk.lower()))
        
        return list(query_words.intersection(chunk_words))
    
    def _find_missing_terms(self, query: str, chunk: str) -> List[str]:
        """Encontra termos da query que NÃO aparecem no chunk"""
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        chunk_words = set(re.findall(r'\b\w+\b', chunk.lower()))
        
        # Remove stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        missing = query_words - chunk_words - stop_words
        
        return list(missing)
    
    def _find_context_matches(self, query: str, metadata: Dict[str, Any], 
                            context: Optional[Dict[str, Any]]) -> List[str]:
        """Encontra correspondências contextuais"""
        matches = []
        
        if context:
            stack = metadata.get('stack', '')
            if context.get('stack') and stack.lower() == context['stack'].lower():
                matches.append(f"Stack match: {stack}")
            
            categoria = metadata.get('categoria', '')
            if context.get('categoria') and categoria.lower() == context['categoria'].lower():
                matches.append(f"Category match: {categoria}")
        
        return matches
    
    def _find_quality_indicators(self, chunk: str, fonte: Dict[str, Any]) -> List[str]:
        """Encontra indicadores de qualidade"""
        indicators = []
        
        chunk_lower = chunk.lower()
        
        # Indicadores positivos
        for indicator in self.quality_indicators['positive']:
            if indicator in chunk_lower:
                indicators.append(f"Positive: {indicator}")
        
        # Indicadores negativos
        for indicator in self.quality_indicators['negative']:
            if indicator in chunk_lower:
                indicators.append(f"Negative: {indicator}")
        
        # Fonte oficial
        fonte_url = fonte.get('url', '').lower()
        if any(pattern in fonte_url for pattern in self.authoritative_sources['official']):
            indicators.append("Official source")
        
        return indicators
    
    def _calculate_confidence(self, breakdown: Dict[str, float]) -> float:
        """Calcula confiança na avaliação"""
        # Confiança baseada na consistência dos scores
        scores = list(breakdown.values())
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        # Confiança inversamente proporcional à variância
        confidence = max(0.3, 1.0 - variance)
        
        return confidence
    
    def _generate_explanation(self, relevance_score: RelevanceScore, 
                            matching_terms: List[str], missing_terms: List[str],
                            context_matches: List[str]) -> str:
        """Gera explicação da relevância"""
        explanation_parts = []
        
        # Score geral
        if relevance_score.overall_score >= 0.8:
            explanation_parts.append("Alta relevância")
        elif relevance_score.overall_score >= 0.6:
            explanation_parts.append("Boa relevância")
        elif relevance_score.overall_score >= 0.4:
            explanation_parts.append("Relevância moderada")
        else:
            explanation_parts.append("Baixa relevância")
        
        # Termos correspondentes
        if matching_terms:
            explanation_parts.append(f"Termos encontrados: {', '.join(matching_terms[:3])}")
        
        # Contexto
        if context_matches:
            explanation_parts.append(f"Contexto: {', '.join(context_matches)}")
        
        # Aspectos fortes
        strong_aspects = []
        for aspect, score in relevance_score.breakdown.items():
            if score >= 0.8:
                strong_aspects.append(aspect)
        
        if strong_aspects:
            explanation_parts.append(f"Pontos fortes: {', '.join(strong_aspects)}")
        
        return ". ".join(explanation_parts) + "."
    
    def _create_fallback_analysis(self, query: str, result: Dict[str, Any]) -> RelevanceAnalysis:
        """Cria análise básica em caso de erro"""
        metadata = result.get('metadata', {})
        
        fallback_score = RelevanceScore(
            overall_score=0.5,
            semantic_score=0.5,
            keyword_score=0.5,
            context_score=0.5,
            quality_score=0.5,
            freshness_score=0.5,
            authority_score=0.5,
            breakdown={'error': 0.5},
            confidence=0.3
        )
        
        return RelevanceAnalysis(
            query=query,
            result_id=metadata.get('chunk_id', 'unknown'),
            relevance_score=fallback_score,
            matching_terms=[],
            missing_terms=[],
            context_matches=[],
            quality_indicators=[],
            relevance_explanation="Análise com erro - score padrão aplicado",
            analyzed_at=datetime.now().isoformat()
        )
    
    def _update_stats(self, score: float, evaluation_time: float):
        """Atualiza estatísticas"""
        self._stats['total_evaluations'] += 1
        self._stats['total_evaluation_time'] += evaluation_time
        self._stats['avg_evaluation_time'] = (
            self._stats['total_evaluation_time'] / self._stats['total_evaluations']
        )
        
        # Distribuição de scores
        if score >= 0.8:
            self._stats['score_distribution']['high'] += 1
        elif score >= 0.5:
            self._stats['score_distribution']['medium'] += 1
        else:
            self._stats['score_distribution']['low'] += 1
    
    def get_relevance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de avaliação"""
        return self._stats.copy()
    
    def update_weights(self, new_weights: Dict[str, float]):
        """Atualiza pesos dos aspectos de relevância"""
        # Valida que os pesos somam 1.0
        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Pesos devem somar 1.0, atual: {total_weight}")
        
        self.relevance_weights.update(new_weights)
        self.logger.info(f"Pesos de relevância atualizados: {self.relevance_weights}")