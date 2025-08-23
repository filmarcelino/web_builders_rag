import json
import hashlib
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import threading

from config.config import RAGConfig

@dataclass
class CacheEntry:
    """Entrada do cache de busca"""
    key: str
    data: Dict[str, Any]
    created_at: float
    last_accessed: float
    access_count: int
    ttl: float  # Time to live em segundos
    size_bytes: int

@dataclass
class CacheStats:
    """Estatísticas do cache"""
    total_entries: int
    total_size_bytes: int
    hit_count: int
    miss_count: int
    eviction_count: int
    hit_rate: float
    avg_access_time: float
    oldest_entry: Optional[str]
    newest_entry: Optional[str]

class SearchCache:
    """Cache inteligente para resultados de busca"""
    
    def __init__(self, cache_dir: str = None, max_size_mb: int = 100, default_ttl: int = 3600):
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.cache_dir = Path(cache_dir or RAGConfig.INDEX_DIR) / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_size_bytes = max_size_mb * 1024 * 1024  # Converte MB para bytes
        self.default_ttl = default_ttl  # TTL padrão em segundos
        self.cleanup_interval = 300  # Limpeza a cada 5 minutos
        
        # Cache em memória
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        
        # Estatísticas
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_access_time': 0,
            'access_count': 0
        }
        
        # Configurações de TTL por tipo de busca
        self.ttl_by_type = {
            'vector': 3600,    # 1 hora
            'text': 1800,      # 30 minutos
            'hybrid': 2400     # 40 minutos
        }
        
        # Arquivo de persistência
        self.cache_file = self.cache_dir / "search_cache.pkl"
        
        # Carrega cache persistido
        self._load_cache()
        
        # Inicia thread de limpeza
        self._start_cleanup_thread()
        
        self.logger.info(f"SearchCache inicializado: max_size={max_size_mb}MB, ttl={default_ttl}s")
    
    def _generate_cache_key(self, query: str, filters: Optional[Dict[str, Any]], 
                           top_k: int, search_type: str) -> str:
        """Gera chave única para cache"""
        # Normaliza query
        normalized_query = query.lower().strip()
        
        # Serializa filtros de forma consistente
        filters_str = json.dumps(filters or {}, sort_keys=True)
        
        # Cria string para hash
        cache_string = f"{normalized_query}|{filters_str}|{top_k}|{search_type}"
        
        # Gera hash SHA-256
        return hashlib.sha256(cache_string.encode('utf-8')).hexdigest()[:16]
    
    def get(self, query: str, filters: Optional[Dict[str, Any]], 
            top_k: int, search_type: str) -> Optional[Dict[str, Any]]:
        """Recupera resultado do cache"""
        start_time = time.time()
        
        try:
            cache_key = self._generate_cache_key(query, filters, top_k, search_type)
            
            with self._lock:
                entry = self._cache.get(cache_key)
                
                if entry is None:
                    self._stats['misses'] += 1
                    return None
                
                # Verifica se expirou
                current_time = time.time()
                if current_time - entry.created_at > entry.ttl:
                    # Remove entrada expirada
                    del self._cache[cache_key]
                    self._stats['misses'] += 1
                    self.logger.debug(f"Cache expirado removido: {cache_key}")
                    return None
                
                # Atualiza estatísticas de acesso
                entry.last_accessed = current_time
                entry.access_count += 1
                
                self._stats['hits'] += 1
                
                access_time = time.time() - start_time
                self._stats['total_access_time'] += access_time
                self._stats['access_count'] += 1
                
                self.logger.debug(f"Cache hit: {cache_key} (acessado {entry.access_count} vezes)")
                
                return entry.data.copy()  # Retorna cópia para evitar modificações
        
        except Exception as e:
            self.logger.error(f"Erro ao acessar cache: {str(e)}")
            self._stats['misses'] += 1
            return None
    
    def set(self, query: str, filters: Optional[Dict[str, Any]], 
            top_k: int, search_type: str, data: Dict[str, Any], 
            custom_ttl: Optional[int] = None) -> bool:
        """Armazena resultado no cache"""
        try:
            cache_key = self._generate_cache_key(query, filters, top_k, search_type)
            
            # Calcula TTL
            ttl = custom_ttl or self.ttl_by_type.get(search_type, self.default_ttl)
            
            # Serializa dados para calcular tamanho
            serialized_data = pickle.dumps(data)
            data_size = len(serialized_data)
            
            # Verifica se cabe no cache
            if data_size > self.max_size_bytes // 10:  # Máximo 10% do cache para uma entrada
                self.logger.warning(f"Dados muito grandes para cache: {data_size} bytes")
                return False
            
            current_time = time.time()
            
            with self._lock:
                # Remove entrada existente se houver
                if cache_key in self._cache:
                    del self._cache[cache_key]
                
                # Cria nova entrada
                entry = CacheEntry(
                    key=cache_key,
                    data=data,
                    created_at=current_time,
                    last_accessed=current_time,
                    access_count=0,
                    ttl=ttl,
                    size_bytes=data_size
                )
                
                # Verifica se precisa fazer eviction
                self._ensure_cache_size(data_size)
                
                # Adiciona ao cache
                self._cache[cache_key] = entry
                
                self.logger.debug(f"Cache set: {cache_key} (TTL: {ttl}s, Size: {data_size} bytes)")
                
                return True
        
        except Exception as e:
            self.logger.error(f"Erro ao armazenar no cache: {str(e)}")
            return False
    
    def _ensure_cache_size(self, new_entry_size: int):
        """Garante que há espaço suficiente no cache"""
        current_size = sum(entry.size_bytes for entry in self._cache.values())
        
        # Se adicionar a nova entrada exceder o limite, remove entradas antigas
        while current_size + new_entry_size > self.max_size_bytes and self._cache:
            # Encontra entrada para remoção (LRU com peso por tamanho)
            victim_key = self._find_eviction_victim()
            
            if victim_key:
                victim_entry = self._cache[victim_key]
                current_size -= victim_entry.size_bytes
                del self._cache[victim_key]
                
                self._stats['evictions'] += 1
                self.logger.debug(f"Cache eviction: {victim_key} ({victim_entry.size_bytes} bytes)")
            else:
                break
    
    def _find_eviction_victim(self) -> Optional[str]:
        """Encontra entrada para remoção usando algoritmo LRU modificado"""
        if not self._cache:
            return None
        
        current_time = time.time()
        best_score = float('inf')
        victim_key = None
        
        for key, entry in self._cache.items():
            # Score baseado em: tempo desde último acesso, frequência de acesso e tamanho
            time_since_access = current_time - entry.last_accessed
            access_frequency = entry.access_count / max(1, (current_time - entry.created_at) / 3600)  # acessos por hora
            size_penalty = entry.size_bytes / (1024 * 1024)  # MB
            
            # Score menor = melhor candidato para remoção
            score = access_frequency - (time_since_access / 3600) - size_penalty
            
            if score < best_score:
                best_score = score
                victim_key = key
        
        return victim_key
    
    def _cleanup_expired(self):
        """Remove entradas expiradas"""
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, entry in self._cache.items():
                if current_time - entry.created_at > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
        
        if expired_keys:
            self.logger.debug(f"Removidas {len(expired_keys)} entradas expiradas do cache")
    
    def _start_cleanup_thread(self):
        """Inicia thread de limpeza automática"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(self.cleanup_interval)
                    self._cleanup_expired()
                    
                    # Persiste cache a cada limpeza
                    self._save_cache()
                    
                except Exception as e:
                    self.logger.error(f"Erro na limpeza do cache: {str(e)}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        
        self.logger.debug("Thread de limpeza do cache iniciada")
    
    def _save_cache(self):
        """Persiste cache no disco"""
        try:
            with self._lock:
                # Salva apenas entradas não expiradas
                current_time = time.time()
                valid_entries = {
                    key: entry for key, entry in self._cache.items()
                    if current_time - entry.created_at <= entry.ttl
                }
                
                cache_data = {
                    'entries': valid_entries,
                    'stats': self._stats,
                    'saved_at': current_time
                }
                
                with open(self.cache_file, 'wb') as f:
                    pickle.dump(cache_data, f)
                
                self.logger.debug(f"Cache persistido: {len(valid_entries)} entradas")
        
        except Exception as e:
            self.logger.error(f"Erro ao salvar cache: {str(e)}")
    
    def _load_cache(self):
        """Carrega cache do disco"""
        try:
            if not self.cache_file.exists():
                return
            
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Verifica se o cache não é muito antigo (máximo 24 horas)
            saved_at = cache_data.get('saved_at', 0)
            if time.time() - saved_at > 24 * 3600:
                self.logger.info("Cache muito antigo, ignorando")
                return
            
            # Carrega entradas válidas
            current_time = time.time()
            loaded_entries = cache_data.get('entries', {})
            
            valid_count = 0
            for key, entry in loaded_entries.items():
                if current_time - entry.created_at <= entry.ttl:
                    self._cache[key] = entry
                    valid_count += 1
            
            # Carrega estatísticas
            if 'stats' in cache_data:
                self._stats.update(cache_data['stats'])
            
            self.logger.info(f"Cache carregado: {valid_count} entradas válidas")
        
        except Exception as e:
            self.logger.warning(f"Erro ao carregar cache: {str(e)}")
    
    def invalidate_by_pattern(self, pattern: str):
        """Invalida entradas do cache que correspondem a um padrão"""
        try:
            with self._lock:
                keys_to_remove = []
                
                for key, entry in self._cache.items():
                    # Verifica se a query original contém o padrão
                    query_info = entry.data.get('query_info', {})
                    original_query = query_info.get('original_query', '')
                    
                    if pattern.lower() in original_query.lower():
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self._cache[key]
                
                if keys_to_remove:
                    self.logger.info(f"Invalidadas {len(keys_to_remove)} entradas do cache (padrão: {pattern})")
        
        except Exception as e:
            self.logger.error(f"Erro ao invalidar cache por padrão: {str(e)}")
    
    def invalidate_by_source(self, source_url: str):
        """Invalida entradas do cache relacionadas a uma fonte específica"""
        try:
            with self._lock:
                keys_to_remove = []
                
                for key, entry in self._cache.items():
                    # Verifica se algum resultado vem da fonte especificada
                    results = entry.data.get('results', [])
                    
                    for result in results:
                        fonte = result.get('fonte', {})
                        if fonte.get('url') == source_url:
                            keys_to_remove.append(key)
                            break
                
                for key in keys_to_remove:
                    del self._cache[key]
                
                if keys_to_remove:
                    self.logger.info(f"Invalidadas {len(keys_to_remove)} entradas do cache (fonte: {source_url})")
        
        except Exception as e:
            self.logger.error(f"Erro ao invalidar cache por fonte: {str(e)}")
    
    def get_cache_stats(self) -> CacheStats:
        """Retorna estatísticas do cache"""
        try:
            with self._lock:
                total_entries = len(self._cache)
                total_size = sum(entry.size_bytes for entry in self._cache.values())
                
                hit_count = self._stats['hits']
                miss_count = self._stats['misses']
                total_requests = hit_count + miss_count
                hit_rate = hit_count / total_requests if total_requests > 0 else 0
                
                avg_access_time = (
                    self._stats['total_access_time'] / self._stats['access_count']
                    if self._stats['access_count'] > 0 else 0
                )
                
                # Encontra entradas mais antiga e mais nova
                oldest_entry = None
                newest_entry = None
                
                if self._cache:
                    oldest_time = float('inf')
                    newest_time = 0
                    
                    for key, entry in self._cache.items():
                        if entry.created_at < oldest_time:
                            oldest_time = entry.created_at
                            oldest_entry = key
                        
                        if entry.created_at > newest_time:
                            newest_time = entry.created_at
                            newest_entry = key
                
                return CacheStats(
                    total_entries=total_entries,
                    total_size_bytes=total_size,
                    hit_count=hit_count,
                    miss_count=miss_count,
                    eviction_count=self._stats['evictions'],
                    hit_rate=hit_rate,
                    avg_access_time=avg_access_time,
                    oldest_entry=oldest_entry,
                    newest_entry=newest_entry
                )
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular estatísticas do cache: {str(e)}")
            return CacheStats(
                total_entries=0, total_size_bytes=0, hit_count=0,
                miss_count=0, eviction_count=0, hit_rate=0,
                avg_access_time=0, oldest_entry=None, newest_entry=None
            )
    
    def get_top_queries(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Retorna queries mais acessadas"""
        try:
            with self._lock:
                query_counts = {}
                
                for entry in self._cache.values():
                    query_info = entry.data.get('query_info', {})
                    original_query = query_info.get('original_query', '')
                    
                    if original_query:
                        query_counts[original_query] = (
                            query_counts.get(original_query, 0) + entry.access_count
                        )
                
                # Ordena por contagem
                sorted_queries = sorted(
                    query_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                return sorted_queries[:limit]
        
        except Exception as e:
            self.logger.error(f"Erro ao obter top queries: {str(e)}")
            return []
    
    def clear(self):
        """Limpa todo o cache"""
        try:
            with self._lock:
                self._cache.clear()
                self._stats = {
                    'hits': 0,
                    'misses': 0,
                    'evictions': 0,
                    'total_access_time': 0,
                    'access_count': 0
                }
            
            # Remove arquivo de cache
            if self.cache_file.exists():
                self.cache_file.unlink()
            
            self.logger.info("Cache limpo")
        
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {str(e)}")
    
    def close(self):
        """Fecha cache e salva estado"""
        try:
            self._save_cache()
            self.logger.info("SearchCache fechado")
        
        except Exception as e:
            self.logger.error(f"Erro ao fechar cache: {str(e)}")