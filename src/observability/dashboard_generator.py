#!/usr/bin/env python3
"""
Dashboard Generator - Gerador de Dashboards de Monitoramento

Este módulo gera dashboards web interativos para visualização
de métricas, alertas e performance do sistema RAG.
Inclui gráficos em tempo real, tabelas de dados e relatórios.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import base64
from io import BytesIO

# Imports condicionais para visualização
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

@dataclass
class DashboardConfig:
    """Configuração do dashboard"""
    title: str = "RAG System Dashboard"
    refresh_interval: int = 30  # segundos
    theme: str = "light"  # light, dark
    show_alerts: bool = True
    show_metrics: bool = True
    show_performance: bool = True
    show_quality: bool = True
    chart_height: int = 400
    chart_width: int = 800
    time_range_hours: int = 24
    auto_refresh: bool = True

@dataclass
class ChartData:
    """Dados para gráfico"""
    title: str
    chart_type: str  # line, bar, pie, gauge, table
    data: List[Dict[str, Any]]
    x_axis: str
    y_axis: str
    description: str = ""
    unit: str = ""
    color_scheme: str = "viridis"

class DashboardGenerator:
    """Gerador de dashboards"""
    
    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()
        self.output_dir = Path("dashboards")
        self.output_dir.mkdir(exist_ok=True)
        
        # Templates HTML
        self.html_template = self._get_html_template()
        self.css_styles = self._get_css_styles()
        self.js_scripts = self._get_js_scripts()
        
        # Cache de dados
        self.cached_data: Dict[str, Any] = {}
        self.last_update: Optional[datetime] = None
    
    def generate_dashboard(self, 
                          metrics_data: Optional[Dict[str, Any]] = None,
                          alerts_data: Optional[List[Dict[str, Any]]] = None,
                          performance_data: Optional[Dict[str, Any]] = None,
                          quality_data: Optional[Dict[str, Any]] = None) -> str:
        """Gera dashboard completo"""
        
        # Coleta dados se não fornecidos
        if metrics_data is None:
            metrics_data = self._collect_metrics_data()
        if alerts_data is None:
            alerts_data = self._collect_alerts_data()
        if performance_data is None:
            performance_data = self._collect_performance_data()
        if quality_data is None:
            quality_data = self._collect_quality_data()
        
        # Gera seções do dashboard
        sections = []
        
        if self.config.show_alerts:
            sections.append(self._generate_alerts_section(alerts_data))
        
        if self.config.show_metrics:
            sections.append(self._generate_metrics_section(metrics_data))
        
        if self.config.show_performance:
            sections.append(self._generate_performance_section(performance_data))
        
        if self.config.show_quality:
            sections.append(self._generate_quality_section(quality_data))
        
        # Monta HTML final
        dashboard_html = self._assemble_dashboard(sections)
        
        # Salva dashboard
        output_file = self.output_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        # Cria link simbólico para latest
        latest_file = self.output_dir / "latest.html"
        if latest_file.exists():
            latest_file.unlink()
        
        try:
            latest_file.write_text(dashboard_html, encoding='utf-8')
        except Exception:
            pass
        
        self.last_update = datetime.now()
        return str(output_file)
    
    def _collect_metrics_data(self) -> Dict[str, Any]:
        """Coleta dados de métricas"""
        try:
            from .metrics_collector import metrics_collector
            return {
                'system_metrics': metrics_collector.get_system_metrics(),
                'search_metrics': metrics_collector.get_search_metrics(),
                'indexing_metrics': metrics_collector.get_indexing_metrics(),
                'api_metrics': metrics_collector.get_api_metrics()
            }
        except ImportError:
            return self._generate_mock_metrics_data()
    
    def _collect_alerts_data(self) -> List[Dict[str, Any]]:
        """Coleta dados de alertas"""
        try:
            from .alert_manager import alert_manager
            active_alerts = alert_manager.get_active_alerts()
            return [alert.to_dict() for alert in active_alerts]
        except ImportError:
            return self._generate_mock_alerts_data()
    
    def _collect_performance_data(self) -> Dict[str, Any]:
        """Coleta dados de performance"""
        try:
            from .performance_monitor import performance_monitor
            return {
                'current_stats': performance_monitor.get_current_stats(),
                'historical_stats': performance_monitor.get_historical_stats(hours=24)
            }
        except ImportError:
            return self._generate_mock_performance_data()
    
    def _collect_quality_data(self) -> Dict[str, Any]:
        """Coleta dados de qualidade"""
        try:
            from .quality_evaluator import quality_evaluator
            return {
                'recent_evaluations': quality_evaluator.get_recent_evaluations(hours=24),
                'quality_trends': quality_evaluator.get_quality_trends()
            }
        except ImportError:
            return self._generate_mock_quality_data()
    
    def _generate_alerts_section(self, alerts_data: List[Dict[str, Any]]) -> str:
        """Gera seção de alertas"""
        active_alerts = [alert for alert in alerts_data if alert.get('status') == 'active']
        
        # Contadores por severidade
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for alert in active_alerts:
            severity = alert.get('severity', 'low')
            severity_counts[severity] += 1
        
        # Gera HTML da seção
        alerts_html = f"""
        <div class="dashboard-section">
            <h2>🚨 Alertas Ativos ({len(active_alerts)})</h2>
            
            <div class="alerts-summary">
                <div class="alert-counter critical">
                    <span class="count">{severity_counts['critical']}</span>
                    <span class="label">Críticos</span>
                </div>
                <div class="alert-counter high">
                    <span class="count">{severity_counts['high']}</span>
                    <span class="label">Altos</span>
                </div>
                <div class="alert-counter medium">
                    <span class="count">{severity_counts['medium']}</span>
                    <span class="label">Médios</span>
                </div>
                <div class="alert-counter low">
                    <span class="count">{severity_counts['low']}</span>
                    <span class="label">Baixos</span>
                </div>
            </div>
            
            <div class="alerts-table">
                <table>
                    <thead>
                        <tr>
                            <th>Severidade</th>
                            <th>Título</th>
                            <th>Descrição</th>
                            <th>Criado</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for alert in active_alerts[:10]:  # Mostra apenas os 10 mais recentes
            created_at = alert.get('created_at', '')
            if created_at:
                try:
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_str = created_dt.strftime('%H:%M:%S')
                except:
                    created_str = created_at
            else:
                created_str = 'N/A'
            
            severity_class = alert.get('severity', 'low')
            alerts_html += f"""
                        <tr class="alert-row {severity_class}">
                            <td><span class="severity-badge {severity_class}">{alert.get('severity', 'N/A').upper()}</span></td>
                            <td>{alert.get('title', 'N/A')}</td>
                            <td>{alert.get('description', 'N/A')[:100]}...</td>
                            <td>{created_str}</td>
                            <td>
                                <button onclick="acknowledgeAlert('{alert.get('id', '')}')">Reconhecer</button>
                                <button onclick="suppressAlert('{alert.get('id', '')}')">Suprimir</button>
                            </td>
                        </tr>
            """
        
        alerts_html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return alerts_html
    
    def _generate_metrics_section(self, metrics_data: Dict[str, Any]) -> str:
        """Gera seção de métricas"""
        system_metrics = metrics_data.get('system_metrics', {})
        search_metrics = metrics_data.get('search_metrics', {})
        
        # Gera gráficos
        charts_html = ""
        
        # Gráfico de uso de recursos
        if PLOTLY_AVAILABLE:
            resource_chart = self._create_resource_usage_chart(system_metrics)
            charts_html += f'<div class="chart-container">{resource_chart}</div>'
        
        # Gráfico de métricas de busca
        if search_metrics and PLOTLY_AVAILABLE:
            search_chart = self._create_search_metrics_chart(search_metrics)
            charts_html += f'<div class="chart-container">{search_chart}</div>'
        
        metrics_html = f"""
        <div class="dashboard-section">
            <h2>📊 Métricas do Sistema</h2>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>CPU</h3>
                    <div class="metric-value">{system_metrics.get('cpu_percent', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <h3>Memória</h3>
                    <div class="metric-value">{system_metrics.get('memory_percent', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <h3>Disco</h3>
                    <div class="metric-value">{system_metrics.get('disk_percent', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <h3>Buscas/min</h3>
                    <div class="metric-value">{search_metrics.get('searches_per_minute', 0):.0f}</div>
                </div>
            </div>
            
            {charts_html}
        </div>
        """
        
        return metrics_html
    
    def _generate_performance_section(self, performance_data: Dict[str, Any]) -> str:
        """Gera seção de performance"""
        current_stats = performance_data.get('current_stats', {})
        
        # Gráfico de latência
        charts_html = ""
        if PLOTLY_AVAILABLE:
            latency_chart = self._create_latency_chart(performance_data)
            charts_html += f'<div class="chart-container">{latency_chart}</div>'
        
        performance_html = f"""
        <div class="dashboard-section">
            <h2>⚡ Performance</h2>
            
            <div class="performance-grid">
                <div class="perf-card">
                    <h3>Latência Média</h3>
                    <div class="perf-value">{current_stats.get('avg_latency', 0):.3f}s</div>
                </div>
                <div class="perf-card">
                    <h3>Throughput</h3>
                    <div class="perf-value">{current_stats.get('throughput', 0):.1f} req/s</div>
                </div>
                <div class="perf-card">
                    <h3>Taxa de Erro</h3>
                    <div class="perf-value">{current_stats.get('error_rate', 0):.2%}</div>
                </div>
                <div class="perf-card">
                    <h3>P95 Latência</h3>
                    <div class="perf-value">{current_stats.get('p95_latency', 0):.3f}s</div>
                </div>
            </div>
            
            {charts_html}
        </div>
        """
        
        return performance_html
    
    def _generate_quality_section(self, quality_data: Dict[str, Any]) -> str:
        """Gera seção de qualidade"""
        recent_evals = quality_data.get('recent_evaluations', [])
        
        # Calcula médias
        if recent_evals:
            avg_relevance = sum(e.get('context_relevance', 0) for e in recent_evals) / len(recent_evals)
            avg_faithfulness = sum(e.get('faithfulness', 0) for e in recent_evals) / len(recent_evals)
            avg_sas = sum(e.get('semantic_answer_similarity', 0) for e in recent_evals) / len(recent_evals)
        else:
            avg_relevance = avg_faithfulness = avg_sas = 0
        
        # Gráfico de qualidade
        charts_html = ""
        if PLOTLY_AVAILABLE and recent_evals:
            quality_chart = self._create_quality_chart(recent_evals)
            charts_html += f'<div class="chart-container">{quality_chart}</div>'
        
        quality_html = f"""
        <div class="dashboard-section">
            <h2>🎯 Qualidade RAG</h2>
            
            <div class="quality-grid">
                <div class="quality-card">
                    <h3>Relevância do Contexto</h3>
                    <div class="quality-value">{avg_relevance:.3f}</div>
                    <div class="quality-bar">
                        <div class="quality-fill" style="width: {avg_relevance*100}%"></div>
                    </div>
                </div>
                <div class="quality-card">
                    <h3>Fidelidade</h3>
                    <div class="quality-value">{avg_faithfulness:.3f}</div>
                    <div class="quality-bar">
                        <div class="quality-fill" style="width: {avg_faithfulness*100}%"></div>
                    </div>
                </div>
                <div class="quality-card">
                    <h3>Similaridade Semântica</h3>
                    <div class="quality-value">{avg_sas:.3f}</div>
                    <div class="quality-bar">
                        <div class="quality-fill" style="width: {avg_sas*100}%"></div>
                    </div>
                </div>
                <div class="quality-card">
                    <h3>Avaliações (24h)</h3>
                    <div class="quality-value">{len(recent_evals)}</div>
                </div>
            </div>
            
            {charts_html}
        </div>
        """
        
        return quality_html
    
    def _create_resource_usage_chart(self, system_metrics: Dict[str, Any]) -> str:
        """Cria gráfico de uso de recursos"""
        if not PLOTLY_AVAILABLE:
            return "<p>Plotly não disponível para gráficos</p>"
        
        fig = go.Figure()
        
        resources = ['CPU', 'Memória', 'Disco']
        values = [
            system_metrics.get('cpu_percent', 0),
            system_metrics.get('memory_percent', 0),
            system_metrics.get('disk_percent', 0)
        ]
        
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']
        
        fig.add_trace(go.Bar(
            x=resources,
            y=values,
            marker_color=colors,
            text=[f'{v:.1f}%' for v in values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Uso de Recursos do Sistema',
            yaxis_title='Porcentagem (%)',
            height=300,
            showlegend=False
        )
        
        return fig.to_html(include_plotlyjs='inline', div_id='resource-chart')
    
    def _create_search_metrics_chart(self, search_metrics: Dict[str, Any]) -> str:
        """Cria gráfico de métricas de busca"""
        if not PLOTLY_AVAILABLE:
            return "<p>Plotly não disponível para gráficos</p>"
        
        # Dados simulados de histórico
        times = [datetime.now() - timedelta(hours=i) for i in range(24, 0, -1)]
        searches = [search_metrics.get('searches_per_minute', 10) + (i % 5) for i in range(24)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=times,
            y=searches,
            mode='lines+markers',
            name='Buscas por Minuto',
            line=dict(color='#45b7d1', width=2)
        ))
        
        fig.update_layout(
            title='Histórico de Buscas (24h)',
            xaxis_title='Hora',
            yaxis_title='Buscas/min',
            height=300
        )
        
        return fig.to_html(include_plotlyjs='inline', div_id='search-chart')
    
    def _create_latency_chart(self, performance_data: Dict[str, Any]) -> str:
        """Cria gráfico de latência"""
        if not PLOTLY_AVAILABLE:
            return "<p>Plotly não disponível para gráficos</p>"
        
        current_stats = performance_data.get('current_stats', {})
        
        # Dados simulados
        times = [datetime.now() - timedelta(minutes=i*5) for i in range(12, 0, -1)]
        latencies = [current_stats.get('avg_latency', 0.5) + (i % 3) * 0.1 for i in range(12)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=times,
            y=latencies,
            mode='lines+markers',
            name='Latência Média',
            line=dict(color='#ff6b6b', width=2)
        ))
        
        fig.update_layout(
            title='Latência ao Longo do Tempo',
            xaxis_title='Hora',
            yaxis_title='Latência (s)',
            height=300
        )
        
        return fig.to_html(include_plotlyjs='inline', div_id='latency-chart')
    
    def _create_quality_chart(self, evaluations: List[Dict[str, Any]]) -> str:
        """Cria gráfico de qualidade"""
        if not PLOTLY_AVAILABLE:
            return "<p>Plotly não disponível para gráficos</p>"
        
        # Agrupa por hora
        hourly_data = {}
        for eval_data in evaluations:
            timestamp = eval_data.get('timestamp', datetime.now().isoformat())
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour_key = dt.replace(minute=0, second=0, microsecond=0)
                
                if hour_key not in hourly_data:
                    hourly_data[hour_key] = {'relevance': [], 'faithfulness': [], 'sas': []}
                
                hourly_data[hour_key]['relevance'].append(eval_data.get('context_relevance', 0))
                hourly_data[hour_key]['faithfulness'].append(eval_data.get('faithfulness', 0))
                hourly_data[hour_key]['sas'].append(eval_data.get('semantic_answer_similarity', 0))
            except:
                continue
        
        if not hourly_data:
            return "<p>Sem dados de qualidade disponíveis</p>"
        
        # Calcula médias por hora
        hours = sorted(hourly_data.keys())
        relevance_avg = [sum(hourly_data[h]['relevance']) / len(hourly_data[h]['relevance']) for h in hours]
        faithfulness_avg = [sum(hourly_data[h]['faithfulness']) / len(hourly_data[h]['faithfulness']) for h in hours]
        sas_avg = [sum(hourly_data[h]['sas']) / len(hourly_data[h]['sas']) for h in hours]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hours, y=relevance_avg,
            mode='lines+markers', name='Relevância',
            line=dict(color='#4ecdc4', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=hours, y=faithfulness_avg,
            mode='lines+markers', name='Fidelidade',
            line=dict(color='#45b7d1', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=hours, y=sas_avg,
            mode='lines+markers', name='SAS',
            line=dict(color='#96ceb4', width=2)
        ))
        
        fig.update_layout(
            title='Métricas de Qualidade ao Longo do Tempo',
            xaxis_title='Hora',
            yaxis_title='Score',
            height=400,
            yaxis=dict(range=[0, 1])
        )
        
        return fig.to_html(include_plotlyjs='inline', div_id='quality-chart')
    
    def _assemble_dashboard(self, sections: List[str]) -> str:
        """Monta HTML final do dashboard"""
        sections_html = '\n'.join(sections)
        
        dashboard_html = self.html_template.format(
            title=self.config.title,
            css_styles=self.css_styles,
            js_scripts=self.js_scripts,
            sections=sections_html,
            refresh_interval=self.config.refresh_interval * 1000,  # Convert to ms
            last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return dashboard_html
    
    def _get_html_template(self) -> str:
        """Template HTML base"""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css_styles}</style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <header class="dashboard-header">
        <h1>{title}</h1>
        <div class="header-info">
            <span class="last-update">Última atualização: {last_update}</span>
            <button id="refresh-btn" onclick="refreshDashboard()">🔄 Atualizar</button>
        </div>
    </header>
    
    <main class="dashboard-main">
        {sections}
    </main>
    
    <script>{js_scripts}</script>
