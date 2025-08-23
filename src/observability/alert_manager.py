#!/usr/bin/env python3
"""
Alert Manager - Sistema de Alertas e Notificações

Este módulo gerencia alertas baseados em métricas e eventos do sistema RAG,
incluindo diferentes tipos de alertas, canais de notificação,
escalonamento e supressão de alertas duplicados.
"""

import asyncio
import json
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import threading
from collections import defaultdict, deque
import hashlib
import requests
from urllib.parse import urljoin

class AlertSeverity(Enum):
    """Níveis de severidade de alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Status de alertas"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"

class NotificationChannel(Enum):
    """Canais de notificação"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    LOG = "log"
    CONSOLE = "console"

@dataclass
class AlertRule:
    """Regra de alerta"""
    id: str
    name: str
    description: str
    metric: str
    condition: str  # e.g., "> 0.8", "< 0.5", "== 0"
    threshold: float
    severity: AlertSeverity
    duration: int = 300  # segundos para confirmar alerta
    cooldown: int = 3600  # segundos antes de reenviar
    enabled: bool = True
    channels: List[NotificationChannel] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, value: float) -> bool:
        """Avalia se a condição do alerta foi atendida"""
        if not self.enabled:
            return False
        
        try:
            if self.condition.startswith('>'):
                if self.condition.startswith('>='): 
                    return value >= self.threshold
                return value > self.threshold
            elif self.condition.startswith('<'):
                if self.condition.startswith('<='): 
                    return value <= self.threshold
                return value < self.threshold
            elif self.condition.startswith('=='):
                return abs(value - self.threshold) < 0.001
            elif self.condition.startswith('!='):
                return abs(value - self.threshold) >= 0.001
            else:
                return False
        except Exception:
            return False

@dataclass
class Alert:
    """Alerta ativo"""
    id: str
    rule_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    current_value: Optional[float] = None
    threshold: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    notifications_sent: int = 0
    last_notification: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        # Converte datetime para string
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, (AlertSeverity, AlertStatus)):
                data[key] = value.value
        return data

@dataclass
class NotificationConfig:
    """Configuração de canal de notificação"""
    channel: NotificationChannel
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Configurações específicas por canal
    # EMAIL: smtp_server, smtp_port, username, password, from_email, to_emails
    # WEBHOOK: url, headers, method
    # SLACK: webhook_url, channel, username
    # DISCORD: webhook_url

