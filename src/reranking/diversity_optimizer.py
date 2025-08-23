import logging
import time
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import math
from collections import defaultdict, Counter
import hashlib

@dataclass
class DiversityMetrics:
    """Métricas de diversidade"""
    content_diversity: float
    source_diversity: float
    category_diversity: float
    temporal_diversity: float
    semantic_diversity: float
    overall_diversity: float
    redundancy_score: float
    coverage_score: float

@dataclass
class DiversityAnalysis:
    """Análise de diversidade dos resultados"""
    original_count: int
    optimized_count: int
    removed_duplicates: int
    diversity_metrics: DiversityMetrics
    diversity_explanation: str
    optimization_strategy: str
    analyzed_at: str

class DiversityOptimizer:
    """Otimizador de diversidade para resultados de busca"""
    
    def __init__(self, max_results: int = 8, similarity_threshold: float = 0.85):
        self.logger = logging.getLogger(__name__)
        self.max_results = max_results
        self.similarity_threshold = similarity_threshold
        
        # Pesos para diferentes aspectos da diversidade
        self.diversity_weights = {
            'content': 0.35,
            'source': 0.20,
            'category': 0.20,
            'temporal': 0.15,
            'semantic': 0.10
        }
        
        # Configurações de diversidade
        self.diversity_config = {
            'min_content_similarity': 0.3,  # Mínimo de similaridade para considerar redundante
            'max_same_source': 2,           # Máximo de resultados da mesma fonte
            'prefer_recent': True,          # Preferir conteúdo mais recente
            'balance_categories': True,     # Balancear categorias
            'semantic_clustering': True     # Agrupar semanticamente
        }
        
        # Cache para análises de similaridade
        self._similarity_cache = {}
        
        # Estatísticas
        self._stats = {
            'total_optimizations': 0,
            'total_duplicates_removed': 0,
            'avg_optimization_time': 0,
            'total_optimization_time': 0,
            'diversity_improvements': 0
        }
        
        self.logger.info(f"DiversityOptimizer inicializado (max_results={max_results})")
    
    def optimize_diversity(self, results: List[Dict[str, Any]], 
                          query: str = "") -> Tuple[List[Dict[str, Any]], DiversityAnalysis]:
        """Otimiza diversidade dos resultados removendo redundâncias"""
        start_time = time.time()
        
        try:
            original_count = len(results)
            
            if not results:
                return results, self._create_empty_analysis()
            
            # Análise inicial de diversidade
            initial_metrics = self._calculate_diversity_metrics(results)
            
            # Estratégia de otimização
            strategy = self._determine_optimization_strategy(results, initial_metrics)
            
            # Aplica otimização
            optimized_results = self._apply_optimization_strategy(results, strategy, query)
            
            # Análise final
            final_metrics = self._calculate_diversity_metrics(optimized_results)
            removed_count = original_count - len(optimized_results)
            
            # Gera explicação
            explanation = self._generate_diversity_explanation(
                initial_metrics, final_metrics, removed_count, strategy
            )
            
            # Cria análise
            analysis = DiversityAnalysis(
                original_count=original_count,
                optimized_count=len(optimized_results),
                removed_duplicates=removed_count,
                diversity_metrics=final_metrics,
                diversity_explanation=explanation,
                optimization_strategy=strategy,
                analyzed_at=datetime.now().isoformat()
            )
            
            # Atualiza estatísticas
            optimization_time = time.time() - start_time
            self._update_stats(removed_count, optimization_time, final_metrics.overall_diversity > initial_metrics.overall_diversity)
            
            return optimized_results, analysis
        
        except Exception as e:
            self.logger.error(f"Erro na otimização de diversidade: {str(e)}")
            return results, self._create_fallback_analysis(results)
    
    def _determine_optimization_strategy(self, results: List[Dict[str, Any]], 
                                       metrics: DiversityMetrics) -> str:
        """Determina estratégia de otimização baseada nas métricas"""
        strategies = []
        
        # Verifica redundância de conteúdo
        if metrics.redundancy_score > 0.7:
            strategies.append("content_deduplication")
        
        # Verifica diversidade de fontes
        if metrics.source_diversity < 0.5:
            strategies.append("source_balancing")
        
        # Verifica diversidade de categorias
        if metrics.category_diversity < 0.6:
            strategies.append("category_balancing")
        
        # Verifica diversidade temporal
        if metrics.temporal_diversity < 0.4:
            strategies.append("temporal_balancing")
        
        # Estratégia padrão se nenhuma específica for necessária
        if not strategies:
            strategies.append("general_optimization")
        
        return "+".join(strategies)
    
    def _apply_optimization_strategy(self, results: List[Dict[str, Any]], 
                                   strategy: str, query: str) -> List[Dict[str, Any]]:
        """Aplica estratégia de otimização"""
        optimized = results.copy()
        
        # Remove duplicatas de conteúdo
        if "content_deduplication" in strategy:
            optimized = self._remove_content_duplicates(optimized)
        
        # Balanceia fontes
        if "source_balancing" in strategy:
            optimized = self._balance_sources(optimized)
        
        # Balanceia categorias
        if "category_balancing" in strategy:
            optimized = self._balance_categories(optimized)
        
        # Balanceia temporalmente
        if "temporal_balancing" in strategy:
            optimized = self._balance_temporal(optimized)
        
        # Otimização geral
        if "general_optimization" in strategy:
            optimized = self._general_optimization(optimized, query)
        
        # Limita ao número máximo
        if len(optimized) > self.max_results:
            optimized = self._select_top_diverse(optimized, self.max_results)
        
        return optimized
    
    def _remove_content_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicatas de conteúdo"""
        unique_results = []
        seen_hashes = set()
        
        for result in results:
            chunk = result.get('chunk', '')
            
            # Calcula hash do conteúdo normalizado
            normalized_content = self._normalize_content_for_comparison(chunk)
            content_hash = hashlib.md5(normalized_content.encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_results.append(result)
            else:
                # Verifica se é realmente similar
                is_duplicate = False
                for existing in unique_results:
                    existing_chunk = existing.get('chunk', '')
                    similarity = self._calculate_content_similarity(chunk, existing_chunk)
                    
                    if similarity > self.similarity_threshold:
                        is_duplicate = True
                        # Mantém o resultado com melhor score
                        if result.get('score', 0) > existing.get('score', 0):
                            unique_results.remove(existing)
                            unique_results.append(result)
                        break
                
                if not is_duplicate:
                    unique_results.append(result)
        
        return unique_results
    
    def _balance_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Balanceia resultados por fonte"""
        source_counts = defaultdict(list)
        
        # Agrupa por fonte
        for result in results:
            fonte_url = result.get('fonte', {}).get('url', 'unknown')
            source_counts[fonte_url].append(result)
        
        # Seleciona até max_same_source por fonte
        balanced_results = []
        for fonte_url, fonte_results in source_counts.items():
            # Ordena por score
            fonte_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Pega os melhores até o limite
            selected = fonte_results[:self.diversity_config['max_same_source']]
            balanced_results.extend(selected)
        
        # Ordena por score geral
        balanced_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return balanced_results
    
    def _balance_categories(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Balanceia resultados por categoria"""
        category_counts = defaultdict(list)
        
        # Agrupa por categoria
        for result in results:
            categoria = result.get('metadata', {}).get('categoria', 'unknown')
            category_counts[categoria].append(result)
        
        # Distribui equitativamente
        balanced_results = []
        max_per_category = max(1, self.max_results // len(category_counts))
        
        for categoria, cat_results in category_counts.items():
            # Ordena por score
            cat_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Seleciona até o limite por categoria
            selected = cat_results[:max_per_category]
            balanced_results.extend(selected)
        
        # Se ainda há espaço, adiciona os melhores restantes
        if len(balanced_results) < self.max_results:
            remaining_results = []
            for result in results:
                if result not in balanced_results:
                    remaining_results.append(result)
            
            remaining_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            needed = self.max_results - len(balanced_results)
            balanced_results.extend(remaining_results[:needed])
        
        return balanced_results
    
    def _balance_temporal(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Balanceia resultados temporalmente"""
        if not self.diversity_config['prefer_recent']:
            return results
        
        # Separa por idade
        recent_results = []  # < 6 meses
        older_results = []   # >= 6 meses
        
        for result in results:
            updated_at = result.get('metadata', {}).get('updated_at')
            if updated_at:
                try:
                    from datetime import datetime, timedelta
                    if isinstance(updated_at, str):
                        updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    else:
                        updated_date = updated_at
                    
                    six_months_ago = datetime.now(updated_date.tzinfo) - timedelta(days=180)
                    
                    if updated_date >= six_months_ago:
                        recent_results.append(result)
                    else:
                        older_results.append(result)
                except:
                    older_results.append(result)
            else:
                older_results.append(result)
        
        # Prioriza conteúdo recente (70% recente, 30% antigo)
        recent_count = int(self.max_results * 0.7)
        older_count = self.max_results - recent_count
        
        # Ordena por score
        recent_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        older_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Seleciona
        balanced = recent_results[:recent_count] + older_results[:older_count]
        
        # Se não há suficientes recentes, completa com antigos
        if len(recent_results) < recent_count:
            needed = recent_count - len(recent_results)
            balanced.extend(older_results[older_count:older_count + needed])
        
        return balanced
    
    def _general_optimization(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Otimização geral de diversidade"""
        if len(results) <= self.max_results:
            return results
        
        # Algoritmo de seleção diversa
        selected = []
        remaining = results.copy()
        
        # Seleciona o primeiro (melhor score)
        remaining.sort(key=lambda x: x.get('score', 0), reverse=True)
        selected.append(remaining.pop(0))
        
        # Seleciona os demais maximizando diversidade
        while len(selected) < self.max_results and remaining:
            best_candidate = None
            best_diversity_score = -1
            
            for candidate in remaining:
                # Calcula diversidade em relação aos já selecionados
                diversity_score = self._calculate_candidate_diversity(candidate, selected)
                
                # Combina com score original
                combined_score = 0.7 * candidate.get('score', 0) + 0.3 * diversity_score
                
                if combined_score > best_diversity_score:
                    best_diversity_score = combined_score
                    best_candidate = candidate
            
            if best_candidate:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
            else:
                break
        
        return selected
    
    def _select_top_diverse(self, results: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
        """Seleciona os top N mais diversos"""
        if len(results) <= count:
            return results
        
        # Usa algoritmo guloso para seleção diversa
        selected = []
        remaining = results.copy()
        
        # Ordena por score
        remaining.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Seleciona o primeiro
        selected.append(remaining.pop(0))
        
        # Seleciona os demais
        while len(selected) < count and remaining:
            best_candidate = None
            best_score = -1
            
            for candidate in remaining:
                # Score de diversidade
                diversity = self._calculate_candidate_diversity(candidate, selected)
                # Score combinado
                combined = 0.6 * candidate.get('score', 0) + 0.4 * diversity
                
                if combined > best_score:
                    best_score = combined
                    best_candidate = candidate
            
            if best_candidate:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
            else:
                break
        
        return selected
    
    def _calculate_candidate_diversity(self, candidate: Dict[str, Any], 
                                     selected: List[Dict[str, Any]]) -> float:
        """Calcula diversidade de um candidato em relação aos selecionados"""
        if not selected:
            return 1.0
        
        diversities = []
        
        for selected_result in selected:
            # Diversidade de conteúdo
            content_div = 1.0 - self._calculate_content_similarity(
                candidate.get('chunk', ''),
                selected_result.get('chunk', '')
            )
            
            # Diversidade de fonte
            source_div = 1.0 if (candidate.get('fonte', {}).get('url') != 
                               selected_result.get('fonte', {}).get('url')) else 0.0
            
            # Diversidade de categoria
            category_div = 1.0 if (candidate.get('metadata', {}).get('categoria') != 
                                 selected_result.get('metadata', {}).get('categoria')) else 0.0
            
            # Combina diversidades
            combined_div = (
                content_div * 0.5 +
                source_div * 0.3 +
                category_div * 0.2
            )
            
            diversities.append(combined_div)
        
        # Retorna diversidade mínima (mais conservadora)
        return min(diversities)
    
    def _calculate_diversity_metrics(self, results: List[Dict[str, Any]]) -> DiversityMetrics:
        """Calcula métricas de diversidade"""
        if not results:
            return DiversityMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        
        # Diversidade de conteúdo
        content_diversity = self._calculate_content_diversity(results)
        
        # Diversidade de fontes
        source_diversity = self._calculate_source_diversity(results)
        
        # Diversidade de categorias
        category_diversity = self._calculate_category_diversity(results)
        
        # Diversidade temporal
        temporal_diversity = self._calculate_temporal_diversity(results)
        
        # Diversidade semântica
        semantic_diversity = self._calculate_semantic_diversity(results)
        
        # Score de redundância
        redundancy_score = self._calculate_redundancy_score(results)
        
        # Score de cobertura
        coverage_score = self._calculate_coverage_score(results)
        
        # Diversidade geral
        overall_diversity = (
            content_diversity * self.diversity_weights['content'] +
            source_diversity * self.diversity_weights['source'] +
            category_diversity * self.diversity_weights['category'] +
            temporal_diversity * self.diversity_weights['temporal'] +
            semantic_diversity * self.diversity_weights['semantic']
        )
        
        return DiversityMetrics(
            content_diversity=content_diversity,
            source_diversity=source_diversity,
            category_diversity=category_diversity,
            temporal_diversity=temporal_diversity,
            semantic_diversity=semantic_diversity,
            overall_diversity=overall_diversity,
            redundancy_score=redundancy_score,
            coverage_score=coverage_score
        )
    
    def _calculate_content_diversity(self, results: List[Dict[str, Any]]) -> float:
        """Calcula diversidade de conteúdo"""
        if len(results) <= 1:
            return 1.0
        
        similarities = []
        
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                chunk1 = results[i].get('chunk', '')
                chunk2 = results[j].get('chunk', '')
                similarity = self._calculate_content_similarity(chunk1, chunk2)
                similarities.append(similarity)
        
        if not similarities:
            return 1.0
        
        avg_similarity = sum(similarities) / len(similarities)
        return 1.0 - avg_similarity
    
    def _calculate_source_diversity(self, results: List[Dict[str, Any]]) -> float:
        """Calcula diversidade de fontes"""
        sources = set()
        for result in results:
            fonte_url = result.get('fonte', {}).get('url', 'unknown')
            sources.add(fonte_url)
        
        # Diversidade = número de fontes únicas / número total de resultados
        return len(sources) / len(results) if results else 0
    
    def _calculate_category_diversity(self, results: List[Dict[str, Any]]) -> float:
        """Calcula diversidade de categorias"""
        categories = set()
        for result in results:
            categoria = result.get('metadata', {}).get('categoria', 'unknown')
            categories.add(categoria)
        
        return len(categories) / len(results) if results else 0
    
    def _calculate_temporal_diversity(self, results: List[Dict[str, Any]]) -> float:
        """Calcula diversidade temporal"""
        dates = []
        
        for result in results:
            updated_at = result.get('metadata', {}).get('updated_at')
            if updated_at:
                try:
                    from datetime import datetime
                    if isinstance(updated_at, str):
                        date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    else:
                        date = updated_at
                    dates.append(date)
                except:
                    continue
        
        if len(dates) <= 1:
            return 0.5
        
        # Calcula dispersão temporal
        dates.sort()
        total_span = (dates[-1] - dates[0]).days
        
        if total_span == 0:
            return 0.0
        
        # Normaliza para 0-1 (considera 2 anos como máxima diversidade)
        max_span_days = 730  # 2 anos
        return min(1.0, total_span / max_span_days)
    
    def _calculate_semantic_diversity(self, results: List[Dict[str, Any]]) -> float:
        """Calcula diversidade semântica"""
        # Simplificado: baseado na diversidade de termos técnicos
        all_terms = set()
        
        for result in results:
            chunk = result.get('chunk', '').lower()
            terms = re.findall(r'\b\w+\b', chunk)
            # Filtra termos técnicos (palavras com mais de 4 caracteres)
            tech_terms = [term for term in terms if len(term) > 4]
            all_terms.update(tech_terms)
        
        # Diversidade baseada na riqueza de vocabulário
        total_words = sum(len(re.findall(r'\b\w+\b', result.get('chunk', ''))) 
                         for result in results)
        
        if total_words == 0:
            return 0.5
        
        return min(1.0, len(all_terms) / (total_words * 0.1))
    
    def _calculate_redundancy_score(self, results: List[Dict[str, Any]]) -> float:
        """Calcula score de redundância"""
        if len(results) <= 1:
            return 0.0
        
        redundant_pairs = 0
        total_pairs = 0
        
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                chunk1 = results[i].get('chunk', '')
                chunk2 = results[j].get('chunk', '')
                similarity = self._calculate_content_similarity(chunk1, chunk2)
                
                if similarity > self.similarity_threshold:
                    redundant_pairs += 1
                
                total_pairs += 1
        
        return redundant_pairs / total_pairs if total_pairs > 0 else 0.0
    
    def _calculate_coverage_score(self, results: List[Dict[str, Any]]) -> float:
        """Calcula score de cobertura de tópicos"""
        # Simplificado: baseado na diversidade de categorias e fontes
        categories = set(result.get('metadata', {}).get('categoria', 'unknown') 
                        for result in results)
        sources = set(result.get('fonte', {}).get('url', 'unknown') 
                     for result in results)
        
        # Score baseado na diversidade
        category_coverage = len(categories) / max(1, len(results))
        source_coverage = len(sources) / max(1, len(results))
        
        return (category_coverage + source_coverage) / 2
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calcula similaridade entre dois conteúdos"""
        # Cache key
        cache_key = hashlib.md5(f"{content1}|{content2}".encode()).hexdigest()
        
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        # Normaliza conteúdos
        norm1 = self._normalize_content_for_comparison(content1)
        norm2 = self._normalize_content_for_comparison(content2)
        
        if not norm1 or not norm2:
            similarity = 0.0
        else:
            # Similaridade baseada em Jaccard de n-gramas
            similarity = self._jaccard_similarity(norm1, norm2)
        
        # Cache resultado
        self._similarity_cache[cache_key] = similarity
        
        return similarity
    
    def _normalize_content_for_comparison(self, content: str) -> str:
        """Normaliza conteúdo para comparação"""
        # Remove HTML/Markdown
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        content = re.sub(r'`([^`]+)`', r'\1', content)
        
        # Remove caracteres especiais e normaliza espaços
        content = re.sub(r'[^\w\s]', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.lower().strip()
    
    def _jaccard_similarity(self, text1: str, text2: str, n: int = 3) -> float:
        """Calcula similaridade Jaccard de n-gramas"""
        def get_ngrams(text: str, n: int) -> Set[str]:
            words = text.split()
            return set(' '.join(words[i:i+n]) for i in range(len(words)-n+1))
        
        ngrams1 = get_ngrams(text1, n)
        ngrams2 = get_ngrams(text2, n)
        
        if not ngrams1 and not ngrams2:
            return 1.0
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1.intersection(ngrams2))
        union = len(ngrams1.union(ngrams2))
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_diversity_explanation(self, initial_metrics: DiversityMetrics,
                                      final_metrics: DiversityMetrics,
                                      removed_count: int, strategy: str) -> str:
        """Gera explicação da otimização de diversidade"""
        explanation_parts = []
        
        # Resultados removidos
        if removed_count > 0:
            explanation_parts.append(f"Removidos {removed_count} resultados redundantes")
        
        # Melhoria na diversidade
        diversity_improvement = final_metrics.overall_diversity - initial_metrics.overall_diversity
        if diversity_improvement > 0.1:
            explanation_parts.append(f"Diversidade melhorada em {diversity_improvement:.1%}")
        
        # Estratégia aplicada
        strategy_descriptions = {
            'content_deduplication': 'remoção de duplicatas',
            'source_balancing': 'balanceamento de fontes',
            'category_balancing': 'balanceamento de categorias',
            'temporal_balancing': 'balanceamento temporal',
            'general_optimization': 'otimização geral'
        }
        
        applied_strategies = []
        for strategy_key, description in strategy_descriptions.items():
            if strategy_key in strategy:
                applied_strategies.append(description)
        
        if applied_strategies:
            explanation_parts.append(f"Estratégias: {', '.join(applied_strategies)}")
        
        # Métricas finais
        if final_metrics.overall_diversity >= 0.8:
            explanation_parts.append("Alta diversidade alcançada")
        elif final_metrics.overall_diversity >= 0.6:
            explanation_parts.append("Boa diversidade alcançada")
        else:
            explanation_parts.append("Diversidade moderada")
        
        return ". ".join(explanation_parts) + "."
    
    def _create_empty_analysis(self) -> DiversityAnalysis:
        """Cria análise vazia"""
        empty_metrics = DiversityMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        
        return DiversityAnalysis(
            original_count=0,
            optimized_count=0,
            removed_duplicates=0,
            diversity_metrics=empty_metrics,
            diversity_explanation="Nenhum resultado para otimizar",
            optimization_strategy="none",
            analyzed_at=datetime.now().isoformat()
        )
    
    def _create_fallback_analysis(self, results: List[Dict[str, Any]]) -> DiversityAnalysis:
        """Cria análise de fallback em caso de erro"""
        fallback_metrics = DiversityMetrics(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
        
        return DiversityAnalysis(
            original_count=len(results),
            optimized_count=len(results),
            removed_duplicates=0,
            diversity_metrics=fallback_metrics,
            diversity_explanation="Erro na otimização - resultados mantidos",
            optimization_strategy="fallback",
            analyzed_at=datetime.now().isoformat()
        )
    
    def _update_stats(self, removed_count: int, optimization_time: float, improved: bool):
        """Atualiza estatísticas"""
        self._stats['total_optimizations'] += 1
        self._stats['total_duplicates_removed'] += removed_count
        self._stats['total_optimization_time'] += optimization_time
        self._stats['avg_optimization_time'] = (
            self._stats['total_optimization_time'] / self._stats['total_optimizations']
        )
        
        if improved:
            self._stats['diversity_improvements'] += 1
    
    def get_diversity_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de diversidade"""
        stats = self._stats.copy()
        
        if stats['total_optimizations'] > 0:
            stats['avg_duplicates_per_optimization'] = (
                stats['total_duplicates_removed'] / stats['total_optimizations']
            )
            stats['improvement_rate'] = (
                stats['diversity_improvements'] / stats['total_optimizations']
            )
        
        return stats
    
    def update_config(self, new_config: Dict[str, Any]):
        """Atualiza configuração de diversidade"""
        self.diversity_config.update(new_config)
        self.logger.info(f"Configuração de diversidade atualizada: {self.diversity_config}")
    
    def clear_cache(self):
        """Limpa cache de similaridade"""
        self._similarity_cache.clear()
        self.logger.info("Cache de similaridade limpo")