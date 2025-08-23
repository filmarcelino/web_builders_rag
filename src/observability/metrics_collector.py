import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import sqlite3
import os

@dataclass
class SearchMetrics:
    """Métricas de uma busca individual"""
    query_id: str
    query: str
    timestamp: str
    user_context: Optional[Dict[str, Any]]
    
    # Métricas de performance
    total_latency_ms: float
    query_processing_ms: float
    search_execution_ms: float
    reranking_ms: float
    
    # Métricas de resultados
    total_results_found: int
    results_returned: int
    results_after_reranking: int
    
    # Métricas de qualidade
    context_relevance: Optional[float] = None
    faithfulness: Optional[float] = None
    semantic_answer_similarity: Optional[float] = None
    
    # Feedback do usuário
    user_feedback: Optional[Dict[str, Any]] = None
    results_clicked: List[str] = None
    results_used: List[str] = None
    
    # Metadados
    search_type: str = "hybrid"  # vector, text, hybrid
    filters_applied: Optional[Dict[str, Any]] = None
    cache_hit: bool = False

@dataclass
class AggregatedMetrics:
    """Métricas agregadas por período"""
    period_start: str
    period_end: str
    total_searches: int
    
    # Performance médias
    avg_latency_ms: float
    p95_latency_ms: float
    avg_results_returned: float
    
    # Qualidade médias
    avg_context_relevance: float
    avg_faithfulness: float
    avg_sas: float
    
    # Distribuições
    search_type_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    stack_distribution: Dict[str, int]
    
    # Taxa de sucesso
    cache_hit_rate: float
    user_satisfaction_rate: float