class MetricBuffer:
    """Buffer para métricas com janela deslizante"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.data: deque = deque(maxlen=max_size)
        self.lock = threading.Lock()
    
    def add(self, timestamp: datetime, value: float):
        """Adiciona valor ao buffer"""
        with self.lock:
            self.data.append((timestamp, value))
    
    def get_recent(self, seconds: int) -> List[tuple]:
        """Obtém valores recentes"""
        cutoff = datetime.now() - timedelta(seconds=seconds)
        with self.lock:
            return [(ts, val) for ts, val in self.data if ts >= cutoff]
    
    def get_average(self, seconds: int) -> Optional[float]:
        """Calcula média dos valores recentes"""
        recent = self.get_recent(seconds)
        if not recent:
            return None
        return sum(val for _, val in recent) / len(recent)
    
    def get_latest(self) -> Optional[tuple]:
        """Obtém último valor"""
        with self.lock:
            return self.data[-1] if self.data else None

class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_configs: Dict[NotificationChannel, NotificationConfig] = {}
        self.metric_buffers: Dict[str, MetricBuffer] = defaultdict(MetricBuffer)
        
        # Estado interno
        self.pending_alerts: Dict[str, datetime] = {}  # Alertas aguardando confirmação
        self.suppressed_alerts: Dict[str, datetime] = {}  # Alertas suprimidos
        self.alert_counts: Dict[str, int] = defaultdict(int)
        
        # Threading
        self.lock = threading.Lock()
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Carrega configuração se fornecida
        if config_file:
            self.load_config(config_file)
        
        # Configuração padrão
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configura regras padrão de alerta"""
        default_rules = [
            AlertRule(
                id="high_search_latency",
                name="Alta Latência de Busca",
                description="Latência de busca acima do limite aceitável",
                metric="search_latency_avg",
                condition=">",
                threshold=2.0,  # 2 segundos
                severity=AlertSeverity.HIGH,
                duration=300,
                channels=[NotificationChannel.LOG, NotificationChannel.CONSOLE]
            ),
            AlertRule(
                id="low_context_relevance",
                name="Baixa Relevância de Contexto",
                description="Relevância de contexto abaixo do mínimo",
                metric="context_relevance_avg",
                condition="<",
                threshold=0.7,
                severity=AlertSeverity.MEDIUM,
                duration=600,
                channels=[NotificationChannel.LOG]
            ),
            AlertRule(
                id="high_error_rate",
                name="Alta Taxa de Erro",
                description="Taxa de erro acima do limite",
                metric="error_rate",
                condition=">",
                threshold=0.05,  # 5%
                severity=AlertSeverity.CRITICAL,
                duration=180,
                channels=[NotificationChannel.LOG, NotificationChannel.CONSOLE]
            ),
            AlertRule(
                id="low_faithfulness",
                name="Baixa Fidelidade",
                description="Score de fidelidade abaixo do esperado",
                metric="faithfulness_avg",
                condition="<",
                threshold=0.8,
                severity=AlertSeverity.MEDIUM,
                duration=600,
                channels=[NotificationChannel.LOG]
            ),
            AlertRule(
                id="memory_usage_high",
                name="Alto Uso de Memória",
                description="Uso de memória acima de 85%",
                metric="memory_usage_percent",
                condition=">",
                threshold=85.0,
                severity=AlertSeverity.HIGH,
                duration=300,
                channels=[NotificationChannel.LOG, NotificationChannel.CONSOLE]
            ),
            AlertRule(
                id="cpu_usage_high",
                name="Alto Uso de CPU",
                description="Uso de CPU acima de 90%",
                metric="cpu_usage_percent",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.HIGH,
                duration=300,
                channels=[NotificationChannel.LOG, NotificationChannel.CONSOLE]
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
    
    def add_rule(self, rule: AlertRule):
        """Adiciona regra de alerta"""
        with self.lock:
            self.rules[rule.id] = rule
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove regra de alerta"""
        with self.lock:
            if rule_id in self.rules:
                del self.rules[rule_id]
                return True
            return False
    
    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Obtém regra por ID"""
        return self.rules.get(rule_id)
    
    def list_rules(self) -> List[AlertRule]:
        """Lista todas as regras"""
        return list(self.rules.values())
    
    def configure_notification(self, channel: NotificationChannel, config: Dict[str, Any]):
        """Configura canal de notificação"""
        self.notification_configs[channel] = NotificationConfig(
            channel=channel,
            enabled=config.get('enabled', True),
            config=config
        )
    
    def add_metric(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """Adiciona métrica para monitoramento"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.metric_buffers[metric_name].add(timestamp, value)
        
        # Verifica regras relacionadas a esta métrica
        self._check_metric_rules(metric_name, value, timestamp)
    
    def _check_metric_rules(self, metric_name: str, value: float, timestamp: datetime):
        """Verifica regras para uma métrica específica"""
        for rule in self.rules.values():
            if rule.metric == metric_name and rule.enabled:
                if rule.evaluate(value):
                    self._handle_rule_triggered(rule, value, timestamp)
                else:
                    self._handle_rule_resolved(rule, timestamp)
    
    def _handle_rule_triggered(self, rule: AlertRule, value: float, timestamp: datetime):
        """Lida com regra disparada"""
        rule_key = f"{rule.id}_{rule.metric}"
        
        # Verifica se já está em período de confirmação
        if rule_key in self.pending_alerts:
            # Verifica se passou o tempo de duração
            if (timestamp - self.pending_alerts[rule_key]).total_seconds() >= rule.duration:
                # Cria alerta
                alert = self._create_alert(rule, value, timestamp)
                self._activate_alert(alert)
                del self.pending_alerts[rule_key]
        else:
            # Inicia período de confirmação
            self.pending_alerts[rule_key] = timestamp
    
    def _handle_rule_resolved(self, rule: AlertRule, timestamp: datetime):
        """Lida com regra resolvida"""
        rule_key = f"{rule.id}_{rule.metric}"
        
        # Remove de pending se existir
        if rule_key in self.pending_alerts:
            del self.pending_alerts[rule_key]
        
        # Resolve alerta ativo se existir
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.rule_id == rule.id and alert.status == AlertStatus.ACTIVE:
                self._resolve_alert(alert_id, timestamp)
    
    def _create_alert(self, rule: AlertRule, value: float, timestamp: datetime) -> Alert:
        """Cria novo alerta"""
        alert_id = self._generate_alert_id(rule, timestamp)
        
        alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            title=rule.name,
            description=f"{rule.description}. Valor atual: {value:.3f}, Limite: {rule.threshold}",
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            created_at=timestamp,
            updated_at=timestamp,
            current_value=value,
            threshold=rule.threshold,
            metadata=rule.metadata.copy()
        )
        
        return alert
    
    def _generate_alert_id(self, rule: AlertRule, timestamp: datetime) -> str:
        """Gera ID único para alerta"""
        content = f"{rule.id}_{rule.metric}_{timestamp.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _activate_alert(self, alert: Alert):
        """Ativa alerta e envia notificações"""
        with self.lock:
            self.active_alerts[alert.id] = alert
            self.alert_history.append(alert)
            self.alert_counts[alert.rule_id] += 1
        
        # Envia notificações
        rule = self.rules.get(alert.rule_id)
        if rule:
            self._send_notifications(alert, rule)
    
    def _resolve_alert(self, alert_id: str, timestamp: datetime):
        """Resolve alerta"""
        with self.lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = timestamp
                alert.updated_at = timestamp
                
                # Remove dos alertas ativos
                del self.active_alerts[alert_id]
                
                # Envia notificação de resolução
                rule = self.rules.get(alert.rule_id)
                if rule:
                    self._send_resolution_notification(alert, rule)
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Reconhece alerta"""
        with self.lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = acknowledged_by
                alert.updated_at = datetime.now()
                return True
            return False
    
    def suppress_alert(self, alert_id: str, duration_minutes: int = 60) -> bool:
        """Suprime alerta por período"""
        with self.lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.SUPPRESSED
                alert.updated_at = datetime.now()
                
                # Agenda remoção da supressão
                suppress_until = datetime.now() + timedelta(minutes=duration_minutes)
                self.suppressed_alerts[alert_id] = suppress_until
                return True
            return False
    
    def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Envia notificações para canais configurados"""
        for channel in rule.channels:
            try:
                if channel == NotificationChannel.LOG:
                    self._send_log_notification(alert)
                elif channel == NotificationChannel.CONSOLE:
                    self._send_console_notification(alert)
                elif channel == NotificationChannel.EMAIL:
                    self._send_email_notification(alert)
                elif channel == NotificationChannel.WEBHOOK:
                    self._send_webhook_notification(alert)
                elif channel == NotificationChannel.SLACK:
                    self._send_slack_notification(alert)
                elif channel == NotificationChannel.DISCORD:
                    self._send_discord_notification(alert)
                
                alert.notifications_sent += 1
                alert.last_notification = datetime.now()
                
            except Exception as e:
                print(f"Erro ao enviar notificação via {channel.value}: {e}")
    
    def _send_log_notification(self, alert: Alert):
        """Envia notificação via log"""
        from .logging_manager import logging_manager
        
        level = 'ERROR' if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL] else 'WARNING'
        
        logging_manager.log(
            level,
            f"ALERTA: {alert.title}",
            'alerts',
            alert_id=alert.id,
            severity=alert.severity.value,
            description=alert.description,
            current_value=alert.current_value,
            threshold=alert.threshold
        )
    
    def _send_console_notification(self, alert: Alert):
        """Envia notificação via console"""
        severity_colors = {
            AlertSeverity.LOW: '\033[94m',      # Azul
            AlertSeverity.MEDIUM: '\033[93m',   # Amarelo
            AlertSeverity.HIGH: '\033[91m',     # Vermelho
            AlertSeverity.CRITICAL: '\033[95m'  # Magenta
        }
        
        color = severity_colors.get(alert.severity, '')
        reset = '\033[0m'
        
        print(f"{color}🚨 ALERTA [{alert.severity.value.upper()}]: {alert.title}{reset}")
        print(f"   {alert.description}")
        print(f"   ID: {alert.id} | Criado: {alert.created_at.strftime('%H:%M:%S')}")
        print()
    
    def _send_email_notification(self, alert: Alert):
        """Envia notificação via email"""
        config = self.notification_configs.get(NotificationChannel.EMAIL)
        if not config or not config.enabled:
            return
        
        smtp_config = config.config
        
        msg = MIMEMultipart()
        msg['From'] = smtp_config.get('from_email')
        msg['To'] = ', '.join(smtp_config.get('to_emails', []))
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
        
        body = f"""
        Alerta: {alert.title}
        Severidade: {alert.severity.value.upper()}
        Descrição: {alert.description}
        
        Detalhes:
        - ID do Alerta: {alert.id}
        - Valor Atual: {alert.current_value}
        - Limite: {alert.threshold}
        - Criado em: {alert.created_at}
        
        Sistema RAG - Monitoramento
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            if smtp_config.get('username'):
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
            
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
    
    def _send_webhook_notification(self, alert: Alert):
        """Envia notificação via webhook"""
        config = self.notification_configs.get(NotificationChannel.WEBHOOK)
        if not config or not config.enabled:
            return
        
        webhook_config = config.config
        payload = {
            'alert': alert.to_dict(),
            'timestamp': datetime.now().isoformat(),
            'source': 'rag_system'
        }
        
        try:
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=webhook_config.get('headers', {}),
                timeout=10
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Erro ao enviar webhook: {e}")
    
    def _send_slack_notification(self, alert: Alert):
        """Envia notificação via Slack"""
        config = self.notification_configs.get(NotificationChannel.SLACK)
        if not config or not config.enabled:
            return
        
        slack_config = config.config
        
        color_map = {
            AlertSeverity.LOW: '#36a64f',
            AlertSeverity.MEDIUM: '#ffcc00',
            AlertSeverity.HIGH: '#ff6600',
            AlertSeverity.CRITICAL: '#ff0000'
        }
        
        payload = {
            'channel': slack_config.get('channel', '#alerts'),
            'username': slack_config.get('username', 'RAG Monitor'),
            'attachments': [{
                'color': color_map.get(alert.severity, '#cccccc'),
                'title': f"🚨 {alert.title}",
                'text': alert.description,
                'fields': [
                    {'title': 'Severidade', 'value': alert.severity.value.upper(), 'short': True},
                    {'title': 'Valor Atual', 'value': str(alert.current_value), 'short': True},
                    {'title': 'Limite', 'value': str(alert.threshold), 'short': True},
                    {'title': 'ID', 'value': alert.id, 'short': True}
                ],
                'timestamp': int(alert.created_at.timestamp())
            }]
        }
        
        try:
            response = requests.post(slack_config['webhook_url'], json=payload, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Erro ao enviar Slack: {e}")
    
    def _send_discord_notification(self, alert: Alert):
        """Envia notificação via Discord"""
        config = self.notification_configs.get(NotificationChannel.DISCORD)
        if not config or not config.enabled:
            return
        
        discord_config = config.config
        
        color_map = {
            AlertSeverity.LOW: 0x36a64f,
            AlertSeverity.MEDIUM: 0xffcc00,
            AlertSeverity.HIGH: 0xff6600,
            AlertSeverity.CRITICAL: 0xff0000
        }
        
        payload = {
            'embeds': [{
                'title': f"🚨 {alert.title}",
                'description': alert.description,
                'color': color_map.get(alert.severity, 0xcccccc),
                'fields': [
                    {'name': 'Severidade', 'value': alert.severity.value.upper(), 'inline': True},
                    {'name': 'Valor Atual', 'value': str(alert.current_value), 'inline': True},
                    {'name': 'Limite', 'value': str(alert.threshold), 'inline': True},
                    {'name': 'ID', 'value': alert.id, 'inline': False}
                ],
                'timestamp': alert.created_at.isoformat()
            }]
        }
        
        try:
            response = requests.post(discord_config['webhook_url'], json=payload, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Erro ao enviar Discord: {e}")
    
    def _send_resolution_notification(self, alert: Alert, rule: AlertRule):
        """Envia notificação de resolução"""
        # Cria cópia do alerta para notificação de resolução
        resolution_alert = Alert(
            id=alert.id,
            rule_id=alert.rule_id,
            title=f"✅ RESOLVIDO: {alert.title}",
            description=f"O alerta foi resolvido. {alert.description}",
            severity=AlertSeverity.LOW,  # Resolução sempre é baixa severidade
            status=AlertStatus.RESOLVED,
            created_at=alert.created_at,
            updated_at=alert.updated_at,
            resolved_at=alert.resolved_at,
            current_value=alert.current_value,
            threshold=alert.threshold,
            metadata=alert.metadata
        )
        
        # Envia apenas para log e console por padrão
        self._send_log_notification(resolution_alert)
        if NotificationChannel.CONSOLE in rule.channels:
            self._send_console_notification(resolution_alert)
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtém alertas ativos"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Obtém histórico de alertas"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.created_at >= cutoff]
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de alertas"""
        active_count = len(self.active_alerts)
        total_count = len(self.alert_history)
        
        severity_counts = defaultdict(int)
        for alert in self.active_alerts.values():
            severity_counts[alert.severity.value] += 1
        
        rule_counts = dict(self.alert_counts)
        
        return {
            'active_alerts': active_count,
            'total_alerts_24h': len(self.get_alert_history(24)),
            'severity_distribution': dict(severity_counts),
            'alerts_by_rule': rule_counts,
            'rules_configured': len(self.rules),
            'notification_channels': len(self.notification_configs)
        }
    
    def start_monitoring(self):
        """Inicia monitoramento em background"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                # Remove supressões expiradas
                self._cleanup_suppressions()
                
                # Verifica alertas pendentes que expiraram
                self._cleanup_pending_alerts()
                
                # Aguarda próxima verificação
                time.sleep(30)  # Verifica a cada 30 segundos
                
            except Exception as e:
                print(f"Erro no loop de monitoramento: {e}")
                time.sleep(60)  # Aguarda mais tempo em caso de erro
    
    def _cleanup_suppressions(self):
        """Remove supressões expiradas"""
        now = datetime.now()
        expired = []
        
        for alert_id, suppress_until in self.suppressed_alerts.items():
            if now >= suppress_until:
                expired.append(alert_id)
        
        for alert_id in expired:
            del self.suppressed_alerts[alert_id]
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].status = AlertStatus.ACTIVE
    
    def _cleanup_pending_alerts(self):
        """Remove alertas pendentes expirados"""
        now = datetime.now()
        expired = []
        
        for rule_key, pending_since in self.pending_alerts.items():
            # Se passou muito tempo sem confirmação, remove
            if (now - pending_since).total_seconds() > 3600:  # 1 hora
                expired.append(rule_key)
        
        for rule_key in expired:
            del self.pending_alerts[rule_key]
    
    def load_config(self, config_file: str):
        """Carrega configuração de arquivo"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Carrega regras
            if 'rules' in config:
                for rule_data in config['rules']:
                    rule = AlertRule(**rule_data)
                    self.add_rule(rule)
            
            # Carrega configurações de notificação
            if 'notifications' in config:
                for channel_name, channel_config in config['notifications'].items():
                    try:
                        channel = NotificationChannel(channel_name)
                        self.configure_notification(channel, channel_config)
                    except ValueError:
                        print(f"Canal de notificação desconhecido: {channel_name}")
        
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
    
    def save_config(self, config_file: str):
        """Salva configuração em arquivo"""
        config = {
            'rules': [asdict(rule) for rule in self.rules.values()],
            'notifications': {
                channel.value: asdict(config) 
                for channel, config in self.notification_configs.items()
            }
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")

# Instância global do alert manager
alert_manager = AlertManager()

# Funções de conveniência
def add_metric(metric_name: str, value: float):
    """Adiciona métrica para monitoramento"""
    alert_manager.add_metric(metric_name, value)

def create_alert_rule(rule_id: str, name: str, metric: str, condition: str, 
                     threshold: float, severity: AlertSeverity) -> AlertRule:
    """Cria regra de alerta"""
    rule = AlertRule(
        id=rule_id,
        name=name,
        description=f"Alerta para {metric} {condition} {threshold}",
        metric=metric,
        condition=condition,
        threshold=threshold,
        severity=severity,
        channels=[NotificationChannel.LOG, NotificationChannel.CONSOLE]
    )
    alert_manager.add_rule(rule)
    return rule

def get_active_alerts() -> List[Alert]:
    """Obtém alertas ativos"""
    return alert_manager.get_active_alerts()

def get_alert_stats() -> Dict[str, Any]:
    """Obtém estatísticas de alertas"""
    return alert_manager.get_alert_stats()