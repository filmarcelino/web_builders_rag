#!/usr/bin/env python3
"""
Logging Manager - Sistema de Logs Estruturados

Este módulo gerencia logs estruturados para o sistema RAG,
incluindo diferentes níveis de log, formatação JSON,
rotação de arquivos e integração com sistemas de monitoramento.
"""

import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import traceback
from contextlib import contextmanager
import threading
from enum import Enum

class LogLevel(Enum):
    """Níveis de log customizados"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    AUDIT = "AUDIT"  # Para auditoria de operações
    PERFORMANCE = "PERFORMANCE"  # Para métricas de performance
    SECURITY = "SECURITY"  # Para eventos de segurança

@dataclass
class LogEntry:
    """Entrada de log estruturada"""
    timestamp: str
    level: str
    logger_name: str
    message: str
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    operation: Optional[str] = None
    duration: Optional[float] = None
    status: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class StructuredFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON"""
    
    def __init__(self, include_extra_fields: bool = True):
        super().__init__()
        self.include_extra_fields = include_extra_fields
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata record como JSON estruturado"""
        # Informações básicas
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger_name': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line_number': record.lineno,
            'thread_id': record.thread,
            'process_id': record.process
        }
        
        # Adiciona campos extras se disponíveis
        if self.include_extra_fields:
            extra_fields = [
                'user_id', 'session_id', 'request_id', 'operation',
                'duration', 'status', 'error_type', 'error_message',
                'metadata'
            ]
            
            for field in extra_fields:
                if hasattr(record, field):
                    log_entry[field] = getattr(record, field)
        
        # Adiciona stack trace se for erro
        if record.exc_info:
            log_entry['stack_trace'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)

class LoggingManager:
    """Gerenciador de logs estruturados"""
    
    def __init__(self, 
                 app_name: str = "rag_system",
                 log_dir: str = "logs",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 console_level: str = "INFO",
                 file_level: str = "DEBUG"):
        
        self.app_name = app_name
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.console_level = getattr(logging, console_level.upper())
        self.file_level = getattr(logging, file_level.upper())
        
        # Cria diretório de logs
        self.log_dir.mkdir(exist_ok=True)
        
        # Configuração de loggers
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers: Dict[str, logging.Handler] = {}
        
        # Context local para thread
        self._context = threading.local()
        
        # Setup inicial
        self._setup_root_logger()
        self._setup_specialized_loggers()
    
    def _setup_root_logger(self):
        """Configura logger principal"""
        root_logger = logging.getLogger(self.app_name)
        root_logger.setLevel(logging.DEBUG)
        
        # Remove handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level)
        console_formatter = StructuredFormatter(include_extra_fields=False)
        console_handler.setFormatter(console_formatter)
        
        # Handler para arquivo principal
        main_log_file = self.log_dir / f"{self.app_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.file_level)
        file_formatter = StructuredFormatter(include_extra_fields=True)
        file_handler.setFormatter(file_formatter)
        
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        self.loggers['root'] = root_logger
        self.handlers['console'] = console_handler
        self.handlers['main_file'] = file_handler
    
    def _setup_specialized_loggers(self):
        """Configura loggers especializados"""
        specialized_configs = {
            'audit': {
                'file': 'audit.log',
                'level': logging.INFO,
                'description': 'Logs de auditoria de operações'
            },
            'performance': {
                'file': 'performance.log',
                'level': logging.DEBUG,
                'description': 'Logs de métricas de performance'
            },
            'security': {
                'file': 'security.log',
                'level': logging.WARNING,
                'description': 'Logs de eventos de segurança'
            },
            'errors': {
                'file': 'errors.log',
                'level': logging.ERROR,
                'description': 'Logs de erros e exceções'
            },
            'api': {
                'file': 'api.log',
                'level': logging.INFO,
                'description': 'Logs de requisições API'
            },
            'search': {
                'file': 'search.log',
                'level': logging.DEBUG,
                'description': 'Logs de operações de busca'
            },
            'indexing': {
                'file': 'indexing.log',
                'level': logging.INFO,
                'description': 'Logs de indexação de documentos'
            }
        }
        
        for logger_name, config in specialized_configs.items():
            logger = logging.getLogger(f"{self.app_name}.{logger_name}")
            logger.setLevel(config['level'])
            
            # Handler específico para arquivo
            log_file = self.log_dir / config['file']
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            handler.setLevel(config['level'])
            handler.setFormatter(StructuredFormatter(include_extra_fields=True))
            
            logger.addHandler(handler)
            logger.propagate = False  # Não propaga para root logger
            
            self.loggers[logger_name] = logger
            self.handlers[f"{logger_name}_file"] = handler
    
    def get_logger(self, name: str = 'root') -> logging.Logger:
        """Obtém logger por nome"""
        if name in self.loggers:
            return self.loggers[name]
        
        # Cria logger customizado se não existir
        full_name = f"{self.app_name}.{name}" if name != 'root' else self.app_name
        logger = logging.getLogger(full_name)
        logger.setLevel(logging.DEBUG)
        
        # Adiciona handler do arquivo principal
        if 'main_file' in self.handlers:
            logger.addHandler(self.handlers['main_file'])
        
        self.loggers[name] = logger
        return logger
    
    def set_context(self, **kwargs):
        """Define contexto para logs da thread atual"""
        if not hasattr(self._context, 'data'):
            self._context.data = {}
        self._context.data.update(kwargs)
    
    def clear_context(self):
        """Limpa contexto da thread atual"""
        if hasattr(self._context, 'data'):
            self._context.data.clear()
    
    def get_context(self) -> Dict[str, Any]:
        """Obtém contexto da thread atual"""
        if hasattr(self._context, 'data'):
            return self._context.data.copy()
        return {}
    
    @contextmanager
    def log_context(self, **kwargs):
        """Context manager para logs com contexto temporário"""
        original_context = self.get_context()
        try:
            self.set_context(**kwargs)
            yield
        finally:
            self.clear_context()
            self.set_context(**original_context)
    
    def log(self, level: Union[str, LogLevel], message: str, 
           logger_name: str = 'root', **kwargs):
        """Log estruturado com contexto"""
        logger = self.get_logger(logger_name)
        
        # Converte level se necessário
        if isinstance(level, LogLevel):
            level = level.value
        
        # Adiciona contexto da thread
        context = self.get_context()
        kwargs.update(context)
        
        # Log com campos extras
        logger.log(getattr(logging, level.upper()), message, extra=kwargs)
    
    def debug(self, message: str, logger_name: str = 'root', **kwargs):
        """Log de debug"""
        self.log(LogLevel.DEBUG, message, logger_name, **kwargs)
    
    def info(self, message: str, logger_name: str = 'root', **kwargs):
        """Log de informação"""
        self.log(LogLevel.INFO, message, logger_name, **kwargs)
    
    def warning(self, message: str, logger_name: str = 'root', **kwargs):
        """Log de aviso"""
        self.log(LogLevel.WARNING, message, logger_name, **kwargs)
    
    def error(self, message: str, logger_name: str = 'root', 
             error: Optional[Exception] = None, **kwargs):
        """Log de erro"""
        if error:
            kwargs.update({
                'error_type': type(error).__name__,
                'error_message': str(error)
            })
        
        logger = self.get_logger(logger_name)
        logger.error(message, extra=kwargs, exc_info=error is not None)
    
    def critical(self, message: str, logger_name: str = 'root', 
                error: Optional[Exception] = None, **kwargs):
        """Log crítico"""
        if error:
            kwargs.update({
                'error_type': type(error).__name__,
                'error_message': str(error)
            })
        
        logger = self.get_logger(logger_name)
        logger.critical(message, extra=kwargs, exc_info=error is not None)
    
    def audit(self, message: str, operation: str, status: str = 'success', **kwargs):
        """Log de auditoria"""
        kwargs.update({
            'operation': operation,
            'status': status
        })
        self.log(LogLevel.AUDIT, message, 'audit', **kwargs)
    
    def performance(self, message: str, operation: str, duration: float, **kwargs):
        """Log de performance"""
        kwargs.update({
            'operation': operation,
            'duration': duration
        })
        self.log(LogLevel.PERFORMANCE, message, 'performance', **kwargs)
    
    def security(self, message: str, event_type: str, severity: str = 'medium', **kwargs):
        """Log de segurança"""
        kwargs.update({
            'event_type': event_type,
            'severity': severity
        })
        self.log(LogLevel.SECURITY, message, 'security', **kwargs)
    
    def api_request(self, method: str, endpoint: str, status_code: int, 
                   duration: float, user_id: Optional[str] = None, **kwargs):
        """Log de requisição API"""
        kwargs.update({
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration': duration,
            'user_id': user_id
        })
        
        level = LogLevel.INFO if status_code < 400 else LogLevel.ERROR
        message = f"{method} {endpoint} - {status_code} ({duration:.3f}s)"
        self.log(level, message, 'api', **kwargs)
    
    def search_operation(self, query: str, results_count: int, duration: float, 
                        search_type: str = 'hybrid', **kwargs):
        """Log de operação de busca"""
        kwargs.update({
            'query': query,
            'results_count': results_count,
            'duration': duration,
            'search_type': search_type
        })
        
        message = f"Search: '{query}' -> {results_count} results ({duration:.3f}s)"
        self.log(LogLevel.INFO, message, 'search', **kwargs)
    
    def indexing_operation(self, document_count: int, duration: float, 
                          source: str, status: str = 'success', **kwargs):
        """Log de operação de indexação"""
        kwargs.update({
            'document_count': document_count,
            'duration': duration,
            'source': source,
            'status': status
        })
        
        level = LogLevel.INFO if status == 'success' else LogLevel.ERROR
        message = f"Indexed {document_count} documents from {source} ({duration:.3f}s)"
        self.log(level, message, 'indexing', **kwargs)
    
    def get_log_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Obtém estatísticas dos logs"""
        stats = {
            'log_files': {},
            'total_size_mb': 0,
            'oldest_log': None,
            'newest_log': None
        }
        
        for log_file in self.log_dir.glob('*.log'):
            if log_file.is_file():
                stat = log_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                
                stats['log_files'][log_file.name] = {
                    'size_mb': round(size_mb, 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                
                stats['total_size_mb'] += size_mb
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats
    
    def cleanup_old_logs(self, days: int = 30):
        """Remove logs antigos"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        removed_files = []
        
        for log_file in self.log_dir.glob('*.log.*'):  # Arquivos rotacionados
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    removed_files.append(str(log_file))
                except Exception as e:
                    self.error(f"Erro ao remover log antigo: {log_file}", error=e)
        
        if removed_files:
            self.info(f"Removidos {len(removed_files)} arquivos de log antigos")
        
        return removed_files
    
    def export_logs(self, logger_name: str, hours: int = 24, 
                   output_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """Exporta logs para análise"""
        log_file = self.log_dir / f"{logger_name}.log"
        if not log_file.exists():
            return []
        
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        logs = []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        log_time = datetime.fromisoformat(log_entry['timestamp']).timestamp()
                        
                        if log_time >= cutoff_time:
                            logs.append(log_entry)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
                
                self.info(f"Logs exportados para {output_file}", 
                         metadata={'exported_count': len(logs)})
        
        except Exception as e:
            self.error(f"Erro ao exportar logs: {e}", error=e)
        
        return logs

# Instância global do logging manager
logging_manager = LoggingManager()

# Funções de conveniência
def get_logger(name: str = 'root') -> logging.Logger:
    """Obtém logger"""
    return logging_manager.get_logger(name)

def log_context(**kwargs):
    """Context manager para logs"""
    return logging_manager.log_context(**kwargs)

def set_log_context(**kwargs):
    """Define contexto de log"""
    logging_manager.set_context(**kwargs)

# Decorator para logging automático
def log_function_calls(logger_name: str = 'root', level: str = 'DEBUG'):
    """Decorator para log automático de chamadas de função"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            logging_manager.log(
                level, 
                f"Iniciando {func.__name__}",
                logger_name,
                operation=func.__name__,
                function_args=str(args)[:200],
                function_kwargs=str(kwargs)[:200]
            )
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                logging_manager.log(
                    level,
                    f"Concluído {func.__name__}",
                    logger_name,
                    operation=func.__name__,
                    duration=duration,
                    status='success'
                )
                
                return result
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                
                logging_manager.error(
                    f"Erro em {func.__name__}: {e}",
                    logger_name,
                    error=e,
                    operation=func.__name__,
                    duration=duration,
                    status='error'
                )
                raise
        
        return wrapper
    return decorator