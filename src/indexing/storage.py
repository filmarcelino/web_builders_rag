import json
import sqlite3
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging
import pickle
import gzip
import hashlib

from config.config import RAGConfig

@dataclass
class StorageStats:
    """Estatísticas de armazenamento"""
    total_chunks: int
    total_size_bytes: int
    database_size_bytes: int
    index_files_count: int
    last_updated: str
    oldest_content: Optional[str]
    newest_content: Optional[str]

class IndexStorage:
    """Gerenciador de armazenamento persistente para índices RAG"""
    
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Arquivos de armazenamento
        self.db_path = self.storage_dir / "rag_storage.db"
        self.metadata_path = self.storage_dir / "metadata.json"
        self.config_path = self.storage_dir / "storage_config.json"
        
        # Configuração de armazenamento
        self.storage_config = {
            'version': '1.0',
            'compression_enabled': True,
            'backup_retention_days': 30,
            'auto_vacuum': True,
            'chunk_size_limit': 50000,  # 50KB por chunk
            'metadata_cache_size': 1000
        }
        
        # Cache de metadados
        self._metadata_cache = {}
        self._cache_dirty = False
        
        # Inicializa armazenamento
        self._init_storage()
    
    def _init_storage(self):
        """Inicializa estruturas de armazenamento"""
        try:
            # Carrega configuração
            self._load_storage_config()
            
            # Inicializa banco de dados
            self._init_database()
            
            # Carrega cache de metadados
            self._load_metadata_cache()
            
            self.logger.info(f"Armazenamento inicializado em: {self.storage_dir}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar armazenamento: {str(e)}")
            raise
    
    def _load_storage_config(self):
        """Carrega configuração de armazenamento"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.storage_config.update(saved_config)
            else:
                # Salva configuração padrão
                self._save_storage_config()
        
        except Exception as e:
            self.logger.warning(f"Erro ao carregar configuração: {str(e)}")
    
    def _save_storage_config(self):
        """Salva configuração de armazenamento"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.storage_config, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {str(e)}")
    
    def _init_database(self):
        """Inicializa banco de dados SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                conn.execute('PRAGMA cache_size=10000')
                conn.execute('PRAGMA temp_store=MEMORY')
                
                if self.storage_config['auto_vacuum']:
                    conn.execute('PRAGMA auto_vacuum=INCREMENTAL')
                
                # Tabela principal de chunks
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS chunks (
                        chunk_id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        content_hash TEXT NOT NULL,
                        compressed_content BLOB,
                        metadata TEXT NOT NULL,
                        source_url TEXT NOT NULL,
                        source_title TEXT,
                        license TEXT,
                        stack TEXT,
                        category TEXT,
                        language TEXT DEFAULT 'pt',
                        maturity_level TEXT,
                        quality_score REAL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        size_bytes INTEGER,
                        embedding_model TEXT,
                        INDEX(source_url),
                        INDEX(stack),
                        INDEX(category),
                        INDEX(license),
                        INDEX(created_at),
                        INDEX(content_hash)
                    )
                ''')
                
                # Tabela de embeddings (separada para otimização)
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS embeddings (
                        chunk_id TEXT PRIMARY KEY,
                        embedding BLOB NOT NULL,
                        embedding_model TEXT NOT NULL,
                        embedding_dim INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (chunk_id) REFERENCES chunks (chunk_id) ON DELETE CASCADE
                    )
                ''')
                
                # Tabela de estatísticas
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS storage_stats (
                        stat_name TEXT PRIMARY KEY,
                        stat_value TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                # Tabela de logs de operações
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS operation_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation TEXT NOT NULL,
                        chunk_id TEXT,
                        source_url TEXT,
                        details TEXT,
                        timestamp TEXT NOT NULL,
                        INDEX(operation),
                        INDEX(timestamp),
                        INDEX(source_url)
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
            raise
    
    def _load_metadata_cache(self):
        """Carrega cache de metadados"""
        try:
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self._metadata_cache = json.load(f)
            
            # Limita tamanho do cache
            cache_size = self.storage_config['metadata_cache_size']
            if len(self._metadata_cache) > cache_size:
                # Remove entradas mais antigas
                sorted_items = sorted(
                    self._metadata_cache.items(),
                    key=lambda x: x[1].get('last_accessed', ''),
                    reverse=True
                )
                self._metadata_cache = dict(sorted_items[:cache_size])
                self._cache_dirty = True
        
        except Exception as e:
            self.logger.warning(f"Erro ao carregar cache de metadados: {str(e)}")
            self._metadata_cache = {}
    
    def _save_metadata_cache(self):
        """Salva cache de metadados"""
        if not self._cache_dirty:
            return
        
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self._metadata_cache, f, indent=2, ensure_ascii=False)
            
            self._cache_dirty = False
        
        except Exception as e:
            self.logger.error(f"Erro ao salvar cache de metadados: {str(e)}")
    
    def _compress_content(self, content: str) -> bytes:
        """Comprime conteúdo se habilitado"""
        if not self.storage_config['compression_enabled']:
            return None
        
        try:
            return gzip.compress(content.encode('utf-8'))
        except Exception as e:
            self.logger.warning(f"Erro na compressão: {str(e)}")
            return None
    
    def _decompress_content(self, compressed_data: bytes) -> str:
        """Descomprime conteúdo"""
        try:
            return gzip.decompress(compressed_data).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Erro na descompressão: {str(e)}")
            return ""
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calcula hash do conteúdo para detecção de duplicatas"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def store_chunk(self, chunk_id: str, content: str, metadata: Dict[str, Any], 
                   embedding: Optional[List[float]] = None) -> bool:
        """Armazena um chunk com metadados e embedding opcional"""
        try:
            # Validações
            if len(content) > self.storage_config['chunk_size_limit']:
                self.logger.warning(f"Chunk {chunk_id} excede limite de tamanho")
                return False
            
            content_hash = self._calculate_content_hash(content)
            compressed_content = self._compress_content(content)
            
            # Extrai metadados principais
            source_url = metadata.get('source_url', '')
            source_title = metadata.get('source_title', '')
            license_info = metadata.get('license', '')
            stack = metadata.get('stack', '')
            category = metadata.get('category', '')
            language = metadata.get('language', 'pt')
            maturity_level = metadata.get('maturity_level', '')
            quality_score = metadata.get('quality_score', 0.0)
            
            current_time = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Verifica se chunk já existe
                cursor = conn.execute(
                    'SELECT content_hash FROM chunks WHERE chunk_id = ?',
                    (chunk_id,)
                )
                existing = cursor.fetchone()
                
                if existing and existing[0] == content_hash:
                    # Conteúdo idêntico, apenas atualiza timestamp
                    conn.execute(
                        'UPDATE chunks SET updated_at = ? WHERE chunk_id = ?',
                        (current_time, chunk_id)
                    )
                    self._log_operation('update_timestamp', chunk_id, source_url)
                else:
                    # Insere ou atualiza chunk
                    conn.execute('''
                        INSERT OR REPLACE INTO chunks (
                            chunk_id, content, content_hash, compressed_content,
                            metadata, source_url, source_title, license, stack,
                            category, language, maturity_level, quality_score,
                            created_at, updated_at, size_bytes, embedding_model
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        chunk_id, content, content_hash, compressed_content,
                        json.dumps(metadata, ensure_ascii=False),
                        source_url, source_title, license_info, stack,
                        category, language, maturity_level, quality_score,
                        current_time, current_time, len(content.encode('utf-8')),
                        metadata.get('embedding_model', '')
                    ))
                    
                    operation = 'insert' if not existing else 'update'
                    self._log_operation(operation, chunk_id, source_url)
                
                # Armazena embedding se fornecido
                if embedding:
                    embedding_blob = pickle.dumps(embedding)
                    conn.execute('''
                        INSERT OR REPLACE INTO embeddings (
                            chunk_id, embedding, embedding_model, embedding_dim, created_at
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        chunk_id, embedding_blob,
                        metadata.get('embedding_model', 'text-embedding-3-large'),
                        len(embedding), current_time
                    ))
                
                conn.commit()
            
            # Atualiza cache de metadados
            self._metadata_cache[chunk_id] = {
                'metadata': metadata,
                'last_accessed': current_time,
                'content_hash': content_hash
            }
            self._cache_dirty = True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao armazenar chunk {chunk_id}: {str(e)}")
            return False
    
    def get_chunk(self, chunk_id: str, include_embedding: bool = False) -> Optional[Dict[str, Any]]:
        """Recupera chunk por ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Busca chunk principal
                cursor = conn.execute('''
                    SELECT content, compressed_content, metadata, source_url,
                           source_title, license, stack, category, language,
                           maturity_level, quality_score, created_at, updated_at
                    FROM chunks WHERE chunk_id = ?
                ''', (chunk_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Descomprime conteúdo se necessário
                content = row[0]
                if row[1]:  # compressed_content
                    content = self._decompress_content(row[1])
                
                # Monta resultado
                result = {
                    'chunk_id': chunk_id,
                    'content': content,
                    'metadata': json.loads(row[2]),
                    'source_url': row[3],
                    'source_title': row[4],
                    'license': row[5],
                    'stack': row[6],
                    'category': row[7],
                    'language': row[8],
                    'maturity_level': row[9],
                    'quality_score': row[10],
                    'created_at': row[11],
                    'updated_at': row[12]
                }
                
                # Busca embedding se solicitado
                if include_embedding:
                    cursor = conn.execute(
                        'SELECT embedding, embedding_model, embedding_dim FROM embeddings WHERE chunk_id = ?',
                        (chunk_id,)
                    )
                    embedding_row = cursor.fetchone()
                    if embedding_row:
                        result['embedding'] = pickle.loads(embedding_row[0])
                        result['embedding_model'] = embedding_row[1]
                        result['embedding_dim'] = embedding_row[2]
                
                # Atualiza cache
                self._metadata_cache[chunk_id] = {
                    'metadata': result['metadata'],
                    'last_accessed': datetime.now().isoformat(),
                    'content_hash': self._calculate_content_hash(content)
                }
                self._cache_dirty = True
                
                return result
                
        except Exception as e:
            self.logger.error(f"Erro ao recuperar chunk {chunk_id}: {str(e)}")
            return None
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Remove chunk por ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Remove chunk e embedding (CASCADE)
                cursor = conn.execute('DELETE FROM chunks WHERE chunk_id = ?', (chunk_id,))
                deleted = cursor.rowcount > 0
                
                if deleted:
                    self._log_operation('delete', chunk_id, '')
                    
                    # Remove do cache
                    if chunk_id in self._metadata_cache:
                        del self._metadata_cache[chunk_id]
                        self._cache_dirty = True
                
                conn.commit()
                return deleted
                
        except Exception as e:
            self.logger.error(f"Erro ao deletar chunk {chunk_id}: {str(e)}")
            return False
    
    def delete_chunks_by_source(self, source_url: str) -> int:
        """Remove todos os chunks de uma fonte"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('DELETE FROM chunks WHERE source_url = ?', (source_url,))
                deleted_count = cursor.rowcount
                
                if deleted_count > 0:
                    self._log_operation('delete_by_source', '', source_url, 
                                      f"Removidos {deleted_count} chunks")
                    
                    # Remove do cache
                    to_remove = []
                    for chunk_id, cache_data in self._metadata_cache.items():
                        if cache_data['metadata'].get('source_url') == source_url:
                            to_remove.append(chunk_id)
                    
                    for chunk_id in to_remove:
                        del self._metadata_cache[chunk_id]
                    
                    if to_remove:
                        self._cache_dirty = True
                
                conn.commit()
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Erro ao deletar chunks da fonte {source_url}: {str(e)}")
            return 0
    
    def search_chunks(self, filters: Optional[Dict[str, Any]] = None, 
                     limit: int = 100) -> List[Dict[str, Any]]:
        """Busca chunks com filtros"""
        try:
            query = 'SELECT chunk_id, content, metadata, source_url, source_title, license, stack, category FROM chunks'
            params = []
            conditions = []
            
            if filters:
                if 'source_url' in filters:
                    conditions.append('source_url = ?')
                    params.append(filters['source_url'])
                
                if 'stack' in filters:
                    conditions.append('stack = ?')
                    params.append(filters['stack'])
                
                if 'category' in filters:
                    conditions.append('category = ?')
                    params.append(filters['category'])
                
                if 'license' in filters:
                    conditions.append('license = ?')
                    params.append(filters['license'])
                
                if 'updated_after' in filters:
                    conditions.append('updated_at > ?')
                    params.append(filters['updated_after'])
                
                if 'quality_score_min' in filters:
                    conditions.append('quality_score >= ?')
                    params.append(filters['quality_score_min'])
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY updated_at DESC LIMIT ?'
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        'chunk_id': row[0],
                        'content': row[1],
                        'metadata': json.loads(row[2]),
                        'source_url': row[3],
                        'source_title': row[4],
                        'license': row[5],
                        'stack': row[6],
                        'category': row[7]
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Erro na busca de chunks: {str(e)}")
            return []
    
    def _log_operation(self, operation: str, chunk_id: str, source_url: str, details: str = ''):
        """Registra operação no log"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO operation_logs (operation, chunk_id, source_url, details, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (operation, chunk_id, source_url, details, datetime.now().isoformat()))
                conn.commit()
        
        except Exception as e:
            self.logger.warning(f"Erro ao registrar operação: {str(e)}")
    
    def get_storage_stats(self) -> StorageStats:
        """Retorna estatísticas de armazenamento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Conta total de chunks
                cursor = conn.execute('SELECT COUNT(*), SUM(size_bytes) FROM chunks')
                total_chunks, total_size = cursor.fetchone()
                total_chunks = total_chunks or 0
                total_size = total_size or 0
                
                # Data mais antiga e mais nova
                cursor = conn.execute('SELECT MIN(created_at), MAX(created_at) FROM chunks')
                oldest, newest = cursor.fetchone()
                
                # Tamanho do banco
                db_size = os.path.getsize(self.db_path) if self.db_path.exists() else 0
                
                # Conta arquivos de índice
                index_files = len(list(self.storage_dir.glob('*.index'))) + len(list(self.storage_dir.glob('*.faiss')))
                
                return StorageStats(
                    total_chunks=total_chunks,
                    total_size_bytes=total_size,
                    database_size_bytes=db_size,
                    index_files_count=index_files,
                    last_updated=datetime.now().isoformat(),
                    oldest_content=oldest,
                    newest_content=newest
                )
                
        except Exception as e:
            self.logger.error(f"Erro ao calcular estatísticas: {str(e)}")
            return StorageStats(
                total_chunks=0, total_size_bytes=0, database_size_bytes=0,
                index_files_count=0, last_updated=datetime.now().isoformat(),
                oldest_content=None, newest_content=None
            )
    
    def vacuum_database(self):
        """Executa limpeza do banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('VACUUM')
                conn.execute('PRAGMA incremental_vacuum')
                conn.commit()
            
            self.logger.info("Limpeza do banco de dados concluída")
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza do banco: {str(e)}")
    
    def export_metadata(self, output_file: str) -> bool:
        """Exporta metadados para arquivo JSON"""
        try:
            chunks = self.search_chunks(limit=10000)  # Todos os chunks
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_chunks': len(chunks),
                'chunks': chunks,
                'storage_stats': asdict(self.get_storage_stats())
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Metadados exportados para: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar metadados: {str(e)}")
            return False
    
    def close(self):
        """Fecha armazenamento e salva estado"""
        try:
            # Salva cache de metadados
            self._save_metadata_cache()
            
            # Salva configuração
            self._save_storage_config()
            
            # Executa limpeza se necessário
            if self.storage_config['auto_vacuum']:
                self.vacuum_database()
            
            self.logger.info("Armazenamento fechado")
            
        except Exception as e:
            self.logger.error(f"Erro ao fechar armazenamento: {str(e)}")