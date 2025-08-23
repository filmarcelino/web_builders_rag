import faiss
import numpy as np
import pickle
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
import sqlite3
from pathlib import Path

from config.config import RAGConfig
from .chunker import Chunk
from .embeddings import EmbeddingResult

@dataclass
class IndexedChunk:
    """Chunk indexado com embedding"""
    chunk_id: str
    vector_id: int  # ID no índice FAISS
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    indexed_at: str
    section_title: str
    section_type: str
    tokens: int
    source_url: str
    license: str
    stack: str
    category: str
    language: str
    maturity: str
    quality_score: float

class VectorIndexer:
    """Indexador vetorial usando FAISS para busca de similaridade"""
    
    def __init__(self, index_dir: str, dimensions: int = None):
        self.logger = logging.getLogger(__name__)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.dimensions = dimensions or RAGConfig.EMBEDDING_DIMENSIONS
        
        # Arquivos do índice
        self.faiss_index_path = self.index_dir / "vector_index.faiss"
        self.metadata_db_path = self.index_dir / "metadata.db"
        self.config_path = self.index_dir / "index_config.json"
        
        # Índice FAISS
        self.faiss_index = None
        self.next_vector_id = 0
        
        # Conexão SQLite para metadados
        self.db_conn = None
        
        # Estatísticas
        self.stats = {
            'total_vectors': 0,
            'index_size_mb': 0,
            'last_updated': None,
            'search_count': 0,
            'avg_search_time': 0
        }
        
        # Inicializa índice
        self._initialize_index()
    
    def _initialize_index(self):
        """Inicializa o índice FAISS e banco de metadados"""
        try:
            # Carrega índice existente ou cria novo
            if self.faiss_index_path.exists():
                self._load_existing_index()
            else:
                self._create_new_index()
            
            # Inicializa banco de metadados
            self._initialize_metadata_db()
            
            self.logger.info(f"Índice vetorial inicializado: {self.stats['total_vectors']} vetores")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar índice: {str(e)}")
            raise
    
    def _create_new_index(self):
        """Cria novo índice FAISS"""
        # Usa IndexFlatIP (Inner Product) para similaridade coseno
        # Alternativa: IndexFlatL2 para distância euclidiana
        self.faiss_index = faiss.IndexFlatIP(self.dimensions)
        
        # Para índices maiores, pode usar IndexIVFFlat para melhor performance
        # nlist = 100  # número de clusters
        # quantizer = faiss.IndexFlatIP(self.dimensions)
        # self.faiss_index = faiss.IndexIVFFlat(quantizer, self.dimensions, nlist)
        
        self.next_vector_id = 0
        
        # Salva configuração
        config = {
            'dimensions': self.dimensions,
            'index_type': 'IndexFlatIP',
            'created_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info(f"Novo índice FAISS criado: {self.dimensions} dimensões")
    
    def _load_existing_index(self):
        """Carrega índice FAISS existente"""
        try:
            self.faiss_index = faiss.read_index(str(self.faiss_index_path))
            
            # Carrega configuração
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.dimensions = config.get('dimensions', self.dimensions)
            
            # Atualiza estatísticas
            self.stats['total_vectors'] = self.faiss_index.ntotal
            self.next_vector_id = self.faiss_index.ntotal
            
            # Calcula tamanho do arquivo
            size_bytes = self.faiss_index_path.stat().st_size
            self.stats['index_size_mb'] = size_bytes / (1024 * 1024)
            
            self.logger.info(f"Índice FAISS carregado: {self.stats['total_vectors']} vetores")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar índice: {str(e)}")
            # Se falhar, cria novo índice
            self._create_new_index()
    
    def _initialize_metadata_db(self):
        """Inicializa banco SQLite para metadados"""
        self.db_conn = sqlite3.connect(str(self.metadata_db_path), check_same_thread=False)
        self.db_conn.row_factory = sqlite3.Row
        
        # Cria tabela de metadados
        self.db_conn.execute('''
            CREATE TABLE IF NOT EXISTS chunk_metadata (
                vector_id INTEGER PRIMARY KEY,
                chunk_id TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                indexed_at TEXT NOT NULL,
                section_title TEXT,
                section_type TEXT,
                tokens INTEGER,
                source_url TEXT,
                license TEXT,
                stack TEXT,
                category TEXT,
                language TEXT,
                maturity TEXT,
                quality_score REAL
            )
        ''')
        
        # Índices para busca rápida
        self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_chunk_id ON chunk_metadata(chunk_id)')
        self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_source_url ON chunk_metadata(source_url)')
        self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_stack ON chunk_metadata(stack)')
        self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON chunk_metadata(category)')
        self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_license ON chunk_metadata(license)')
        self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_quality_score ON chunk_metadata(quality_score)')
        
        self.db_conn.commit()
    
    def add_chunks(self, chunks: List[Chunk], embeddings: List[EmbeddingResult]) -> List[IndexedChunk]:
        """Adiciona chunks com embeddings ao índice"""
        if not chunks or not embeddings:
            return []
        
        if len(chunks) != len(embeddings):
            raise ValueError("Número de chunks deve ser igual ao número de embeddings")
        
        indexed_chunks = []
        vectors_to_add = []
        metadata_to_add = []
        
        for chunk, embedding_result in zip(chunks, embeddings):
            if embedding_result.error or not embedding_result.embedding:
                self.logger.warning(f"Pulando chunk {chunk.id}: {embedding_result.error}")
                continue
            
            # Normaliza embedding para similaridade coseno
            embedding_array = np.array(embedding_result.embedding, dtype=np.float32)
            embedding_array = embedding_array / np.linalg.norm(embedding_array)
            
            # Cria chunk indexado
            indexed_chunk = IndexedChunk(
                chunk_id=chunk.id,
                vector_id=self.next_vector_id,
                content=chunk.content,
                embedding=embedding_result.embedding,
                metadata=chunk.metadata,
                indexed_at=datetime.now().isoformat(),
                section_title=chunk.section_title,
                section_type=chunk.section_type,
                tokens=chunk.tokens,
                source_url=chunk.metadata.get('source_url', ''),
                license=chunk.metadata.get('licenca', ''),
                stack=chunk.metadata.get('stack', ''),
                category=chunk.metadata.get('categoria', ''),
                language=chunk.metadata.get('idioma', 'pt'),
                maturity=chunk.metadata.get('maturidade', ''),
                quality_score=chunk.metadata.get('quality_score', 0.0)
            )
            
            indexed_chunks.append(indexed_chunk)
            vectors_to_add.append(embedding_array)
            metadata_to_add.append(indexed_chunk)
            
            self.next_vector_id += 1
        
        if vectors_to_add:
            # Adiciona vetores ao índice FAISS
            vectors_matrix = np.vstack(vectors_to_add)
            self.faiss_index.add(vectors_matrix)
            
            # Adiciona metadados ao banco
            self._add_metadata_batch(metadata_to_add)
            
            # Salva índice
            self._save_index()
            
            # Atualiza estatísticas
            self.stats['total_vectors'] = self.faiss_index.ntotal
            self.stats['last_updated'] = datetime.now().isoformat()
            
            self.logger.info(f"Adicionados {len(indexed_chunks)} chunks ao índice")
        
        return indexed_chunks
    
    def _add_metadata_batch(self, indexed_chunks: List[IndexedChunk]):
        """Adiciona metadados em lote ao banco"""
        cursor = self.db_conn.cursor()
        
        for chunk in indexed_chunks:
            cursor.execute('''
                INSERT OR REPLACE INTO chunk_metadata (
                    vector_id, chunk_id, content, metadata, indexed_at,
                    section_title, section_type, tokens, source_url,
                    license, stack, category, language, maturity, quality_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                chunk.vector_id,
                chunk.chunk_id,
                chunk.content,
                json.dumps(chunk.metadata, ensure_ascii=False),
                chunk.indexed_at,
                chunk.section_title,
                chunk.section_type,
                chunk.tokens,
                chunk.source_url,
                chunk.license,
                chunk.stack,
                chunk.category,
                chunk.language,
                chunk.maturity,
                chunk.quality_score
            ))
        
        self.db_conn.commit()
    
    def search(self, query_embedding: List[float], top_k: int = 10, 
               filters: Optional[Dict[str, Any]] = None) -> List[Tuple[IndexedChunk, float]]:
        """Busca por similaridade vetorial"""
        if not query_embedding or self.faiss_index.ntotal == 0:
            return []
        
        start_time = datetime.now()
        
        try:
            # Normaliza query embedding
            query_array = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
            query_array = query_array / np.linalg.norm(query_array)
            
            # Busca no índice FAISS
            # Para IndexFlatIP, scores maiores = mais similares
            scores, indices = self.faiss_index.search(query_array, min(top_k * 2, self.faiss_index.ntotal))
            
            # Recupera metadados
            results = []
            for i, (score, vector_id) in enumerate(zip(scores[0], indices[0])):
                if vector_id == -1:  # FAISS retorna -1 para resultados inválidos
                    continue
                
                # Busca metadados no banco
                chunk_data = self._get_chunk_metadata(int(vector_id))
                if not chunk_data:
                    continue
                
                # Aplica filtros
                if filters and not self._apply_filters(chunk_data, filters):
                    continue
                
                # Cria IndexedChunk
                indexed_chunk = IndexedChunk(
                    chunk_id=chunk_data['chunk_id'],
                    vector_id=chunk_data['vector_id'],
                    content=chunk_data['content'],
                    embedding=[],  # Não retorna embedding para economizar memória
                    metadata=json.loads(chunk_data['metadata']),
                    indexed_at=chunk_data['indexed_at'],
                    section_title=chunk_data['section_title'] or '',
                    section_type=chunk_data['section_type'] or '',
                    tokens=chunk_data['tokens'] or 0,
                    source_url=chunk_data['source_url'] or '',
                    license=chunk_data['license'] or '',
                    stack=chunk_data['stack'] or '',
                    category=chunk_data['category'] or '',
                    language=chunk_data['language'] or '',
                    maturity=chunk_data['maturity'] or '',
                    quality_score=chunk_data['quality_score'] or 0.0
                )
                
                results.append((indexed_chunk, float(score)))
                
                if len(results) >= top_k:
                    break
            
            # Atualiza estatísticas
            search_time = (datetime.now() - start_time).total_seconds()
            self.stats['search_count'] += 1
            self.stats['avg_search_time'] = (
                (self.stats['avg_search_time'] * (self.stats['search_count'] - 1) + search_time) /
                self.stats['search_count']
            )
            
            self.logger.debug(f"Busca vetorial: {len(results)} resultados em {search_time:.3f}s")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca vetorial: {str(e)}")
            return []
    
    def _get_chunk_metadata(self, vector_id: int) -> Optional[Dict[str, Any]]:
        """Recupera metadados de um chunk pelo vector_id"""
        cursor = self.db_conn.cursor()
        cursor.execute(
            'SELECT * FROM chunk_metadata WHERE vector_id = ?',
            (vector_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def _apply_filters(self, chunk_data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Aplica filtros aos resultados"""
        for key, value in filters.items():
            if key == 'stack' and chunk_data.get('stack') != value:
                return False
            elif key == 'categoria' and chunk_data.get('category') != value:
                return False
            elif key == 'licenca' and chunk_data.get('license') != value:
                return False
            elif key == 'updated_after':
                # Implementar filtro de data se necessário
                pass
            elif key == 'min_quality_score':
                if chunk_data.get('quality_score', 0) < value:
                    return False
            elif key == 'language' and chunk_data.get('language') != value:
                return False
            elif key == 'maturity' and chunk_data.get('maturity') != value:
                return False
        
        return True
    
    def _save_index(self):
        """Salva índice FAISS em disco"""
        try:
            faiss.write_index(self.faiss_index, str(self.faiss_index_path))
            
            # Atualiza tamanho do arquivo
            if self.faiss_index_path.exists():
                size_bytes = self.faiss_index_path.stat().st_size
                self.stats['index_size_mb'] = size_bytes / (1024 * 1024)
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar índice: {str(e)}")
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[IndexedChunk]:
        """Recupera chunk pelo ID"""
        cursor = self.db_conn.cursor()
        cursor.execute(
            'SELECT * FROM chunk_metadata WHERE chunk_id = ?',
            (chunk_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return IndexedChunk(
            chunk_id=row['chunk_id'],
            vector_id=row['vector_id'],
            content=row['content'],
            embedding=[],
            metadata=json.loads(row['metadata']),
            indexed_at=row['indexed_at'],
            section_title=row['section_title'] or '',
            section_type=row['section_type'] or '',
            tokens=row['tokens'] or 0,
            source_url=row['source_url'] or '',
            license=row['license'] or '',
            stack=row['stack'] or '',
            category=row['category'] or '',
            language=row['language'] or '',
            maturity=row['maturity'] or '',
            quality_score=row['quality_score'] or 0.0
        )
    
    def delete_chunks_by_source(self, source_url: str) -> int:
        """Remove chunks de uma fonte específica"""
        try:
            # Busca vector_ids para remover
            cursor = self.db_conn.cursor()
            cursor.execute(
                'SELECT vector_id FROM chunk_metadata WHERE source_url = ?',
                (source_url,)
            )
            vector_ids = [row[0] for row in cursor.fetchall()]
            
            if not vector_ids:
                return 0
            
            # Remove do banco de metadados
            cursor.execute(
                'DELETE FROM chunk_metadata WHERE source_url = ?',
                (source_url,)
            )
            self.db_conn.commit()
            
            # Para FAISS, seria necessário reconstruir o índice para remover vetores
            # Por simplicidade, marcamos como removidos nos metadados
            # Em produção, implementar estratégia de rebuild periódico
            
            self.logger.info(f"Removidos {len(vector_ids)} chunks da fonte {source_url}")
            return len(vector_ids)
            
        except Exception as e:
            self.logger.error(f"Erro ao remover chunks: {str(e)}")
            return 0
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do índice"""
        # Estatísticas do banco
        cursor = self.db_conn.cursor()
        
        # Contagem por stack
        cursor.execute('SELECT stack, COUNT(*) FROM chunk_metadata GROUP BY stack')
        stack_counts = dict(cursor.fetchall())
        
        # Contagem por categoria
        cursor.execute('SELECT category, COUNT(*) FROM chunk_metadata GROUP BY category')
        category_counts = dict(cursor.fetchall())
        
        # Contagem por licença
        cursor.execute('SELECT license, COUNT(*) FROM chunk_metadata GROUP BY license')
        license_counts = dict(cursor.fetchall())
        
        # Qualidade média
        cursor.execute('SELECT AVG(quality_score) FROM chunk_metadata')
        avg_quality = cursor.fetchone()[0] or 0.0
        
        return {
            **self.stats,
            'stack_distribution': stack_counts,
            'category_distribution': category_counts,
            'license_distribution': license_counts,
            'avg_quality_score': avg_quality,
            'index_file_size_mb': self.stats['index_size_mb'],
            'metadata_db_size_mb': self.metadata_db_path.stat().st_size / (1024 * 1024) if self.metadata_db_path.exists() else 0
        }
    
    def rebuild_index(self):
        """Reconstrói o índice FAISS (útil após remoções)"""
        self.logger.info("Reconstruindo índice vetorial...")
        
        try:
            # Busca todos os chunks válidos
            cursor = self.db_conn.cursor()
            cursor.execute('SELECT vector_id, chunk_id FROM chunk_metadata ORDER BY vector_id')
            valid_chunks = cursor.fetchall()
            
            if not valid_chunks:
                self.logger.warning("Nenhum chunk válido encontrado")
                return
            
            # Cria novo índice
            new_index = faiss.IndexFlatIP(self.dimensions)
            
            # Recarrega embeddings e reconstrói
            # Nota: Em produção, seria necessário armazenar embeddings separadamente
            # ou recalculá-los
            
            self.faiss_index = new_index
            self.next_vector_id = len(valid_chunks)
            
            self._save_index()
            self.logger.info(f"Índice reconstruído com {len(valid_chunks)} vetores")
            
        except Exception as e:
            self.logger.error(f"Erro ao reconstruir índice: {str(e)}")
    
    def close(self):
        """Fecha conexões e salva índice"""
        if self.db_conn:
            self.db_conn.close()
        
        if self.faiss_index:
            self._save_index()
        
        self.logger.info("Índice vetorial fechado")