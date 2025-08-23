#!/usr/bin/env python3
"""
Coverage Monitor - Monitor de Cobertura

Este módulo monitora a cobertura de tópicos e identifica lacunas de conhecimento
no sistema RAG, ajudando a identificar áreas que precisam de mais fontes.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)

@dataclass
class TopicCoverage:
    """Representa a cobertura de um tópico específico"""
    topic: str
    coverage_score: float  # 0.0 a 1.0
    source_count: int
    query_frequency: int
    last_updated: str
    gaps: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
@dataclass
class CoverageReport:
    """Relatório completo de cobertura"""
    generated_at: str
    overall_coverage: float
    total_topics: int
    well_covered_topics: int
    poorly_covered_topics: int
    coverage_gaps: List[str]
    topic_coverage: Dict[str, TopicCoverage]
    recommendations: List[str] = field(default_factory=list)
    trending_topics: List[str] = field(default_factory=list)
    
class CoverageMonitor:
    """Monitor de cobertura de tópicos e lacunas de conhecimento"""
    
    def __init__(self, data_dir: str = "data/governance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações
        self.min_coverage_threshold = 0.6
        self.min_sources_per_topic = 3
        self.analysis_window_days = 30
        
        # Dados de cobertura
        self.topic_coverage: Dict[str, TopicCoverage] = {}
        self.query_history: List[Dict[str, Any]] = []
        self.source_topics: Dict[str, Set[str]] = defaultdict(set)
        
        # Tópicos conhecidos (expandir conforme necessário)
        self.known_topics = {
            "react", "nextjs", "typescript", "javascript", "tailwind", "css",
            "nodejs", "express", "fastapi", "python", "authentication", "database",
            "prisma", "mongodb", "postgresql", "redis", "docker", "kubernetes",
            "aws", "vercel", "deployment", "testing", "jest", "playwright",
            "security", "performance", "optimization", "seo", "accessibility",
            "ui", "ux", "design", "components", "hooks", "state-management",
            "api", "rest", "graphql", "websockets", "real-time", "caching",
            "monitoring", "logging", "analytics", "error-handling", "debugging"
        }
        
        self._load_coverage_data()
    
    def analyze_query_coverage(self, query: str, results: List[Dict[str, Any]]) -> None:
        """Analisa a cobertura de uma query específica"""
        try:
            # Extrai tópicos da query
            topics = self._extract_topics_from_query(query)
            
            # Registra a query
            query_record = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "topics": topics,
                "result_count": len(results),
                "has_results": len(results) > 0
            }
            self.query_history.append(query_record)
            
            # Atualiza cobertura dos tópicos
            for topic in topics:
                self._update_topic_coverage(topic, results)
            
            # Limita histórico
            cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
            self.query_history = [
                q for q in self.query_history 
                if datetime.fromisoformat(q["timestamp"]) > cutoff_date
            ]
            
            logger.info(f"Analisada cobertura para query: {query[:50]}...")
            
        except Exception as e:
            logger.error(f"Erro ao analisar cobertura da query: {e}")
    
    def analyze_source_coverage(self, source_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """Analisa a cobertura de uma fonte específica"""
        try:
            # Extrai tópicos do conteúdo
            topics = self._extract_topics_from_content(content, metadata)
            
            # Registra tópicos da fonte
            self.source_topics[source_id] = set(topics)
            
            # Atualiza cobertura
            for topic in topics:
                if topic not in self.topic_coverage:
                    self.topic_coverage[topic] = TopicCoverage(
                        topic=topic,
                        coverage_score=0.0,
                        source_count=0,
                        query_frequency=0,
                        last_updated=datetime.now().isoformat()
                    )
                
                self.topic_coverage[topic].source_count += 1
                self.topic_coverage[topic].last_updated = datetime.now().isoformat()
            
            logger.info(f"Analisada cobertura da fonte: {source_id}")
            
        except Exception as e:
            logger.error(f"Erro ao analisar cobertura da fonte {source_id}: {e}")
    
    def generate_coverage_report(self) -> CoverageReport:
        """Gera relatório completo de cobertura"""
        try:
            # Calcula estatísticas gerais
            total_topics = len(self.topic_coverage)
            well_covered = sum(1 for tc in self.topic_coverage.values() 
                             if tc.coverage_score >= self.min_coverage_threshold)
            poorly_covered = total_topics - well_covered
            
            # Calcula cobertura geral
            if total_topics > 0:
                overall_coverage = sum(tc.coverage_score for tc in self.topic_coverage.values()) / total_topics
            else:
                overall_coverage = 0.0
            
            # Identifica lacunas
            coverage_gaps = [
                tc.topic for tc in self.topic_coverage.values()
                if tc.coverage_score < self.min_coverage_threshold
            ]
            
            # Gera recomendações
            recommendations = self._generate_recommendations()
            
            # Identifica tópicos em alta
            trending_topics = self._identify_trending_topics()
            
            report = CoverageReport(
                generated_at=datetime.now().isoformat(),
                overall_coverage=overall_coverage,
                total_topics=total_topics,
                well_covered_topics=well_covered,
                poorly_covered_topics=poorly_covered,
                coverage_gaps=coverage_gaps,
                topic_coverage=self.topic_coverage.copy(),
                recommendations=recommendations,
                trending_topics=trending_topics
            )
            
            # Salva relatório
            self._save_coverage_report(report)
            
            logger.info(f"Relatório de cobertura gerado: {total_topics} tópicos analisados")
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de cobertura: {e}")
            raise
    
    def identify_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """Identifica lacunas específicas de conhecimento"""
        gaps = []
        
        try:
            # Analisa queries sem resultados
            failed_queries = [q for q in self.query_history if not q["has_results"]]
            
            for query in failed_queries:
                gap = {
                    "type": "no_results",
                    "query": query["query"],
                    "topics": query["topics"],
                    "timestamp": query["timestamp"],
                    "severity": "high" if len(query["topics"]) > 0 else "medium"
                }
                gaps.append(gap)
            
            # Analisa tópicos com baixa cobertura
            for topic, coverage in self.topic_coverage.items():
                if coverage.coverage_score < self.min_coverage_threshold:
                    gap = {
                        "type": "low_coverage",
                        "topic": topic,
                        "coverage_score": coverage.coverage_score,
                        "source_count": coverage.source_count,
                        "query_frequency": coverage.query_frequency,
                        "severity": "high" if coverage.query_frequency > 5 else "medium"
                    }
                    gaps.append(gap)
            
            # Analisa tópicos populares sem fontes suficientes
            topic_queries = Counter()
            for query in self.query_history:
                for topic in query["topics"]:
                    topic_queries[topic] += 1
            
            for topic, frequency in topic_queries.most_common(20):
                if topic in self.topic_coverage:
                    coverage = self.topic_coverage[topic]
                    if coverage.source_count < self.min_sources_per_topic:
                        gap = {
                            "type": "insufficient_sources",
                            "topic": topic,
                            "query_frequency": frequency,
                            "source_count": coverage.source_count,
                            "needed_sources": self.min_sources_per_topic - coverage.source_count,
                            "severity": "high"
                        }
                        gaps.append(gap)
            
            # Ordena por severidade
            gaps.sort(key=lambda x: (x["severity"] == "high", x.get("query_frequency", 0)), reverse=True)
            
            logger.info(f"Identificadas {len(gaps)} lacunas de conhecimento")
            return gaps
            
        except Exception as e:
            logger.error(f"Erro ao identificar lacunas: {e}")
            return []
    
    def _extract_topics_from_query(self, query: str) -> List[str]:
        """Extrai tópicos de uma query"""
        query_lower = query.lower()
        topics = []
        
        # Busca tópicos conhecidos
        for topic in self.known_topics:
            if topic in query_lower:
                topics.append(topic)
        
        # Extrai tecnologias mencionadas
        tech_patterns = [
            r'\b(react|vue|angular|svelte)\b',
            r'\b(next\.?js|nuxt|gatsby)\b',
            r'\b(typescript|javascript|python|java|go|rust)\b',
            r'\b(node\.?js|express|fastapi|django|flask)\b',
            r'\b(mongodb|postgresql|mysql|redis|sqlite)\b',
            r'\b(docker|kubernetes|aws|gcp|azure)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, query_lower)
            topics.extend(matches)
        
        return list(set(topics))  # Remove duplicatas
    
    def _extract_topics_from_content(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """Extrai tópicos do conteúdo de uma fonte"""
        topics = []
        content_lower = content.lower()
        
        # Usa metadados se disponíveis
        if "tags" in metadata:
            topics.extend(metadata["tags"])
        
        if "category" in metadata:
            topics.append(metadata["category"])
        
        # Busca tópicos no conteúdo
        for topic in self.known_topics:
            if topic in content_lower:
                topics.append(topic)
        
        return list(set(topics))
    
    def _update_topic_coverage(self, topic: str, results: List[Dict[str, Any]]) -> None:
        """Atualiza a cobertura de um tópico"""
        if topic not in self.topic_coverage:
            self.topic_coverage[topic] = TopicCoverage(
                topic=topic,
                coverage_score=0.0,
                source_count=0,
                query_frequency=0,
                last_updated=datetime.now().isoformat()
            )
        
        coverage = self.topic_coverage[topic]
        coverage.query_frequency += 1
        
        # Calcula score baseado em resultados
        if len(results) > 0:
            # Score baseado na quantidade e qualidade dos resultados
            result_score = min(len(results) / 10.0, 1.0)  # Normaliza para 0-1
            
            # Considera relevância dos resultados
            relevance_scores = [r.get("score", 0.5) for r in results]
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.5
            
            # Combina scores
            new_score = (result_score * 0.6) + (avg_relevance * 0.4)
            
            # Atualiza com média ponderada
            coverage.coverage_score = (coverage.coverage_score * 0.8) + (new_score * 0.2)
        else:
            # Penaliza falta de resultados
            coverage.coverage_score *= 0.9
        
        coverage.last_updated = datetime.now().isoformat()
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações para melhorar cobertura"""
        recommendations = []
        
        # Analisa lacunas críticas
        critical_gaps = [
            tc for tc in self.topic_coverage.values()
            if tc.coverage_score < 0.3 and tc.query_frequency > 3
        ]
        
        for gap in critical_gaps:
            recommendations.append(
                f"Adicionar mais fontes sobre '{gap.topic}' - apenas {gap.source_count} fontes disponíveis"
            )
        
        # Analisa tópicos populares
        popular_topics = sorted(
            self.topic_coverage.values(),
            key=lambda x: x.query_frequency,
            reverse=True
        )[:5]
        
        for topic in popular_topics:
            if topic.source_count < self.min_sources_per_topic:
                recommendations.append(
                    f"Expandir cobertura de '{topic.topic}' - tópico popular com poucas fontes"
                )
        
        return recommendations[:10]  # Limita a 10 recomendações
    
    def _identify_trending_topics(self) -> List[str]:
        """Identifica tópicos em alta baseado em queries recentes"""
        recent_queries = [
            q for q in self.query_history
            if datetime.fromisoformat(q["timestamp"]) > datetime.now() - timedelta(days=7)
        ]
        
        topic_counts = Counter()
        for query in recent_queries:
            for topic in query["topics"]:
                topic_counts[topic] += 1
        
        return [topic for topic, _ in topic_counts.most_common(10)]
    
    def _save_coverage_report(self, report: CoverageReport) -> None:
        """Salva relatório de cobertura"""
        try:
            report_file = self.data_dir / f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Converte para dict serializável
            report_dict = {
                "generated_at": report.generated_at,
                "overall_coverage": report.overall_coverage,
                "total_topics": report.total_topics,
                "well_covered_topics": report.well_covered_topics,
                "poorly_covered_topics": report.poorly_covered_topics,
                "coverage_gaps": report.coverage_gaps,
                "recommendations": report.recommendations,
                "trending_topics": report.trending_topics,
                "topic_coverage": {
                    topic: {
                        "topic": tc.topic,
                        "coverage_score": tc.coverage_score,
                        "source_count": tc.source_count,
                        "query_frequency": tc.query_frequency,
                        "last_updated": tc.last_updated,
                        "gaps": tc.gaps,
                        "related_topics": tc.related_topics,
                        "confidence": tc.confidence
                    }
                    for topic, tc in report.topic_coverage.items()
                }
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Relatório salvo: {report_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")
    
    def _load_coverage_data(self) -> None:
        """Carrega dados de cobertura salvos"""
        try:
            coverage_file = self.data_dir / "coverage_data.json"
            
            if coverage_file.exists():
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Carrega cobertura de tópicos
                for topic_data in data.get("topic_coverage", []):
                    topic = TopicCoverage(**topic_data)
                    self.topic_coverage[topic.topic] = topic
                
                # Carrega histórico de queries (últimos 30 dias)
                self.query_history = data.get("query_history", [])
                
                logger.info(f"Dados de cobertura carregados: {len(self.topic_coverage)} tópicos")
                
        except Exception as e:
            logger.warning(f"Erro ao carregar dados de cobertura: {e}")
    
    def save_coverage_data(self) -> None:
        """Salva dados de cobertura"""
        try:
            coverage_file = self.data_dir / "coverage_data.json"
            
            data = {
                "saved_at": datetime.now().isoformat(),
                "topic_coverage": [
                    {
                        "topic": tc.topic,
                        "coverage_score": tc.coverage_score,
                        "source_count": tc.source_count,
                        "query_frequency": tc.query_frequency,
                        "last_updated": tc.last_updated,
                        "gaps": tc.gaps,
                        "related_topics": tc.related_topics,
                        "confidence": tc.confidence
                    }
                    for tc in self.topic_coverage.values()
                ],
                "query_history": self.query_history
            }
            
            with open(coverage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Dados de cobertura salvos: {coverage_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados de cobertura: {e}")