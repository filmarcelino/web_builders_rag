#!/usr/bin/env python3
"""
Observability Module - Sistema de Observabilidade

Este módulo fornece capacidades completas de observabilidade para o sistema RAG,
incluindo coleta de métricas, avaliação de qualidade, monitoramento de performance,
logging estruturado, alertas e dashboards.
"""

from .metrics_collector import (
    MetricsCollector,
    SearchMetrics
)

from .performance_monitor import (
    PerformanceMonitor,
    SystemMetrics,
    PerformanceMetrics,
    PerformanceStats
)

from .quality_evaluator import (
    QualityEvaluator,
    QualityScores,
    EvaluationResult
)

# Removed duplicate import - already imported above

from .logging_manager import (
    LoggingManager,
    LogLevel,
    LogEntry,
    StructuredFormatter,
    logging_manager,
    get_logger,
    log_context,
    set_log_context,
    log_function_calls
)

from .alert_manager import (
    AlertManager,
    AlertRule,
    Alert,
    AlertSeverity,
    AlertStatus,
    NotificationChannel,
    NotificationConfig,
    alert_manager,
    add_metric,
    create_alert_rule,
    get_active_alerts,
    get_alert_stats
)

from .dashboard_generator import (
    DashboardGenerator,
    DashboardConfig,
    ChartData,
    dashboard_generator,
    generate_dashboard,
    generate_report
)

__all__ = [
    # Classes principais
    'MetricsCollector',
    'QualityEvaluator',
    'PerformanceMonitor',
    'LoggingManager',
    'AlertManager',
    'DashboardGenerator',
    
    # Dataclasses e Enums
    'SystemMetrics',
    'SearchMetrics', 
    'IndexingMetrics',
    'APIMetrics',
    'QualityScores',
    'EvaluationResult',
    'PerformanceMetrics',
    'PerfSystemMetrics',
    'PerformanceStats',
    'LogLevel',
    'LogEntry',
    'StructuredFormatter',
    'AlertRule',
    'Alert',
    'AlertSeverity',
    'AlertStatus',
    'NotificationChannel',
    'NotificationConfig',
    'DashboardConfig',
    'ChartData',
    
    # Instâncias globais
    'metrics_collector',
    'quality_evaluator',
    'performance_monitor',
    'logging_manager',
    'alert_manager',
    'dashboard_generator',
    
    # Funções de conveniência
    'monitor_operation',
    'get_logger',
    'log_context',
    'set_log_context',
    'log_function_calls',
    'add_metric',
    'create_alert_rule',
    'get_active_alerts',
    'get_alert_stats',
    'generate_dashboard',
    'generate_report'
]