</body>
</html>
        """
    
    def _get_css_styles(self) -> str:
        """Estilos CSS"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .dashboard-header h1 {
            font-size: 1.8rem;
            font-weight: 300;
        }
        
        .header-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .last-update {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        #refresh-btn {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        #refresh-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .dashboard-main {
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .dashboard-section {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid #e1e8ed;
        }
        
        .dashboard-section h2 {
            margin-bottom: 1.5rem;
            color: #2c3e50;
            font-weight: 500;
        }
        
        /* Alertas */
        .alerts-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .alert-counter {
            text-align: center;
            padding: 1rem;
            border-radius: 8px;
            color: white;
        }
        
        .alert-counter.critical { background: #e74c3c; }
        .alert-counter.high { background: #f39c12; }
        .alert-counter.medium { background: #f1c40f; color: #333; }
        .alert-counter.low { background: #27ae60; }
        
        .alert-counter .count {
            display: block;
            font-size: 2rem;
            font-weight: bold;
        }
        
        .alert-counter .label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .alerts-table {
            overflow-x: auto;
        }
        
        .alerts-table table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .alerts-table th,
        .alerts-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e1e8ed;
        }
        
        .alerts-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .severity-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            color: white;
        }
        
        .severity-badge.critical { background: #e74c3c; }
        .severity-badge.high { background: #f39c12; }
        .severity-badge.medium { background: #f1c40f; color: #333; }
        .severity-badge.low { background: #27ae60; }
        
        /* Métricas */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric-card h3 {
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            opacity: 0.9;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
        }
        
        /* Performance */
        .performance-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .perf-card {
            background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .perf-card h3 {
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            opacity: 0.9;
        }
        
        .perf-value {
            font-size: 2rem;
            font-weight: bold;
        }
        
        /* Qualidade */
        .quality-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .quality-card {
            background: white;
            border: 2px solid #e1e8ed;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .quality-card h3 {
            font-size: 0.9rem;
            margin-bottom: 1rem;
            color: #2c3e50;
        }
        
        .quality-value {
            font-size: 2rem;
            font-weight: bold;
            color: #27ae60;
            margin-bottom: 1rem;
        }
        
        .quality-bar {
            width: 100%;
            height: 8px;
            background: #e1e8ed;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .quality-fill {
            height: 100%;
            background: linear-gradient(90deg, #27ae60, #2ecc71);
            transition: width 0.3s ease;
        }
        
        /* Gráficos */
        .chart-container {
            margin: 2rem 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Responsivo */
        @media (max-width: 768px) {
            .dashboard-header {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
            
            .dashboard-main {
                padding: 1rem;
            }
            
            .metrics-grid,
            .performance-grid,
            .quality-grid {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def _get_js_scripts(self) -> str:
        """Scripts JavaScript"""
        return f"""
        // Auto refresh
        let autoRefreshInterval;
        
        function startAutoRefresh() {{
            if ({str(self.config.auto_refresh).lower()}) {{
                autoRefreshInterval = setInterval(refreshDashboard, {self.config.refresh_interval * 1000});
            }}
        }}
        
        function stopAutoRefresh() {{
            if (autoRefreshInterval) {{
                clearInterval(autoRefreshInterval);
            }}
        }}
        
        function refreshDashboard() {{
            location.reload();
        }}
        
        function acknowledgeAlert(alertId) {{
            console.log('Acknowledging alert:', alertId);
            // Implementar chamada para API
        }}
        
        function suppressAlert(alertId) {{
            console.log('Suppressing alert:', alertId);
            // Implementar chamada para API
        }}
        
        // Inicia auto refresh quando página carrega
        document.addEventListener('DOMContentLoaded', function() {{
            startAutoRefresh();
        }});
        
        // Para auto refresh quando página é fechada
        window.addEventListener('beforeunload', function() {{
            stopAutoRefresh();
        }});
        """
    
    def _generate_mock_metrics_data(self) -> Dict[str, Any]:
        """Gera dados mock para métricas"""
        import random
        return {
            'system_metrics': {
                'cpu_percent': random.uniform(20, 80),
                'memory_percent': random.uniform(30, 70),
                'disk_percent': random.uniform(10, 50)
            },
            'search_metrics': {
                'searches_per_minute': random.randint(5, 25)
            }
        }
    
    def _generate_mock_alerts_data(self) -> List[Dict[str, Any]]:
        """Gera dados mock para alertas"""
        return [
            {
                'id': 'alert_001',
                'title': 'Alta latência de busca',
                'description': 'Latência acima de 2 segundos detectada',
                'severity': 'high',
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
        ]
    
    def _generate_mock_performance_data(self) -> Dict[str, Any]:
        """Gera dados mock para performance"""
        import random
        return {
            'current_stats': {
                'avg_latency': random.uniform(0.1, 2.0),
                'throughput': random.uniform(10, 100),
                'error_rate': random.uniform(0, 0.05),
                'p95_latency': random.uniform(0.5, 3.0)
            }
        }
    
    def _generate_mock_quality_data(self) -> Dict[str, Any]:
        """Gera dados mock para qualidade"""
        import random
        evaluations = []
        for i in range(10):
            evaluations.append({
                'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                'context_relevance': random.uniform(0.7, 1.0),
                'faithfulness': random.uniform(0.8, 1.0),
                'semantic_answer_similarity': random.uniform(0.6, 0.9)
            })
        
        return {
            'recent_evaluations': evaluations
        }
    
    def generate_static_report(self, output_file: str = None) -> str:
        """Gera relatório estático em HTML"""
        if output_file is None:
            output_file = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Coleta todos os dados
        metrics_data = self._collect_metrics_data()
        alerts_data = self._collect_alerts_data()
        performance_data = self._collect_performance_data()
        quality_data = self._collect_quality_data()
        
        # Gera relatório
        report_html = self._generate_static_report_html(
            metrics_data, alerts_data, performance_data, quality_data
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        return str(output_file)
    
    def _generate_static_report_html(self, metrics_data, alerts_data, 
                                   performance_data, quality_data) -> str:
        """Gera HTML do relatório estático"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório RAG System - {timestamp}</title>
    <style>{self.css_styles}</style>
</head>
<body>
    <header class="dashboard-header">
        <h1>📊 Relatório RAG System</h1>
        <div class="header-info">
            <span class="last-update">Gerado em: {timestamp}</span>
        </div>
    </header>
    
    <main class="dashboard-main">
        <div class="dashboard-section">
            <h2>📋 Resumo Executivo</h2>
            <p>Este relatório apresenta o status atual do sistema RAG, incluindo métricas de performance, qualidade e alertas ativos.</p>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Alertas Ativos</h3>
                    <div class="metric-value">{len([a for a in alerts_data if a.get('status') == 'active'])}</div>
                </div>
                <div class="metric-card">
                    <h3>CPU Médio</h3>
                    <div class="metric-value">{metrics_data.get('system_metrics', {}).get('cpu_percent', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <h3>Latência Média</h3>
                    <div class="metric-value">{performance_data.get('current_stats', {}).get('avg_latency', 0):.3f}s</div>
                </div>
                <div class="metric-card">
                    <h3>Qualidade Média</h3>
                    <div class="metric-value">{sum(e.get('context_relevance', 0) for e in quality_data.get('recent_evaluations', [])) / max(len(quality_data.get('recent_evaluations', [])), 1):.3f}</div>
                </div>
            </div>
        </div>
        
        {self._generate_alerts_section(alerts_data)}
        {self._generate_metrics_section(metrics_data)}
        {self._generate_performance_section(performance_data)}
        {self._generate_quality_section(quality_data)}
    </main>
</body>
</html>
        """

# Instância global do dashboard generator
dashboard_generator = DashboardGenerator()

# Funções de conveniência
def generate_dashboard(config: Optional[DashboardConfig] = None) -> str:
    """Gera dashboard com configuração opcional"""
    if config:
        generator = DashboardGenerator(config)
        return generator.generate_dashboard()
    return dashboard_generator.generate_dashboard()

def generate_report() -> str:
    """Gera relatório estático"""
    return dashboard_generator.generate_static_report()