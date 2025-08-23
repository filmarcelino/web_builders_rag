#!/usr/bin/env python3
"""
Source Analyzer - Analisador de Fontes

Este módulo analisa a utilidade e relevância das fontes no sistema RAG,
identificando fontes obsoletas, úteis e sugerindo melhorias.
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict, Counter
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@dataclass
class SourceMetrics:
    """Métricas de uma fonte específica"""
    source_id: str
    url: str
    title: str
    category: str
    usage_count: int = 0
    last_accessed: Optional[str] = None
    relevance_score: float = 0.0
    freshness_score: float = 0.0
    quality_score: float = 0.0
    overall_score: float = 0.0
    access_frequency: float = 0.0  # acessos por dia
    user_feedback: List[Dict[str, Any]] = field(default_factory=list)
    content_age_days: int = 0
    last_updated: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    
@dataclass
class SourceAnalysisReport:
    """Relatório de análise de fontes"""
    generated_at: str
    total_sources: int
    active_sources: int
    obsolete_sources: int
    high_value_sources: int
    low_value_sources: int
    source_metrics: Dict[str, SourceMetrics]
    recommendations: List[str] = field(default_factory=list)
    obsolete_candidates: List[str] = field(default_factory=list)
    improvement_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    
class SourceAnalyzer:
    """Analisador de fontes para identificar utilidade e obsolescência"""
    
    def __init__(self, data_dir: str = "data/governance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações de análise
        self.obsolescence_threshold_days = 365  # 1 ano sem acesso
        self.low_usage_threshold = 5  # menos de 5 acessos
        self.min_relevance_score = 0.3
        self.analysis_window_days = 90
        
        # Dados de análise
        self.source_metrics: Dict[str, SourceMetrics] = {}
        self.access_history: List[Dict[str, Any]] = []
        self.feedback_history: List[Dict[str, Any]] = []
        
        # Padrões para detectar tecnologias obsoletas
        self.obsolete_patterns = {
            "jquery": {"patterns": [r"jquery", r"\$\("], "severity": "medium"},
            "bower": {"patterns": [r"bower"], "severity": "high"},
            "grunt": {"patterns": [r"grunt"], "severity": "medium"},
            "gulp": {"patterns": [r"gulp"], "severity": "low"},
            "angular_js": {"patterns": [r"angular\.js", r"angularjs"], "severity": "high"},
            "backbone": {"patterns": [r"backbone\.js"], "severity": "high"},
            "ember": {"patterns": [r"ember\.js"], "severity": "medium"},
            "coffeescript": {"patterns": [r"coffeescript"], "severity": "high"},
            "less": {"patterns": [r"less css", r"\.less"], "severity": "medium"},
            "stylus": {"patterns": [r"stylus"], "severity": "medium"},
            "webpack_v1": {"patterns": [r"webpack.*1\."], "severity": "high"},
            "node_v10": {"patterns": [r"node.*10\.", r"nodejs.*10\."], "severity": "high"},
            "python_v2": {"patterns": [r"python.*2\.", r"python2"], "severity": "high"}
        }
        
        # Padrões para detectar tecnologias modernas
        self.modern_patterns = {
            "react_18": {"patterns": [r"react.*18", r"react.*concurrent"], "boost": 0.2},
            "nextjs_13": {"patterns": [r"next.*13", r"app directory"], "boost": 0.2},
            "typescript": {"patterns": [r"typescript", r"\.ts", r"\.tsx"], "boost": 0.15},
            "tailwind": {"patterns": [r"tailwind"], "boost": 0.1},
            "vite": {"patterns": [r"vite"], "boost": 0.1},
            "pnpm": {"patterns": [r"pnpm"], "boost": 0.05},
            "bun": {"patterns": [r"bun"], "boost": 0.1}
        }
        
        self._load_analysis_data()
    
    def record_source_access(self, source_id: str, query: str, relevance_score: float, 
                           user_feedback: Optional[Dict[str, Any]] = None) -> None:
        """Registra acesso a uma fonte"""
        try:
            access_record = {
                "timestamp": datetime.now().isoformat(),
                "source_id": source_id,
                "query": query,
                "relevance_score": relevance_score,
                "user_feedback": user_feedback
            }
            
            self.access_history.append(access_record)
            
            # Atualiza métricas da fonte
            if source_id not in self.source_metrics:
                logger.warning(f"Fonte {source_id} não encontrada nas métricas")
                return
            
            metrics = self.source_metrics[source_id]
            metrics.usage_count += 1
            metrics.last_accessed = datetime.now().isoformat()
            
            # Atualiza score de relevância (média móvel)
            if metrics.relevance_score == 0:
                metrics.relevance_score = relevance_score
            else:
                metrics.relevance_score = (metrics.relevance_score * 0.8) + (relevance_score * 0.2)
            
            # Registra feedback se fornecido
            if user_feedback:
                metrics.user_feedback.append({
                    "timestamp": datetime.now().isoformat(),
                    "feedback": user_feedback
                })
                self.feedback_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "source_id": source_id,
                    "feedback": user_feedback
                })
            
            # Calcula frequência de acesso
            self._calculate_access_frequency(source_id)
            
            # Limita histórico
            cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
            self.access_history = [
                a for a in self.access_history 
                if datetime.fromisoformat(a["timestamp"]) > cutoff_date
            ]
            
            logger.debug(f"Acesso registrado para fonte: {source_id}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar acesso à fonte {source_id}: {e}")
    
    def analyze_source(self, source_id: str, content: str, metadata: Dict[str, Any]) -> SourceMetrics:
        """Analisa uma fonte específica"""
        try:
            # Cria ou atualiza métricas
            if source_id not in self.source_metrics:
                self.source_metrics[source_id] = SourceMetrics(
                    source_id=source_id,
                    url=metadata.get("url", ""),
                    title=metadata.get("title", ""),
                    category=metadata.get("category", "unknown"),
                    tags=metadata.get("tags", [])
                )
            
            metrics = self.source_metrics[source_id]
            
            # Analisa frescor do conteúdo
            metrics.freshness_score = self._analyze_content_freshness(content, metadata)
            
            # Analisa qualidade do conteúdo
            metrics.quality_score = self._analyze_content_quality(content, metadata)
            
            # Calcula idade do conteúdo
            metrics.content_age_days = self._calculate_content_age(metadata)
            
            # Identifica problemas
            metrics.issues = self._identify_content_issues(content, metadata)
            
            # Calcula score geral
            metrics.overall_score = self._calculate_overall_score(metrics)
            
            metrics.last_updated = datetime.now().isoformat()
            
            logger.debug(f"Fonte analisada: {source_id} (score: {metrics.overall_score:.2f})")
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao analisar fonte {source_id}: {e}")
            raise
    
    def identify_obsolete_sources(self) -> List[str]:
        """Identifica fontes obsoletas"""
        obsolete_sources = []
        
        try:
            current_time = datetime.now()
            
            for source_id, metrics in self.source_metrics.items():
                is_obsolete = False
                reasons = []
                
                # Verifica último acesso
                if metrics.last_accessed:
                    last_access = datetime.fromisoformat(metrics.last_accessed)
                    days_since_access = (current_time - last_access).days
                    
                    if days_since_access > self.obsolescence_threshold_days:
                        is_obsolete = True
                        reasons.append(f"Não acessada há {days_since_access} dias")
                
                # Verifica baixo uso
                if metrics.usage_count < self.low_usage_threshold:
                    is_obsolete = True
                    reasons.append(f"Baixo uso: {metrics.usage_count} acessos")
                
                # Verifica relevância baixa
                if metrics.relevance_score < self.min_relevance_score:
                    is_obsolete = True
                    reasons.append(f"Baixa relevância: {metrics.relevance_score:.2f}")
                
                # Verifica conteúdo muito antigo
                if metrics.content_age_days > 730:  # 2 anos
                    is_obsolete = True
                    reasons.append(f"Conteúdo antigo: {metrics.content_age_days} dias")
                
                # Verifica tecnologias obsoletas
                if "obsolete_tech" in metrics.issues:
                    is_obsolete = True
                    reasons.append("Contém tecnologias obsoletas")
                
                if is_obsolete:
                    obsolete_sources.append({
                        "source_id": source_id,
                        "reasons": reasons,
                        "last_accessed": metrics.last_accessed,
                        "usage_count": metrics.usage_count,
                        "relevance_score": metrics.relevance_score
                    })
            
            logger.info(f"Identificadas {len(obsolete_sources)} fontes obsoletas")
            return obsolete_sources
            
        except Exception as e:
            logger.error(f"Erro ao identificar fontes obsoletas: {e}")
            return []
    
    def identify_high_value_sources(self) -> List[str]:
        """Identifica fontes de alto valor"""
        try:
            # Ordena por score geral
            sorted_sources = sorted(
                self.source_metrics.items(),
                key=lambda x: x[1].overall_score,
                reverse=True
            )
            
            # Critérios para alto valor
            high_value = []
            for source_id, metrics in sorted_sources:
                if (
                    metrics.overall_score > 0.7 and
                    metrics.usage_count > 10 and
                    metrics.relevance_score > 0.6 and
                    metrics.access_frequency > 0.1  # pelo menos 1 acesso a cada 10 dias
                ):
                    high_value.append({
                        "source_id": source_id,
                        "overall_score": metrics.overall_score,
                        "usage_count": metrics.usage_count,
                        "relevance_score": metrics.relevance_score,
                        "access_frequency": metrics.access_frequency
                    })
            
            logger.info(f"Identificadas {len(high_value)} fontes de alto valor")
            return high_value
            
        except Exception as e:
            logger.error(f"Erro ao identificar fontes de alto valor: {e}")
            return []
    
    def generate_analysis_report(self) -> SourceAnalysisReport:
        """Gera relatório completo de análise de fontes"""
        try:
            total_sources = len(self.source_metrics)
            
            # Conta fontes ativas (acessadas nos últimos 30 dias)
            cutoff_date = datetime.now() - timedelta(days=30)
            active_sources = sum(
                1 for metrics in self.source_metrics.values()
                if metrics.last_accessed and 
                datetime.fromisoformat(metrics.last_accessed) > cutoff_date
            )
            
            # Identifica fontes obsoletas
            obsolete_candidates = self.identify_obsolete_sources()
            obsolete_sources = len(obsolete_candidates)
            
            # Identifica fontes de alto valor
            high_value_sources = len(self.identify_high_value_sources())
            
            # Identifica fontes de baixo valor
            low_value_sources = sum(
                1 for metrics in self.source_metrics.values()
                if metrics.overall_score < 0.3
            )
            
            # Gera recomendações
            recommendations = self._generate_source_recommendations()
            
            # Gera sugestões de melhoria
            improvement_suggestions = self._generate_improvement_suggestions()
            
            report = SourceAnalysisReport(
                generated_at=datetime.now().isoformat(),
                total_sources=total_sources,
                active_sources=active_sources,
                obsolete_sources=obsolete_sources,
                high_value_sources=high_value_sources,
                low_value_sources=low_value_sources,
                source_metrics=self.source_metrics.copy(),
                recommendations=recommendations,
                obsolete_candidates=[c["source_id"] for c in obsolete_candidates],
                improvement_suggestions=improvement_suggestions
            )
            
            # Salva relatório
            self._save_analysis_report(report)
            
            logger.info(f"Relatório de análise gerado: {total_sources} fontes analisadas")
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de análise: {e}")
            raise
    
    def _analyze_content_freshness(self, content: str, metadata: Dict[str, Any]) -> float:
        """Analisa o frescor do conteúdo"""
        score = 0.5  # Score base
        
        try:
            # Verifica data de publicação/atualização
            content_age = self._calculate_content_age(metadata)
            
            if content_age < 30:  # Menos de 1 mês
                score += 0.4
            elif content_age < 90:  # Menos de 3 meses
                score += 0.3
            elif content_age < 180:  # Menos de 6 meses
                score += 0.2
            elif content_age < 365:  # Menos de 1 ano
                score += 0.1
            elif content_age > 730:  # Mais de 2 anos
                score -= 0.3
            
            # Verifica menções a tecnologias modernas
            content_lower = content.lower()
            for tech, config in self.modern_patterns.items():
                for pattern in config["patterns"]:
                    if re.search(pattern, content_lower):
                        score += config["boost"]
                        break
            
            # Verifica menções a tecnologias obsoletas
            for tech, config in self.obsolete_patterns.items():
                for pattern in config["patterns"]:
                    if re.search(pattern, content_lower):
                        penalty = 0.1 if config["severity"] == "low" else \
                                 0.2 if config["severity"] == "medium" else 0.3
                        score -= penalty
                        break
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Erro ao analisar frescor do conteúdo: {e}")
            return 0.5
    
    def _analyze_content_quality(self, content: str, metadata: Dict[str, Any]) -> float:
        """Analisa a qualidade do conteúdo"""
        score = 0.5  # Score base
        
        try:
            # Verifica tamanho do conteúdo
            content_length = len(content)
            if content_length > 5000:  # Conteúdo substancial
                score += 0.2
            elif content_length > 2000:
                score += 0.1
            elif content_length < 500:  # Muito curto
                score -= 0.2
            
            # Verifica estrutura (headers, listas, etc.)
            if re.search(r'#{1,6}\s', content):  # Headers markdown
                score += 0.1
            if re.search(r'^\s*[-*+]\s', content, re.MULTILINE):  # Listas
                score += 0.05
            if re.search(r'```', content):  # Blocos de código
                score += 0.1
            
            # Verifica links e referências
            if re.search(r'https?://', content):
                score += 0.05
            
            # Verifica metadados de qualidade
            if metadata.get("author"):
                score += 0.05
            if metadata.get("tags"):
                score += 0.05
            if metadata.get("description"):
                score += 0.05
            
            # Penaliza conteúdo com muitos erros
            error_patterns = [r'404', r'not found', r'error', r'broken']
            for pattern in error_patterns:
                if re.search(pattern, content.lower()):
                    score -= 0.1
                    break
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Erro ao analisar qualidade do conteúdo: {e}")
            return 0.5
    
    def _calculate_content_age(self, metadata: Dict[str, Any]) -> int:
        """Calcula idade do conteúdo em dias"""
        try:
            # Tenta diferentes campos de data
            date_fields = ['published_date', 'updated_date', 'created_date', 'date']
            
            for field in date_fields:
                if field in metadata and metadata[field]:
                    try:
                        content_date = datetime.fromisoformat(metadata[field].replace('Z', '+00:00'))
                        age_days = (datetime.now() - content_date.replace(tzinfo=None)).days
                        return max(0, age_days)
                    except:
                        continue
            
            # Se não encontrar data, assume idade média
            return 180  # 6 meses
            
        except Exception as e:
            logger.error(f"Erro ao calcular idade do conteúdo: {e}")
            return 180
    
    def _identify_content_issues(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """Identifica problemas no conteúdo"""
        issues = []
        
        try:
            content_lower = content.lower()
            
            # Verifica tecnologias obsoletas
            for tech, config in self.obsolete_patterns.items():
                for pattern in config["patterns"]:
                    if re.search(pattern, content_lower):
                        issues.append("obsolete_tech")
                        break
            
            # Verifica links quebrados (padrões comuns)
            if re.search(r'404|not found|page not found', content_lower):
                issues.append("broken_links")
            
            # Verifica conteúdo muito curto
            if len(content) < 500:
                issues.append("too_short")
            
            # Verifica falta de estrutura
            if not re.search(r'#{1,6}\s', content) and len(content) > 1000:
                issues.append("poor_structure")
            
            # Verifica falta de exemplos de código
            if 'tutorial' in metadata.get('category', '').lower() and not re.search(r'```', content):
                issues.append("no_code_examples")
            
            # Verifica idade excessiva
            age_days = self._calculate_content_age(metadata)
            if age_days > 730:  # 2 anos
                issues.append("very_old")
            
            return list(set(issues))  # Remove duplicatas
            
        except Exception as e:
            logger.error(f"Erro ao identificar problemas do conteúdo: {e}")
            return []
    
    def _calculate_overall_score(self, metrics: SourceMetrics) -> float:
        """Calcula score geral da fonte"""
        try:
            # Pesos para diferentes métricas
            weights = {
                "relevance": 0.3,
                "freshness": 0.25,
                "quality": 0.2,
                "usage": 0.15,
                "frequency": 0.1
            }
            
            # Normaliza usage_count (0-1)
            usage_score = min(metrics.usage_count / 50.0, 1.0)
            
            # Normaliza access_frequency (0-1)
            frequency_score = min(metrics.access_frequency, 1.0)
            
            # Calcula score ponderado
            overall_score = (
                metrics.relevance_score * weights["relevance"] +
                metrics.freshness_score * weights["freshness"] +
                metrics.quality_score * weights["quality"] +
                usage_score * weights["usage"] +
                frequency_score * weights["frequency"]
            )
            
            # Aplica penalidades por problemas
            penalty = len(metrics.issues) * 0.05
            overall_score = max(0.0, overall_score - penalty)
            
            return min(1.0, overall_score)
            
        except Exception as e:
            logger.error(f"Erro ao calcular score geral: {e}")
            return 0.0
    
    def _calculate_access_frequency(self, source_id: str) -> None:
        """Calcula frequência de acesso de uma fonte"""
        try:
            # Conta acessos nos últimos 30 dias
            cutoff_date = datetime.now() - timedelta(days=30)
            recent_accesses = [
                a for a in self.access_history
                if a["source_id"] == source_id and 
                datetime.fromisoformat(a["timestamp"]) > cutoff_date
            ]
            
            # Calcula frequência (acessos por dia)
            frequency = len(recent_accesses) / 30.0
            self.source_metrics[source_id].access_frequency = frequency
            
        except Exception as e:
            logger.error(f"Erro ao calcular frequência de acesso: {e}")
    
    def _generate_source_recommendations(self) -> List[str]:
        """Gera recomendações para gestão de fontes"""
        recommendations = []
        
        try:
            # Analisa fontes obsoletas
            obsolete_sources = self.identify_obsolete_sources()
            if len(obsolete_sources) > 10:
                recommendations.append(
                    f"Remover {len(obsolete_sources)} fontes obsoletas para otimizar performance"
                )
            
            # Analisa fontes de baixo valor
            low_value_count = sum(
                1 for metrics in self.source_metrics.values()
                if metrics.overall_score < 0.3
            )
            if low_value_count > 5:
                recommendations.append(
                    f"Revisar {low_value_count} fontes de baixo valor"
                )
            
            # Analisa cobertura por categoria
            category_counts = Counter(
                metrics.category for metrics in self.source_metrics.values()
            )
            
            for category, count in category_counts.items():
                if count < 3:
                    recommendations.append(
                        f"Adicionar mais fontes na categoria '{category}' (apenas {count} disponíveis)"
                    )
            
            # Analisa fontes com problemas
            sources_with_issues = [
                metrics for metrics in self.source_metrics.values()
                if len(metrics.issues) > 0
            ]
            
            if len(sources_with_issues) > 0:
                recommendations.append(
                    f"Corrigir problemas em {len(sources_with_issues)} fontes"
                )
            
            return recommendations[:10]  # Limita a 10 recomendações
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            return []
    
    def _generate_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Gera sugestões específicas de melhoria"""
        suggestions = []
        
        try:
            for source_id, metrics in self.source_metrics.items():
                source_suggestions = []
                
                # Sugestões baseadas em problemas
                if "obsolete_tech" in metrics.issues:
                    source_suggestions.append("Atualizar para tecnologias modernas")
                
                if "broken_links" in metrics.issues:
                    source_suggestions.append("Corrigir links quebrados")
                
                if "too_short" in metrics.issues:
                    source_suggestions.append("Expandir conteúdo com mais detalhes")
                
                if "poor_structure" in metrics.issues:
                    source_suggestions.append("Melhorar estrutura com headers e seções")
                
                if "no_code_examples" in metrics.issues:
                    source_suggestions.append("Adicionar exemplos de código")
                
                # Sugestões baseadas em scores baixos
                if metrics.relevance_score < 0.4:
                    source_suggestions.append("Melhorar relevância do conteúdo")
                
                if metrics.quality_score < 0.4:
                    source_suggestions.append("Melhorar qualidade do conteúdo")
                
                if metrics.freshness_score < 0.3:
                    source_suggestions.append("Atualizar conteúdo desatualizado")
                
                if source_suggestions:
                    suggestions.append({
                        "source_id": source_id,
                        "title": metrics.title,
                        "current_score": metrics.overall_score,
                        "suggestions": source_suggestions,
                        "priority": "high" if metrics.overall_score < 0.3 else 
                                   "medium" if metrics.overall_score < 0.6 else "low"
                    })
            
            # Ordena por prioridade e score
            suggestions.sort(key=lambda x: (x["priority"] == "high", -x["current_score"]), reverse=True)
            
            return suggestions[:20]  # Limita a 20 sugestões
            
        except Exception as e:
            logger.error(f"Erro ao gerar sugestões de melhoria: {e}")
            return []
    
    def _save_analysis_report(self, report: SourceAnalysisReport) -> None:
        """Salva relatório de análise"""
        try:
            report_file = self.data_dir / f"source_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Converte para dict serializável
            report_dict = {
                "generated_at": report.generated_at,
                "total_sources": report.total_sources,
                "active_sources": report.active_sources,
                "obsolete_sources": report.obsolete_sources,
                "high_value_sources": report.high_value_sources,
                "low_value_sources": report.low_value_sources,
                "recommendations": report.recommendations,
                "obsolete_candidates": report.obsolete_candidates,
                "improvement_suggestions": report.improvement_suggestions,
                "source_metrics": {
                    source_id: {
                        "source_id": sm.source_id,
                        "url": sm.url,
                        "title": sm.title,
                        "category": sm.category,
                        "usage_count": sm.usage_count,
                        "last_accessed": sm.last_accessed,
                        "relevance_score": sm.relevance_score,
                        "freshness_score": sm.freshness_score,
                        "quality_score": sm.quality_score,
                        "overall_score": sm.overall_score,
                        "access_frequency": sm.access_frequency,
                        "content_age_days": sm.content_age_days,
                        "last_updated": sm.last_updated,
                        "tags": sm.tags,
                        "issues": sm.issues
                    }
                    for source_id, sm in report.source_metrics.items()
                }
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Relatório de análise salvo: {report_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório de análise: {e}")
    
    def _load_analysis_data(self) -> None:
        """Carrega dados de análise salvos"""
        try:
            analysis_file = self.data_dir / "source_analysis_data.json"
            
            if analysis_file.exists():
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Carrega métricas de fontes
                for source_data in data.get("source_metrics", []):
                    metrics = SourceMetrics(**source_data)
                    self.source_metrics[metrics.source_id] = metrics
                
                # Carrega histórico de acessos
                self.access_history = data.get("access_history", [])
                
                # Carrega histórico de feedback
                self.feedback_history = data.get("feedback_history", [])
                
                logger.info(f"Dados de análise carregados: {len(self.source_metrics)} fontes")
                
        except Exception as e:
            logger.warning(f"Erro ao carregar dados de análise: {e}")
    
    def save_analysis_data(self) -> None:
        """Salva dados de análise"""
        try:
            analysis_file = self.data_dir / "source_analysis_data.json"
            
            data = {
                "saved_at": datetime.now().isoformat(),
                "source_metrics": [
                    {
                        "source_id": sm.source_id,
                        "url": sm.url,
                        "title": sm.title,
                        "category": sm.category,
                        "usage_count": sm.usage_count,
                        "last_accessed": sm.last_accessed,
                        "relevance_score": sm.relevance_score,
                        "freshness_score": sm.freshness_score,
                        "quality_score": sm.quality_score,
                        "overall_score": sm.overall_score,
                        "access_frequency": sm.access_frequency,
                        "user_feedback": sm.user_feedback,
                        "content_age_days": sm.content_age_days,
                        "last_updated": sm.last_updated,
                        "tags": sm.tags,
                        "issues": sm.issues
                    }
                    for sm in self.source_metrics.values()
                ],
                "access_history": self.access_history,
                "feedback_history": self.feedback_history
            }
            
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Dados de análise salvos: {analysis_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados de análise: {e}")