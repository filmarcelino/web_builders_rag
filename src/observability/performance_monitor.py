#!/usr/bin/env python3
"""
Performance Monitor - Sistema de Monitoramento de Performance

Este módulo monitora a performance do sistema RAG em tempo real,
coletando métricas de latência, throughput, uso de recursos e
identificando gargalos de performance.
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import statistics
from contextlib import contextmanager

@dataclass
class PerformanceMetrics:
    """Métricas de performance de uma operação"""
    operation: str
    start_time: float
    end_time: float
    duration: float
    cpu_usage: float
    memory_usage: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.start_time)

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    active_threads: int
    
@dataclass
class PerformanceStats:
    """Estatísticas agregadas de performance"""
    operation: str
    total_calls: int
    success_rate: float
    avg_duration: float
    min_duration: float
    max_duration: float
    p50_duration: float
    p95_duration: float
    p99_duration: float
    avg_cpu_usage: float
    avg_memory_usage: float
    calls_per_minute: float
    error_count: int
    last_updated: datetime

class PerformanceMonitor:
    """Monitor de performance do sistema RAG"""
    
    def __init__(self, 
                 max_metrics_history: int = 10000,
                 system_monitoring_interval: float = 30.0,
                 enable_system_monitoring: bool = True):
        self.max_metrics_history = max_metrics_history
        self.system_monitoring_interval = system_monitoring_interval
        self.enable_system_monitoring = enable_system_monitoring
        
        # Armazenamento de métricas
        self.metrics_history: deque = deque(maxlen=max_metrics_history)
        self.system_metrics_history: deque = deque(maxlen=1000)
        self.operation_metrics: Dict[str, List[PerformanceMetrics]] = defaultdict(list)
        
        # Controle de threading
        self._lock = threading.Lock()
        self._system_monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        
        # Cache de estatísticas
        self._stats_cache: Dict[str, PerformanceStats] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=5)
        
        # Alertas de performance
        self.alert_thresholds = {
            'max_duration': 30.0,  # segundos
            'max_cpu_usage': 80.0,  # porcentagem
            'max_memory_usage': 85.0,  # porcentagem
            'min_success_rate': 95.0  # porcentagem
        }
        
        self.alert_callbacks: List[Callable] = []
        
        # Inicia monitoramento do sistema
        if self.enable_system_monitoring:
            self._start_system_monitoring()
    
    def _start_system_monitoring(self):
        """Inicia thread de monitoramento do sistema"""
        self._system_monitor_thread = threading.Thread(
            target=self._system_monitor_loop,
            daemon=True
        )
        self._system_monitor_thread.start()
    
    def _system_monitor_loop(self):
        """Loop de monitoramento do sistema"""
        while not self._stop_monitoring.wait(self.system_monitoring_interval):
            try:
                metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=psutil.cpu_percent(interval=1),
                    memory_percent=psutil.virtual_memory().percent,
                    memory_used_mb=psutil.virtual_memory().used / (1024 * 1024),
                    disk_usage_percent=psutil.disk_usage('/').percent,
                    active_threads=threading.active_count()
                )
                
                with self._lock:
                    self.system_metrics_history.append(metrics)
                    
            except Exception as e:
                print(f"Erro no monitoramento do sistema: {e}")
    
    @contextmanager
    def monitor_operation(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager para monitorar uma operação"""
        start_time = time.time()
        start_cpu = psutil.cpu_percent()
        start_memory = psutil.virtual_memory().percent
        
        success = True
        error_message = None
        
        try:
            yield
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            end_cpu = psutil.cpu_percent()
            end_memory = psutil.virtual_memory().percent
            
            metrics = PerformanceMetrics(
                operation=operation,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                cpu_usage=(start_cpu + end_cpu) / 2,
                memory_usage=(start_memory + end_memory) / 2,
                success=success,
                error_message=error_message,
                metadata=metadata or {}
            )
            
            self.record_metrics(metrics)
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """Registra métricas de performance"""
        with self._lock:
            self.metrics_history.append(metrics)
            self.operation_metrics[metrics.operation].append(metrics)
            
            # Limita histórico por operação
            if len(self.operation_metrics[metrics.operation]) > 1000:
                self.operation_metrics[metrics.operation] = \
                    self.operation_metrics[metrics.operation][-1000:]
            
            # Invalida cache de estatísticas
            if metrics.operation in self._stats_cache:
                del self._stats_cache[metrics.operation]
                del self._cache_expiry[metrics.operation]
        
        # Verifica alertas
        self._check_alerts(metrics)
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Verifica se métricas excedem thresholds de alerta"""
        alerts = []
        
        if metrics.duration > self.alert_thresholds['max_duration']:
            alerts.append({
                'type': 'high_latency',
                'operation': metrics.operation,
                'value': metrics.duration,
                'threshold': self.alert_thresholds['max_duration'],
                'timestamp': metrics.timestamp
            })
        
        if metrics.cpu_usage > self.alert_thresholds['max_cpu_usage']:
            alerts.append({
                'type': 'high_cpu',
                'operation': metrics.operation,
                'value': metrics.cpu_usage,
                'threshold': self.alert_thresholds['max_cpu_usage'],
                'timestamp': metrics.timestamp
            })
        
        if metrics.memory_usage > self.alert_thresholds['max_memory_usage']:
            alerts.append({
                'type': 'high_memory',
                'operation': metrics.operation,
                'value': metrics.memory_usage,
                'threshold': self.alert_thresholds['max_memory_usage'],
                'timestamp': metrics.timestamp
            })
        
        # Dispara callbacks de alerta
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    print(f"Erro em callback de alerta: {e}")
    
    def get_operation_stats(self, operation: str, 
                           time_window: Optional[timedelta] = None) -> Optional[PerformanceStats]:
        """Obtém estatísticas de uma operação"""
        # Verifica cache
        if (operation in self._stats_cache and 
            operation in self._cache_expiry and
            datetime.now() < self._cache_expiry[operation]):
            return self._stats_cache[operation]
        
        with self._lock:
            if operation not in self.operation_metrics:
                return None
            
            metrics_list = self.operation_metrics[operation]
            
            # Filtra por janela de tempo se especificada
            if time_window:
                cutoff_time = datetime.now() - time_window
                metrics_list = [
                    m for m in metrics_list 
                    if m.timestamp >= cutoff_time
                ]
            
            if not metrics_list:
                return None
            
            # Calcula estatísticas
            durations = [m.duration for m in metrics_list]
            cpu_usages = [m.cpu_usage for m in metrics_list]
            memory_usages = [m.memory_usage for m in metrics_list]
            successes = [m.success for m in metrics_list]
            
            # Calcula calls per minute
            if len(metrics_list) > 1:
                time_span = (metrics_list[-1].timestamp - metrics_list[0].timestamp).total_seconds() / 60
                calls_per_minute = len(metrics_list) / max(time_span, 1)
            else:
                calls_per_minute = 0
            
            stats = PerformanceStats(
                operation=operation,
                total_calls=len(metrics_list),
                success_rate=(sum(successes) / len(successes)) * 100,
                avg_duration=statistics.mean(durations),
                min_duration=min(durations),
                max_duration=max(durations),
                p50_duration=statistics.median(durations),
                p95_duration=self._percentile(durations, 95),
                p99_duration=self._percentile(durations, 99),
                avg_cpu_usage=statistics.mean(cpu_usages),
                avg_memory_usage=statistics.mean(memory_usages),
                calls_per_minute=calls_per_minute,
                error_count=len([m for m in metrics_list if not m.success]),
                last_updated=datetime.now()
            )
            
            # Atualiza cache
            self._stats_cache[operation] = stats
            self._cache_expiry[operation] = datetime.now() + self._cache_ttl
            
            return stats
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calcula percentil"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def get_all_operations_stats(self, 
                                time_window: Optional[timedelta] = None) -> Dict[str, PerformanceStats]:
        """Obtém estatísticas de todas as operações"""
        stats = {}
        for operation in self.operation_metrics.keys():
            operation_stats = self.get_operation_stats(operation, time_window)
            if operation_stats:
                stats[operation] = operation_stats
        return stats
    
    def get_system_metrics(self, 
                          time_window: Optional[timedelta] = None) -> List[SystemMetrics]:
        """Obtém métricas do sistema"""
        with self._lock:
            metrics = list(self.system_metrics_history)
        
        if time_window:
            cutoff_time = datetime.now() - time_window
            metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        return metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtém resumo geral de performance"""
        with self._lock:
            total_operations = len(self.metrics_history)
            if total_operations == 0:
                return {'total_operations': 0}
            
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= datetime.now() - timedelta(hours=1)
            ]
            
            operations_stats = self.get_all_operations_stats(timedelta(hours=24))
            
            # Métricas do sistema mais recentes
            latest_system = None
            if self.system_metrics_history:
                latest_system = self.system_metrics_history[-1]
            
            return {
                'total_operations': total_operations,
                'recent_operations_1h': len(recent_metrics),
                'operations_stats': {op: {
                    'total_calls': stats.total_calls,
                    'success_rate': stats.success_rate,
                    'avg_duration': stats.avg_duration,
                    'p95_duration': stats.p95_duration,
                    'calls_per_minute': stats.calls_per_minute
                } for op, stats in operations_stats.items()},
                'system_status': {
                    'cpu_percent': latest_system.cpu_percent if latest_system else None,
                    'memory_percent': latest_system.memory_percent if latest_system else None,
                    'active_threads': latest_system.active_threads if latest_system else None
                } if latest_system else None,
                'last_updated': datetime.now().isoformat()
            }
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Adiciona callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def update_alert_thresholds(self, thresholds: Dict[str, float]):
        """Atualiza thresholds de alerta"""
        self.alert_thresholds.update(thresholds)
    
    def export_metrics(self, 
                      operation: Optional[str] = None,
                      time_window: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """Exporta métricas para análise externa"""
        with self._lock:
            if operation:
                metrics_list = self.operation_metrics.get(operation, [])
            else:
                metrics_list = list(self.metrics_history)
        
        if time_window:
            cutoff_time = datetime.now() - time_window
            metrics_list = [
                m for m in metrics_list 
                if m.timestamp >= cutoff_time
            ]
        
        return [
            {
                'operation': m.operation,
                'timestamp': m.timestamp.isoformat(),
                'duration': m.duration,
                'cpu_usage': m.cpu_usage,
                'memory_usage': m.memory_usage,
                'success': m.success,
                'error_message': m.error_message,
                'metadata': m.metadata
            }
            for m in metrics_list
        ]
    
    def clear_metrics(self, operation: Optional[str] = None):
        """Limpa métricas armazenadas"""
        with self._lock:
            if operation:
                if operation in self.operation_metrics:
                    del self.operation_metrics[operation]
                if operation in self._stats_cache:
                    del self._stats_cache[operation]
                    del self._cache_expiry[operation]
            else:
                self.metrics_history.clear()
                self.operation_metrics.clear()
                self._stats_cache.clear()
                self._cache_expiry.clear()
    
    def stop_monitoring(self):
        """Para o monitoramento do sistema"""
        self._stop_monitoring.set()
        if self._system_monitor_thread:
            self._system_monitor_thread.join(timeout=5)
    
    def __del__(self):
        """Cleanup ao destruir objeto"""
        self.stop_monitoring()

# Instância global do monitor
performance_monitor = PerformanceMonitor()

# Decorator para monitoramento automático
def monitor_performance(operation_name: str = None, metadata: Dict[str, Any] = None):
    """Decorator para monitorar performance de funções"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            with performance_monitor.monitor_operation(op_name, metadata):
                return func(*args, **kwargs)
        return wrapper
    return decorator