class MetricsCollector:
    """Coletor central de métricas do RAG"""
    
    def __init__(self, db_path: str = "data/metrics.db", 
                 retention_days: int = 90):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.retention_days = retention_days
        
        # Buffer em memória para métricas recentes
        self._metrics_buffer = deque(maxlen=1000)
        self._buffer_lock = threading.Lock()
        
        # Cache de métricas agregadas
        self._aggregated_cache = {}
        self._cache_lock = threading.Lock()
        
        # Contadores em tempo real
        self._realtime_counters = {
            'total_searches': 0,
            'searches_last_hour': deque(maxlen=3600),  # 1 por segundo
            'avg_latency_window': deque(maxlen=100),
            'quality_scores_window': deque(maxlen=100)
        }
        
        # Inicializa banco de dados
        self._init_database()
        
        # Thread para flush periódico
        self._flush_thread = threading.Thread(target=self._periodic_flush, daemon=True)
        self._flush_thread.start()
        
        self.logger.info(f"MetricsCollector inicializado (db: {db_path})")
    
    def record_search_metrics(self, metrics: SearchMetrics):
        """Registra métricas de uma busca"""
        try:
            # Adiciona ao buffer
            with self._buffer_lock:
                self._metrics_buffer.append(metrics)
            
            # Atualiza contadores em tempo real
            self._update_realtime_counters(metrics)
            
            # Log estruturado
            self.logger.info(
                "Search completed",
                extra={
                    'query_id': metrics.query_id,
                    'latency_ms': metrics.total_latency_ms,
                    'results_returned': metrics.results_returned,
                    'search_type': metrics.search_type,
                    'cache_hit': metrics.cache_hit
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar métricas: {str(e)}")
    
    def update_quality_metrics(self, query_id: str, 
                             context_relevance: Optional[float] = None,
                             faithfulness: Optional[float] = None,
                             sas: Optional[float] = None):
        """Atualiza métricas de qualidade para uma busca"""
        try:
            # Atualiza no buffer
            with self._buffer_lock:
                for metrics in reversed(self._metrics_buffer):
                    if metrics.query_id == query_id:
                        if context_relevance is not None:
                            metrics.context_relevance = context_relevance
                        if faithfulness is not None:
                            metrics.faithfulness = faithfulness
                        if sas is not None:
                            metrics.semantic_answer_similarity = sas
                        break
            
            # Atualiza no banco de dados
            self._update_quality_in_db(query_id, context_relevance, faithfulness, sas)
            
            # Atualiza janela de qualidade
            if any(score is not None for score in [context_relevance, faithfulness, sas]):
                quality_scores = [s for s in [context_relevance, faithfulness, sas] if s is not None]
                avg_quality = sum(quality_scores) / len(quality_scores)
                self._realtime_counters['quality_scores_window'].append(avg_quality)
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar métricas de qualidade: {str(e)}")
    
    def record_user_feedback(self, query_id: str, feedback: Dict[str, Any]):
        """Registra feedback do usuário"""
        try:
            # Atualiza no buffer
            with self._buffer_lock:
                for metrics in reversed(self._metrics_buffer):
                    if metrics.query_id == query_id:
                        metrics.user_feedback = feedback
                        
                        # Extrai informações de uso
                        if 'results_clicked' in feedback:
                            metrics.results_clicked = feedback['results_clicked']
                        if 'results_used' in feedback:
                            metrics.results_used = feedback['results_used']
                        break
            
            # Persiste no banco
            self._update_feedback_in_db(query_id, feedback)
            
            self.logger.info(
                "User feedback recorded",
                extra={
                    'query_id': query_id,
                    'feedback_type': feedback.get('type', 'unknown'),
                    'satisfaction': feedback.get('satisfaction')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar feedback: {str(e)}")
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Retorna métricas em tempo real"""
        try:
            current_time = time.time()
            
            # Searches na última hora
            hour_ago = current_time - 3600
            searches_last_hour = sum(
                1 for timestamp in self._realtime_counters['searches_last_hour']
                if timestamp > hour_ago
            )
            
            # Latência média recente
            latency_window = self._realtime_counters['avg_latency_window']
            avg_latency = sum(latency_window) / len(latency_window) if latency_window else 0
            
            # Qualidade média recente
            quality_window = self._realtime_counters['quality_scores_window']
            avg_quality = sum(quality_window) / len(quality_window) if quality_window else 0
            
            return {
                'total_searches': self._realtime_counters['total_searches'],
                'searches_last_hour': searches_last_hour,
                'avg_latency_ms': avg_latency,
                'avg_quality_score': avg_quality,
                'buffer_size': len(self._metrics_buffer),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas em tempo real: {str(e)}")
            return {}
    
    def get_aggregated_metrics(self, period: str = "1h", 
                             start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None) -> AggregatedMetrics:
        """Retorna métricas agregadas por período"""
        try:
            # Define período se não especificado
            if not end_time:
                end_time = datetime.now()
            
            if not start_time:
                if period == "1h":
                    start_time = end_time - timedelta(hours=1)
                elif period == "1d":
                    start_time = end_time - timedelta(days=1)
                elif period == "1w":
                    start_time = end_time - timedelta(weeks=1)
                else:
                    start_time = end_time - timedelta(hours=1)
            
            # Verifica cache
            cache_key = f"{period}_{start_time.isoformat()}_{end_time.isoformat()}"
            with self._cache_lock:
                if cache_key in self._aggregated_cache:
                    cache_entry = self._aggregated_cache[cache_key]
                    # Cache válido por 5 minutos
                    if (datetime.now() - cache_entry['timestamp']).seconds < 300:
                        return cache_entry['metrics']
            
            # Calcula métricas agregadas
            aggregated = self._calculate_aggregated_metrics(start_time, end_time)
            
            # Atualiza cache
            with self._cache_lock:
                self._aggregated_cache[cache_key] = {
                    'metrics': aggregated,
                    'timestamp': datetime.now()
                }
            
            return aggregated
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas agregadas: {str(e)}")
            return self._create_empty_aggregated_metrics(start_time, end_time)
    
    def get_search_history(self, limit: int = 100, 
                          filters: Optional[Dict[str, Any]] = None) -> List[SearchMetrics]:
        """Retorna histórico de buscas"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM search_metrics WHERE 1=1"
            params = []
            
            # Aplica filtros
            if filters:
                if 'start_time' in filters:
                    query += " AND timestamp >= ?"
                    params.append(filters['start_time'])
                
                if 'end_time' in filters:
                    query += " AND timestamp <= ?"
                    params.append(filters['end_time'])
                
                if 'search_type' in filters:
                    query += " AND search_type = ?"
                    params.append(filters['search_type'])
                
                if 'min_latency' in filters:
                    query += " AND total_latency_ms >= ?"
                    params.append(filters['min_latency'])
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            # Converte para SearchMetrics
            search_history = []
            for row in rows:
                metrics = SearchMetrics(
                    query_id=row['query_id'],
                    query=row['query'],
                    timestamp=row['timestamp'],
                    user_context=json.loads(row['user_context']) if row['user_context'] else None,
                    total_latency_ms=row['total_latency_ms'],
                    query_processing_ms=row['query_processing_ms'],
                    search_execution_ms=row['search_execution_ms'],
                    reranking_ms=row['reranking_ms'],
                    total_results_found=row['total_results_found'],
                    results_returned=row['results_returned'],
                    results_after_reranking=row['results_after_reranking'],
                    context_relevance=row['context_relevance'],
                    faithfulness=row['faithfulness'],
                    semantic_answer_similarity=row['semantic_answer_similarity'],
                    user_feedback=json.loads(row['user_feedback']) if row['user_feedback'] else None,
                    results_clicked=json.loads(row['results_clicked']) if row['results_clicked'] else [],
                    results_used=json.loads(row['results_used']) if row['results_used'] else [],
                    search_type=row['search_type'],
                    filters_applied=json.loads(row['filters_applied']) if row['filters_applied'] else None,
                    cache_hit=bool(row['cache_hit'])
                )
                search_history.append(metrics)
            
            return search_history
            
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {str(e)}")
            return []
    
    def get_top_queries(self, limit: int = 10, period_days: int = 7) -> List[Dict[str, Any]]:
        """Retorna queries mais frequentes"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            start_date = (datetime.now() - timedelta(days=period_days)).isoformat()
            
            query = """
                SELECT query, COUNT(*) as frequency,
                       AVG(total_latency_ms) as avg_latency,
                       AVG(context_relevance) as avg_relevance
                FROM search_metrics 
                WHERE timestamp >= ?
                GROUP BY query 
                ORDER BY frequency DESC 
                LIMIT ?
            """
            
            cursor = conn.execute(query, [start_date, limit])
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'query': row[0],
                    'frequency': row[1],
                    'avg_latency_ms': row[2] or 0,
                    'avg_relevance': row[3] or 0
                }
                for row in rows
            ]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter top queries: {str(e)}")
            return []
    
    def _init_database(self):
        """Inicializa banco de dados"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            
            # Tabela principal de métricas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_metrics (
                    query_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_context TEXT,
                    total_latency_ms REAL NOT NULL,
                    query_processing_ms REAL NOT NULL,
                    search_execution_ms REAL NOT NULL,
                    reranking_ms REAL NOT NULL,
                    total_results_found INTEGER NOT NULL,
                    results_returned INTEGER NOT NULL,
                    results_after_reranking INTEGER NOT NULL,
                    context_relevance REAL,
                    faithfulness REAL,
                    semantic_answer_similarity REAL,
                    user_feedback TEXT,
                    results_clicked TEXT,
                    results_used TEXT,
                    search_type TEXT NOT NULL,
                    filters_applied TEXT,
                    cache_hit INTEGER NOT NULL
                )
            """)
            
            # Índices para performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON search_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_query ON search_metrics(query)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_type ON search_metrics(search_type)")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco: {str(e)}")
    
    def _update_realtime_counters(self, metrics: SearchMetrics):
        """Atualiza contadores em tempo real"""
        current_time = time.time()
        
        self._realtime_counters['total_searches'] += 1
        self._realtime_counters['searches_last_hour'].append(current_time)
        self._realtime_counters['avg_latency_window'].append(metrics.total_latency_ms)
    
    def _periodic_flush(self):
        """Thread para flush periódico do buffer"""
        while True:
            try:
                time.sleep(60)  # Flush a cada minuto
                self._flush_buffer_to_db()
                self._cleanup_old_data()
            except Exception as e:
                self.logger.error(f"Erro no flush periódico: {str(e)}")
    
    def _flush_buffer_to_db(self):
        """Flush do buffer para o banco de dados"""
        try:
            with self._buffer_lock:
                if not self._metrics_buffer:
                    return
                
                metrics_to_flush = list(self._metrics_buffer)
                self._metrics_buffer.clear()
            
            conn = sqlite3.connect(self.db_path)
            
            for metrics in metrics_to_flush:
                conn.execute("""
                    INSERT OR REPLACE INTO search_metrics VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.query_id,
                    metrics.query,
                    metrics.timestamp,
                    json.dumps(metrics.user_context) if metrics.user_context else None,
                    metrics.total_latency_ms,
                    metrics.query_processing_ms,
                    metrics.search_execution_ms,
                    metrics.reranking_ms,
                    metrics.total_results_found,
                    metrics.results_returned,
                    metrics.results_after_reranking,
                    metrics.context_relevance,
                    metrics.faithfulness,
                    metrics.semantic_answer_similarity,
                    json.dumps(metrics.user_feedback) if metrics.user_feedback else None,
                    json.dumps(metrics.results_clicked) if metrics.results_clicked else None,
                    json.dumps(metrics.results_used) if metrics.results_used else None,
                    metrics.search_type,
                    json.dumps(metrics.filters_applied) if metrics.filters_applied else None,
                    int(metrics.cache_hit)
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Flushed {len(metrics_to_flush)} metrics to database")
            
        except Exception as e:
            self.logger.error(f"Erro no flush para DB: {str(e)}")
    
    def _update_quality_in_db(self, query_id: str, context_relevance: Optional[float],
                             faithfulness: Optional[float], sas: Optional[float]):
        """Atualiza métricas de qualidade no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            updates = []
            params = []
            
            if context_relevance is not None:
                updates.append("context_relevance = ?")
                params.append(context_relevance)
            
            if faithfulness is not None:
                updates.append("faithfulness = ?")
                params.append(faithfulness)
            
            if sas is not None:
                updates.append("semantic_answer_similarity = ?")
                params.append(sas)
            
            if updates:
                params.append(query_id)
                query = f"UPDATE search_metrics SET {', '.join(updates)} WHERE query_id = ?"
                conn.execute(query, params)
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar qualidade no DB: {str(e)}")
    
    def _update_feedback_in_db(self, query_id: str, feedback: Dict[str, Any]):
        """Atualiza feedback no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            updates = ["user_feedback = ?"]
            params = [json.dumps(feedback)]
            
            if 'results_clicked' in feedback:
                updates.append("results_clicked = ?")
                params.append(json.dumps(feedback['results_clicked']))
            
            if 'results_used' in feedback:
                updates.append("results_used = ?")
                params.append(json.dumps(feedback['results_used']))
            
            params.append(query_id)
            query = f"UPDATE search_metrics SET {', '.join(updates)} WHERE query_id = ?"
            
            conn.execute(query, params)
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar feedback no DB: {str(e)}")
    
    def _calculate_aggregated_metrics(self, start_time: datetime, 
                                    end_time: datetime) -> AggregatedMetrics:
        """Calcula métricas agregadas para um período"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Query principal
            query = """
                SELECT 
                    COUNT(*) as total_searches,
                    AVG(total_latency_ms) as avg_latency,
                    AVG(results_returned) as avg_results,
                    AVG(context_relevance) as avg_relevance,
                    AVG(faithfulness) as avg_faithfulness,
                    AVG(semantic_answer_similarity) as avg_sas,
                    search_type,
                    cache_hit
                FROM search_metrics 
                WHERE timestamp BETWEEN ? AND ?
            """
            
            cursor = conn.execute(query, [start_time.isoformat(), end_time.isoformat()])
            row = cursor.fetchone()
            
            if not row or row[0] == 0:
                return self._create_empty_aggregated_metrics(start_time, end_time)
            
            # Distribuições
            search_type_dist = self._get_distribution(conn, "search_type", start_time, end_time)
            
            # P95 latency
            p95_query = """
                SELECT total_latency_ms 
                FROM search_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY total_latency_ms 
                LIMIT 1 OFFSET (SELECT COUNT(*) * 0.95 FROM search_metrics WHERE timestamp BETWEEN ? AND ?)
            """
            cursor = conn.execute(p95_query, [start_time.isoformat(), end_time.isoformat(),
                                            start_time.isoformat(), end_time.isoformat()])
            p95_row = cursor.fetchone()
            p95_latency = p95_row[0] if p95_row else row[1]
            
            # Cache hit rate
            cache_query = """
                SELECT AVG(CAST(cache_hit AS FLOAT)) 
                FROM search_metrics 
                WHERE timestamp BETWEEN ? AND ?
            """
            cursor = conn.execute(cache_query, [start_time.isoformat(), end_time.isoformat()])
            cache_row = cursor.fetchone()
            cache_hit_rate = cache_row[0] if cache_row and cache_row[0] else 0
            
            conn.close()
            
            return AggregatedMetrics(
                period_start=start_time.isoformat(),
                period_end=end_time.isoformat(),
                total_searches=row[0],
                avg_latency_ms=row[1] or 0,
                p95_latency_ms=p95_latency or 0,
                avg_results_returned=row[2] or 0,
                avg_context_relevance=row[3] or 0,
                avg_faithfulness=row[4] or 0,
                avg_sas=row[5] or 0,
                search_type_distribution=search_type_dist,
                category_distribution={},  # TODO: implementar
                stack_distribution={},     # TODO: implementar
                cache_hit_rate=cache_hit_rate,
                user_satisfaction_rate=0.0  # TODO: implementar
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular métricas agregadas: {str(e)}")
            return self._create_empty_aggregated_metrics(start_time, end_time)
    
    def _get_distribution(self, conn: sqlite3.Connection, column: str, 
                         start_time: datetime, end_time: datetime) -> Dict[str, int]:
        """Obtém distribuição de valores para uma coluna"""
        try:
            query = f"""
                SELECT {column}, COUNT(*) 
                FROM search_metrics 
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY {column}
            """
            
            cursor = conn.execute(query, [start_time.isoformat(), end_time.isoformat()])
            rows = cursor.fetchall()
            
            return {row[0]: row[1] for row in rows}
            
        except Exception as e:
            self.logger.error(f"Erro ao obter distribuição de {column}: {str(e)}")
            return {}
    
    def _create_empty_aggregated_metrics(self, start_time: datetime, 
                                       end_time: datetime) -> AggregatedMetrics:
        """Cria métricas agregadas vazias"""
        return AggregatedMetrics(
            period_start=start_time.isoformat(),
            period_end=end_time.isoformat(),
            total_searches=0,
            avg_latency_ms=0,
            p95_latency_ms=0,
            avg_results_returned=0,
            avg_context_relevance=0,
            avg_faithfulness=0,
            avg_sas=0,
            search_type_distribution={},
            category_distribution={},
            stack_distribution={},
            cache_hit_rate=0,
            user_satisfaction_rate=0
        )
    
    def _cleanup_old_data(self):
        """Remove dados antigos baseado na retenção"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=self.retention_days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("DELETE FROM search_metrics WHERE timestamp < ?", [cutoff_date])
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                self.logger.info(f"Removed {deleted_count} old metrics records")
                
        except Exception as e:
            self.logger.error(f"Erro na limpeza de dados antigos: {str(e)}")
    
    def export_metrics(self, start_time: datetime, end_time: datetime, 
                      format: str = "json") -> str:
        """Exporta métricas para análise externa"""
        try:
            metrics = self.get_search_history(
                limit=10000,
                filters={
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat()
                }
            )
            
            if format == "json":
                return json.dumps([asdict(m) for m in metrics], indent=2)
            elif format == "csv":
                # TODO: implementar export CSV
                pass
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Erro no export de métricas: {str(e)}")
            return ""
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna resumo geral das métricas"""
        try:
            realtime = self.get_realtime_metrics()
            aggregated_1h = self.get_aggregated_metrics("1h")
            aggregated_1d = self.get_aggregated_metrics("1d")
            top_queries = self.get_top_queries(5)
            
            return {
                'realtime': realtime,
                'last_hour': asdict(aggregated_1h),
                'last_day': asdict(aggregated_1d),
                'top_queries': top_queries,
                'system_health': {
                    'avg_latency_ok': aggregated_1h.avg_latency_ms < 2000,
                    'quality_ok': aggregated_1h.avg_context_relevance > 0.7,
                    'cache_efficiency_ok': aggregated_1h.cache_hit_rate > 0.3
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter resumo de métricas: {str(e)}")
            return {}