#!/usr/bin/env python3
"""
Governance Module - Módulo de Governança

Este módulo fornece ferramentas para monitorar e gerenciar a qualidade,
cobertura e relevância das fontes no sistema RAG.

Componentes:
- Coverage Monitor: Monitora cobertura de tópicos e lacunas
- Source Analyzer: Analisa utilidade e relevância das fontes
- Obsolescence Detector: Detecta conteúdo obsoleto ou desatualizado
- Governance Dashboard: Interface para visualização e gestão
"""

from .coverage_monitor import CoverageMonitor, TopicCoverage, CoverageReport
from .source_analyzer import SourceAnalyzer, SourceMetrics, SourceAnalysisReport
from .obsolescence_detector import ObsolescenceDetector, ObsolescenceRule, ObsolescenceDetection, ObsolescenceReport
from .governance_dashboard import GovernanceDashboardGenerator, GovernanceDashboard, GovernanceMetrics

# Instâncias globais para uso direto
coverage_monitor = CoverageMonitor()
source_analyzer = SourceAnalyzer()
obsolescence_detector = ObsolescenceDetector()
governance_dashboard = GovernanceDashboardGenerator()

__all__ = [
    # Classes principais
    "CoverageMonitor",
    "SourceAnalyzer", 
    "ObsolescenceDetector",
    "GovernanceDashboardGenerator",
    
    # Data classes
    "TopicCoverage",
    "CoverageReport",
    "SourceMetrics",
    "SourceAnalysisReport",
    "ObsolescenceRule",
    "ObsolescenceDetection",
    "ObsolescenceReport",
    "GovernanceDashboard",
    "GovernanceMetrics",
    
    # Instâncias globais
    "coverage_monitor",
    "source_analyzer",
    "obsolescence_detector",
    "governance_dashboard"
]