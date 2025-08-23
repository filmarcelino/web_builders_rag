#!/usr/bin/env python3
"""
Governance Dashboard - Dashboard de Governança

Este módulo fornece um dashboard unificado para monitorar a governança
do sistema RAG, incluindo cobertura, análise de fontes e obsolescência.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from .coverage_monitor import CoverageMonitor, CoverageReport
from .source_analyzer import SourceAnalyzer, SourceAnalysisReport
from .obsolescence_detector import ObsolescenceDetector, ObsolescenceReport

logger = logging.getLogger(__name__)

@dataclass
class GovernanceMetrics:
    """Métricas consolidadas de governança"""
    timestamp: str
    
    # Métricas de cobertura
    overall_coverage: float
    total_topics: int
    coverage_gaps: int
    trending_topics: List[str]
    
    # Métricas de fontes
    total_sources: int
    active_sources: int
    obsolete_sources: int
    high_value_sources: int
    
    # Métricas de obsolescência
    total_detections: int
    critical_issues: int
    high_issues: int
    sources_with_issues: int
    
    # Scores gerais
    governance_score: float
    health_score: float
    quality_score: float
    
@dataclass
class GovernanceDashboard:
    """Dashboard principal de governança"""
    generated_at: str
    metrics: GovernanceMetrics
    coverage_summary: Dict[str, Any]
    source_summary: Dict[str, Any]
    obsolescence_summary: Dict[str, Any]
    recommendations: List[str]
    alerts: List[Dict[str, Any]]
    trends: Dict[str, List[float]]
    
class GovernanceDashboardGenerator:
    """Gerador do dashboard de governança"""
    
    def __init__(self, data_dir: str = "data/governance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Componentes de governança
        self.coverage_monitor = CoverageMonitor(data_dir)
        self.source_analyzer = SourceAnalyzer(data_dir)
        self.obsolescence_detector = ObsolescenceDetector(data_dir)
        
        # Histórico de métricas
        self.metrics_history: List[GovernanceMetrics] = []
        self.max_history_days = 30
        
        # Thresholds para alertas
        self.alert_thresholds = {
            "coverage_min": 0.7,
            "obsolete_sources_max": 10,
            "critical_issues_max": 5,
            "inactive_sources_max": 0.3,  # 30% de fontes inativas
            "governance_score_min": 0.6
        }
        
        self._load_metrics_history()
    
    def generate_dashboard(self) -> GovernanceDashboard:
        """Gera dashboard completo de governança"""
        try:
            logger.info("Gerando dashboard de governança...")
            
            # Gera relatórios individuais
            coverage_report = self.coverage_monitor.generate_coverage_report()
            source_report = self.source_analyzer.generate_analysis_report()
            obsolescence_report = self.obsolescence_detector.generate_obsolescence_report()
            
            # Calcula métricas consolidadas
            metrics = self._calculate_consolidated_metrics(
                coverage_report, source_report, obsolescence_report
            )
            
            # Adiciona ao histórico
            self.metrics_history.append(metrics)
            self._trim_metrics_history()
            
            # Gera resumos
            coverage_summary = self._generate_coverage_summary(coverage_report)
            source_summary = self._generate_source_summary(source_report)
            obsolescence_summary = self._generate_obsolescence_summary(obsolescence_report)
            
            # Gera recomendações consolidadas
            recommendations = self._generate_consolidated_recommendations(
                coverage_report, source_report, obsolescence_report
            )
            
            # Gera alertas
            alerts = self._generate_alerts(metrics)
            
            # Calcula tendências
            trends = self._calculate_trends()
            
            dashboard = GovernanceDashboard(
                generated_at=datetime.now().isoformat(),
                metrics=metrics,
                coverage_summary=coverage_summary,
                source_summary=source_summary,
                obsolescence_summary=obsolescence_summary,
                recommendations=recommendations,
                alerts=alerts,
                trends=trends
            )
            
            # Salva dashboard
            self._save_dashboard(dashboard)
            
            logger.info("Dashboard de governança gerado com sucesso")
            return dashboard
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard de governança: {e}")
            raise
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde do sistema"""
        try:
            if not self.metrics_history:
                return {"status": "unknown", "message": "Dados insuficientes"}
            
            latest_metrics = self.metrics_history[-1]
            
            # Calcula status baseado em múltiplos fatores
            health_factors = {
                "coverage": latest_metrics.overall_coverage,
                "governance_score": latest_metrics.governance_score,
                "quality_score": latest_metrics.quality_score,
                "critical_issues": 1.0 - min(latest_metrics.critical_issues / 10.0, 1.0)
            }
            
            overall_health = sum(health_factors.values()) / len(health_factors)
            
            if overall_health >= 0.8:
                status = "excellent"
                message = "Sistema em excelente estado"
            elif overall_health >= 0.6:
                status = "good"
                message = "Sistema em bom estado"
            elif overall_health >= 0.4:
                status = "warning"
                message = "Sistema precisa de atenção"
            else:
                status = "critical"
                message = "Sistema em estado crítico"
            
            return {
                "status": status,
                "message": message,
                "overall_health": overall_health,
                "factors": health_factors,
                "timestamp": latest_metrics.timestamp
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular status de saúde: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_priority_actions(self) -> List[Dict[str, Any]]:
        """Retorna ações prioritárias baseadas no estado atual"""
        actions = []
        
        try:
            if not self.metrics_history:
                return actions
            
            latest_metrics = self.metrics_history[-1]
            
            # Ações baseadas em problemas críticos
            if latest_metrics.critical_issues > 0:
                actions.append({
                    "priority": "critical",
                    "action": "Corrigir problemas críticos de segurança",
                    "description": f"{latest_metrics.critical_issues} problemas críticos detectados",
                    "estimated_effort": "high",
                    "impact": "security"
                })
            
            # Ações baseadas em cobertura baixa
            if latest_metrics.overall_coverage < 0.6:
                actions.append({
                    "priority": "high",
                    "action": "Melhorar cobertura de tópicos",
                    "description": f"Cobertura atual: {latest_metrics.overall_coverage:.1%}",
                    "estimated_effort": "medium",
                    "impact": "coverage"
                })
            
            # Ações baseadas em fontes obsoletas
            if latest_metrics.obsolete_sources > 10:
                actions.append({
                    "priority": "medium",
                    "action": "Remover fontes obsoletas",
                    "description": f"{latest_metrics.obsolete_sources} fontes obsoletas",
                    "estimated_effort": "low",
                    "impact": "performance"
                })
            
            # Ações baseadas em fontes inativas
            inactive_ratio = 1 - (latest_metrics.active_sources / max(latest_metrics.total_sources, 1))
            if inactive_ratio > 0.3:
                actions.append({
                    "priority": "medium",
                    "action": "Revisar fontes inativas",
                    "description": f"{inactive_ratio:.1%} das fontes estão inativas",
                    "estimated_effort": "medium",
                    "impact": "efficiency"
                })
            
            # Ações baseadas em lacunas de cobertura
            if latest_metrics.coverage_gaps > 5:
                actions.append({
                    "priority": "medium",
                    "action": "Adicionar fontes para tópicos descobertos",
                    "description": f"{latest_metrics.coverage_gaps} lacunas de cobertura",
                    "estimated_effort": "high",
                    "impact": "coverage"
                })
            
            # Ordena por prioridade
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            actions.sort(key=lambda x: priority_order.get(x["priority"], 4))
            
            return actions[:10]  # Limita a 10 ações
            
        except Exception as e:
            logger.error(f"Erro ao gerar ações prioritárias: {e}")
            return []
    
    def export_governance_report(self, format: str = "json") -> str:
        """Exporta relatório de governança em diferentes formatos"""
        try:
            dashboard = self.generate_dashboard()
            
            if format.lower() == "json":
                return self._export_json_report(dashboard)
            elif format.lower() == "html":
                return self._export_html_report(dashboard)
            elif format.lower() == "markdown":
                return self._export_markdown_report(dashboard)
            else:
                raise ValueError(f"Formato não suportado: {format}")
                
        except Exception as e:
            logger.error(f"Erro ao exportar relatório: {e}")
            raise
    
    def _calculate_consolidated_metrics(self, coverage_report: CoverageReport, 
                                      source_report: SourceAnalysisReport,
                                      obsolescence_report: ObsolescenceReport) -> GovernanceMetrics:
        """Calcula métricas consolidadas"""
        try:
            # Calcula scores
            governance_score = self._calculate_governance_score(
                coverage_report, source_report, obsolescence_report
            )
            
            health_score = self._calculate_health_score(
                coverage_report, source_report, obsolescence_report
            )
            
            quality_score = self._calculate_quality_score(
                coverage_report, source_report, obsolescence_report
            )
            
            return GovernanceMetrics(
                timestamp=datetime.now().isoformat(),
                
                # Cobertura
                overall_coverage=coverage_report.overall_coverage,
                total_topics=coverage_report.total_topics,
                coverage_gaps=len(coverage_report.coverage_gaps),
                trending_topics=coverage_report.trending_topics,
                
                # Fontes
                total_sources=source_report.total_sources,
                active_sources=source_report.active_sources,
                obsolete_sources=source_report.obsolete_sources,
                high_value_sources=source_report.high_value_sources,
                
                # Obsolescência
                total_detections=obsolescence_report.total_detections,
                critical_issues=obsolescence_report.critical_issues,
                high_issues=obsolescence_report.high_issues,
                sources_with_issues=obsolescence_report.sources_with_issues,
                
                # Scores
                governance_score=governance_score,
                health_score=health_score,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas consolidadas: {e}")
            raise
    
    def _calculate_governance_score(self, coverage_report: CoverageReport,
                                  source_report: SourceAnalysisReport,
                                  obsolescence_report: ObsolescenceReport) -> float:
        """Calcula score de governança"""
        try:
            # Componentes do score (pesos)
            weights = {
                "coverage": 0.3,
                "source_quality": 0.25,
                "obsolescence": 0.25,
                "activity": 0.2
            }
            
            # Score de cobertura
            coverage_score = coverage_report.overall_coverage
            
            # Score de qualidade das fontes
            if source_report.total_sources > 0:
                source_quality_score = source_report.high_value_sources / source_report.total_sources
            else:
                source_quality_score = 0.0
            
            # Score de obsolescência (inverso)
            if obsolescence_report.total_detections > 0:
                obsolescence_score = max(0, 1 - (obsolescence_report.critical_issues / 10.0))
            else:
                obsolescence_score = 1.0
            
            # Score de atividade
            if source_report.total_sources > 0:
                activity_score = source_report.active_sources / source_report.total_sources
            else:
                activity_score = 0.0
            
            # Calcula score ponderado
            governance_score = (
                coverage_score * weights["coverage"] +
                source_quality_score * weights["source_quality"] +
                obsolescence_score * weights["obsolescence"] +
                activity_score * weights["activity"]
            )
            
            return min(1.0, max(0.0, governance_score))
            
        except Exception as e:
            logger.error(f"Erro ao calcular score de governança: {e}")
            return 0.0
    
    def _calculate_health_score(self, coverage_report: CoverageReport,
                              source_report: SourceAnalysisReport,
                              obsolescence_report: ObsolescenceReport) -> float:
        """Calcula score de saúde do sistema"""
        try:
            health_factors = []
            
            # Fator de cobertura
            health_factors.append(coverage_report.overall_coverage)
            
            # Fator de problemas críticos
            critical_penalty = min(obsolescence_report.critical_issues / 5.0, 1.0)
            health_factors.append(1.0 - critical_penalty)
            
            # Fator de fontes ativas
            if source_report.total_sources > 0:
                activity_factor = source_report.active_sources / source_report.total_sources
                health_factors.append(activity_factor)
            
            # Fator de lacunas
            if coverage_report.total_topics > 0:
                gap_factor = 1.0 - (len(coverage_report.coverage_gaps) / coverage_report.total_topics)
                health_factors.append(max(0.0, gap_factor))
            
            return sum(health_factors) / len(health_factors) if health_factors else 0.0
            
        except Exception as e:
            logger.error(f"Erro ao calcular score de saúde: {e}")
            return 0.0
    
    def _calculate_quality_score(self, coverage_report: CoverageReport,
                               source_report: SourceAnalysisReport,
                               obsolescence_report: ObsolescenceReport) -> float:
        """Calcula score de qualidade"""
        try:
            quality_factors = []
            
            # Qualidade das fontes
            if source_report.total_sources > 0:
                high_value_ratio = source_report.high_value_sources / source_report.total_sources
                low_value_ratio = source_report.low_value_sources / source_report.total_sources
                source_quality = high_value_ratio - (low_value_ratio * 0.5)
                quality_factors.append(max(0.0, source_quality))
            
            # Ausência de problemas
            if obsolescence_report.total_detections == 0:
                quality_factors.append(1.0)
            else:
                problem_penalty = min(obsolescence_report.total_detections / 50.0, 1.0)
                quality_factors.append(1.0 - problem_penalty)
            
            # Cobertura bem distribuída
            if coverage_report.total_topics > 0:
                well_covered_ratio = coverage_report.well_covered_topics / coverage_report.total_topics
                quality_factors.append(well_covered_ratio)
            
            return sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
            
        except Exception as e:
            logger.error(f"Erro ao calcular score de qualidade: {e}")
            return 0.0
    
    def _generate_coverage_summary(self, report: CoverageReport) -> Dict[str, Any]:
        """Gera resumo de cobertura"""
        return {
            "overall_coverage": f"{report.overall_coverage:.1%}",
            "total_topics": report.total_topics,
            "well_covered": report.well_covered_topics,
            "poorly_covered": report.poorly_covered_topics,
            "gaps_count": len(report.coverage_gaps),
            "trending_topics": report.trending_topics[:5],
            "top_recommendations": report.recommendations[:3]
        }
    
    def _generate_source_summary(self, report: SourceAnalysisReport) -> Dict[str, Any]:
        """Gera resumo de fontes"""
        return {
            "total_sources": report.total_sources,
            "active_sources": report.active_sources,
            "obsolete_sources": report.obsolete_sources,
            "high_value_sources": report.high_value_sources,
            "low_value_sources": report.low_value_sources,
            "activity_rate": f"{(report.active_sources / max(report.total_sources, 1)):.1%}",
            "top_recommendations": report.recommendations[:3]
        }
    
    def _generate_obsolescence_summary(self, report: ObsolescenceReport) -> Dict[str, Any]:
        """Gera resumo de obsolescência"""
        return {
            "total_detections": report.total_detections,
            "critical_issues": report.critical_issues,
            "high_issues": report.high_issues,
            "medium_issues": report.medium_issues,
            "sources_affected": report.sources_with_issues,
            "top_issues": list(report.summary_by_rule.items())[:5],
            "top_recommendations": report.recommendations[:3]
        }
    
    def _generate_consolidated_recommendations(self, coverage_report: CoverageReport,
                                            source_report: SourceAnalysisReport,
                                            obsolescence_report: ObsolescenceReport) -> List[str]:
        """Gera recomendações consolidadas"""
        recommendations = []
        
        # Prioriza por impacto
        if obsolescence_report.critical_issues > 0:
            recommendations.extend(obsolescence_report.recommendations[:2])
        
        if coverage_report.overall_coverage < 0.6:
            recommendations.extend(coverage_report.recommendations[:2])
        
        if source_report.obsolete_sources > 10:
            recommendations.extend(source_report.recommendations[:2])
        
        # Adiciona outras recomendações
        all_recommendations = (
            coverage_report.recommendations +
            source_report.recommendations +
            obsolescence_report.recommendations
        )
        
        for rec in all_recommendations:
            if rec not in recommendations:
                recommendations.append(rec)
                if len(recommendations) >= 10:
                    break
        
        return recommendations
    
    def _generate_alerts(self, metrics: GovernanceMetrics) -> List[Dict[str, Any]]:
        """Gera alertas baseados nos thresholds"""
        alerts = []
        
        # Alerta de cobertura baixa
        if metrics.overall_coverage < self.alert_thresholds["coverage_min"]:
            alerts.append({
                "type": "warning",
                "category": "coverage",
                "message": f"Cobertura baixa: {metrics.overall_coverage:.1%}",
                "threshold": self.alert_thresholds["coverage_min"],
                "current_value": metrics.overall_coverage
            })
        
        # Alerta de problemas críticos
        if metrics.critical_issues > self.alert_thresholds["critical_issues_max"]:
            alerts.append({
                "type": "critical",
                "category": "security",
                "message": f"{metrics.critical_issues} problemas críticos detectados",
                "threshold": self.alert_thresholds["critical_issues_max"],
                "current_value": metrics.critical_issues
            })
        
        # Alerta de fontes obsoletas
        if metrics.obsolete_sources > self.alert_thresholds["obsolete_sources_max"]:
            alerts.append({
                "type": "warning",
                "category": "maintenance",
                "message": f"{metrics.obsolete_sources} fontes obsoletas",
                "threshold": self.alert_thresholds["obsolete_sources_max"],
                "current_value": metrics.obsolete_sources
            })
        
        # Alerta de score de governança baixo
        if metrics.governance_score < self.alert_thresholds["governance_score_min"]:
            alerts.append({
                "type": "warning",
                "category": "governance",
                "message": f"Score de governança baixo: {metrics.governance_score:.1%}",
                "threshold": self.alert_thresholds["governance_score_min"],
                "current_value": metrics.governance_score
            })
        
        return alerts
    
    def _calculate_trends(self) -> Dict[str, List[float]]:
        """Calcula tendências baseadas no histórico"""
        trends = {}
        
        if len(self.metrics_history) < 2:
            return trends
        
        # Extrai séries temporais
        coverage_trend = [m.overall_coverage for m in self.metrics_history[-7:]]
        governance_trend = [m.governance_score for m in self.metrics_history[-7:]]
        health_trend = [m.health_score for m in self.metrics_history[-7:]]
        critical_issues_trend = [m.critical_issues for m in self.metrics_history[-7:]]
        
        trends = {
            "coverage": coverage_trend,
            "governance_score": governance_trend,
            "health_score": health_trend,
            "critical_issues": critical_issues_trend
        }
        
        return trends
    
    def _export_json_report(self, dashboard: GovernanceDashboard) -> str:
        """Exporta relatório em JSON"""
        try:
            report_file = self.data_dir / f"governance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Converte dashboard para dict
            dashboard_dict = {
                "generated_at": dashboard.generated_at,
                "metrics": {
                    "timestamp": dashboard.metrics.timestamp,
                    "overall_coverage": dashboard.metrics.overall_coverage,
                    "total_topics": dashboard.metrics.total_topics,
                    "coverage_gaps": dashboard.metrics.coverage_gaps,
                    "trending_topics": dashboard.metrics.trending_topics,
                    "total_sources": dashboard.metrics.total_sources,
                    "active_sources": dashboard.metrics.active_sources,
                    "obsolete_sources": dashboard.metrics.obsolete_sources,
                    "high_value_sources": dashboard.metrics.high_value_sources,
                    "total_detections": dashboard.metrics.total_detections,
                    "critical_issues": dashboard.metrics.critical_issues,
                    "high_issues": dashboard.metrics.high_issues,
                    "sources_with_issues": dashboard.metrics.sources_with_issues,
                    "governance_score": dashboard.metrics.governance_score,
                    "health_score": dashboard.metrics.health_score,
                    "quality_score": dashboard.metrics.quality_score
                },
                "coverage_summary": dashboard.coverage_summary,
                "source_summary": dashboard.source_summary,
                "obsolescence_summary": dashboard.obsolescence_summary,
                "recommendations": dashboard.recommendations,
                "alerts": dashboard.alerts,
                "trends": dashboard.trends
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Relatório JSON exportado: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"Erro ao exportar relatório JSON: {e}")
            raise
    
    def _export_markdown_report(self, dashboard: GovernanceDashboard) -> str:
        """Exporta relatório em Markdown"""
        try:
            report_file = self.data_dir / f"governance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            markdown_content = f"""# Relatório de Governança RAG

**Gerado em:** {dashboard.generated_at}

## 📊 Métricas Principais

- **Score de Governança:** {dashboard.metrics.governance_score:.1%}
- **Score de Saúde:** {dashboard.metrics.health_score:.1%}
- **Score de Qualidade:** {dashboard.metrics.quality_score:.1%}

## 🎯 Cobertura

- **Cobertura Geral:** {dashboard.metrics.overall_coverage:.1%}
- **Total de Tópicos:** {dashboard.metrics.total_topics}
- **Lacunas de Cobertura:** {dashboard.metrics.coverage_gaps}
- **Tópicos em Alta:** {', '.join(dashboard.metrics.trending_topics[:5])}

## 📚 Fontes

- **Total de Fontes:** {dashboard.metrics.total_sources}
- **Fontes Ativas:** {dashboard.metrics.active_sources}
- **Fontes Obsoletas:** {dashboard.metrics.obsolete_sources}
- **Fontes de Alto Valor:** {dashboard.metrics.high_value_sources}

## ⚠️ Obsolescência

- **Total de Detecções:** {dashboard.metrics.total_detections}
- **Problemas Críticos:** {dashboard.metrics.critical_issues}
- **Problemas de Alta Prioridade:** {dashboard.metrics.high_issues}
- **Fontes Afetadas:** {dashboard.metrics.sources_with_issues}

## 🚨 Alertas

"""
            
            if dashboard.alerts:
                for alert in dashboard.alerts:
                    icon = "🔴" if alert["type"] == "critical" else "🟡"
                    markdown_content += f"- {icon} **{alert['category'].title()}:** {alert['message']}\n"
            else:
                markdown_content += "- ✅ Nenhum alerta ativo\n"
            
            markdown_content += "\n## 💡 Recomendações\n\n"
            
            for i, rec in enumerate(dashboard.recommendations[:10], 1):
                markdown_content += f"{i}. {rec}\n"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Relatório Markdown exportado: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"Erro ao exportar relatório Markdown: {e}")
            raise
    
    def _export_html_report(self, dashboard: GovernanceDashboard) -> str:
        """Exporta relatório em HTML"""
        # Implementação simplificada - em produção, usar template engine
        try:
            report_file = self.data_dir / f"governance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Relatório de Governança RAG</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .alert {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .critical {{ background: #ffebee; border-left: 4px solid #f44336; }}
        .warning {{ background: #fff3e0; border-left: 4px solid #ff9800; }}
        .score {{ font-size: 24px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>📊 Relatório de Governança RAG</h1>
    <p><strong>Gerado em:</strong> {dashboard.generated_at}</p>
    
    <h2>Métricas Principais</h2>
    <div class="metric">
        <div class="score">Score de Governança: {dashboard.metrics.governance_score:.1%}</div>
        <div class="score">Score de Saúde: {dashboard.metrics.health_score:.1%}</div>
        <div class="score">Score de Qualidade: {dashboard.metrics.quality_score:.1%}</div>
    </div>
    
    <h2>🎯 Cobertura</h2>
    <div class="metric">
        <p><strong>Cobertura Geral:</strong> {dashboard.metrics.overall_coverage:.1%}</p>
        <p><strong>Total de Tópicos:</strong> {dashboard.metrics.total_topics}</p>
        <p><strong>Lacunas:</strong> {dashboard.metrics.coverage_gaps}</p>
    </div>
    
    <h2>📚 Fontes</h2>
    <div class="metric">
        <p><strong>Total:</strong> {dashboard.metrics.total_sources}</p>
        <p><strong>Ativas:</strong> {dashboard.metrics.active_sources}</p>
        <p><strong>Obsoletas:</strong> {dashboard.metrics.obsolete_sources}</p>
        <p><strong>Alto Valor:</strong> {dashboard.metrics.high_value_sources}</p>
    </div>
    
    <h2>⚠️ Obsolescência</h2>
    <div class="metric">
        <p><strong>Total de Detecções:</strong> {dashboard.metrics.total_detections}</p>
        <p><strong>Críticos:</strong> {dashboard.metrics.critical_issues}</p>
        <p><strong>Alta Prioridade:</strong> {dashboard.metrics.high_issues}</p>
    </div>
"""
            
            if dashboard.alerts:
                html_content += "<h2>🚨 Alertas</h2>"
                for alert in dashboard.alerts:
                    css_class = alert["type"]
                    html_content += f'<div class="alert {css_class}"><strong>{alert["category"].title()}:</strong> {alert["message"]}</div>'
            
            html_content += "<h2>💡 Recomendações</h2><ul>"
            for rec in dashboard.recommendations[:10]:
                html_content += f"<li>{rec}</li>"
            html_content += "</ul></body></html>"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Relatório HTML exportado: {report_file}")
            return str(report_file)
            
        except Exception as e:
            logger.error(f"Erro ao exportar relatório HTML: {e}")
            raise
    
    def _save_dashboard(self, dashboard: GovernanceDashboard) -> None:
        """Salva dashboard atual"""
        try:
            dashboard_file = self.data_dir / "latest_dashboard.json"
            
            dashboard_dict = {
                "generated_at": dashboard.generated_at,
                "metrics": {
                    "timestamp": dashboard.metrics.timestamp,
                    "overall_coverage": dashboard.metrics.overall_coverage,
                    "total_topics": dashboard.metrics.total_topics,
                    "coverage_gaps": dashboard.metrics.coverage_gaps,
                    "trending_topics": dashboard.metrics.trending_topics,
                    "total_sources": dashboard.metrics.total_sources,
                    "active_sources": dashboard.metrics.active_sources,
                    "obsolete_sources": dashboard.metrics.obsolete_sources,
                    "high_value_sources": dashboard.metrics.high_value_sources,
                    "total_detections": dashboard.metrics.total_detections,
                    "critical_issues": dashboard.metrics.critical_issues,
                    "high_issues": dashboard.metrics.high_issues,
                    "sources_with_issues": dashboard.metrics.sources_with_issues,
                    "governance_score": dashboard.metrics.governance_score,
                    "health_score": dashboard.metrics.health_score,
                    "quality_score": dashboard.metrics.quality_score
                },
                "coverage_summary": dashboard.coverage_summary,
                "source_summary": dashboard.source_summary,
                "obsolescence_summary": dashboard.obsolescence_summary,
                "recommendations": dashboard.recommendations,
                "alerts": dashboard.alerts,
                "trends": dashboard.trends
            }
            
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_dict, f, indent=2, ensure_ascii=False)
            
            # Salva histórico de métricas
            self._save_metrics_history()
            
            logger.info(f"Dashboard salvo: {dashboard_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar dashboard: {e}")
    
    def _load_metrics_history(self) -> None:
        """Carrega histórico de métricas"""
        try:
            history_file = self.data_dir / "metrics_history.json"
            
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Carrega métricas (apenas as recentes)
                cutoff_date = datetime.now() - timedelta(days=self.max_history_days)
                
                for metrics_data in data.get("metrics", []):
                    timestamp = datetime.fromisoformat(metrics_data["timestamp"])
                    if timestamp > cutoff_date:
                        metrics = GovernanceMetrics(**metrics_data)
                        self.metrics_history.append(metrics)
                
                logger.info(f"Histórico de métricas carregado: {len(self.metrics_history)} registros")
                
        except Exception as e:
            logger.warning(f"Erro ao carregar histórico de métricas: {e}")
    
    def _save_metrics_history(self) -> None:
        """Salva histórico de métricas"""
        try:
            history_file = self.data_dir / "metrics_history.json"
            
            data = {
                "saved_at": datetime.now().isoformat(),
                "metrics": [
                    {
                        "timestamp": m.timestamp,
                        "overall_coverage": m.overall_coverage,
                        "total_topics": m.total_topics,
                        "coverage_gaps": m.coverage_gaps,
                        "trending_topics": m.trending_topics,
                        "total_sources": m.total_sources,
                        "active_sources": m.active_sources,
                        "obsolete_sources": m.obsolete_sources,
                        "high_value_sources": m.high_value_sources,
                        "total_detections": m.total_detections,
                        "critical_issues": m.critical_issues,
                        "high_issues": m.high_issues,
                        "sources_with_issues": m.sources_with_issues,
                        "governance_score": m.governance_score,
                        "health_score": m.health_score,
                        "quality_score": m.quality_score
                    }
                    for m in self.metrics_history
                ]
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Histórico de métricas salvo: {history_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar histórico de métricas: {e}")
    
    def _trim_metrics_history(self) -> None:
        """Remove métricas antigas do histórico"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.max_history_days)
            
            old_count = len(self.metrics_history)
            self.metrics_history = [
                m for m in self.metrics_history
                if datetime.fromisoformat(m.timestamp) > cutoff_date
            ]
            
            removed_count = old_count - len(self.metrics_history)
            if removed_count > 0:
                logger.info(f"Removidas {removed_count} métricas antigas do histórico")
                
        except Exception as e:
            logger.error(f"Erro ao limpar histórico de métricas: {e}")