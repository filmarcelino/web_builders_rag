import asyncio
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
from pathlib import Path
import shutil

from config.config import RAGConfig
from .chunker import ContentChunker, Chunk
from .embeddings import EmbeddingGenerator, EmbeddingResult
from .vector_indexer import VectorIndexer, IndexedChunk
from .text_indexer import TextIndexer, TextSearchResult

@dataclass
class IndexingResult:
    """Resultado do processo de indexação"""
    success: bool
    chunks_processed: int
    chunks_indexed: int
    errors: List[str]
    processing_time: float
    stats: Dict[str, Any]

@dataclass
class SearchResult:
    """Resultado unificado de busca"""
    chunk_id: str
    content: str
    score: float
    source: str  # 'vector', 'text', 'hybrid'
    metadata: Dict[str, Any]
    highlights: List[str]
    rationale: Optional[str] = None

class IndexManager:
    """Gerenciador central dos índices RAG"""
    
    def __init__(self, api_key: str, index_dir: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Diretório dos índices
        self.index_dir = Path(index_dir or RAGConfig.INDEX_DIR)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Componentes de indexação
        self.chunker = ContentChunker()
        self.embedding_generator = EmbeddingGenerator(api_key)
        self.vector_indexer = VectorIndexer(str(self.index_dir / "vector"))
        self.text_indexer = TextIndexer(str(self.index_dir / "text"))
        
        # Configurações
        self.api_key = api_key
        
        # Estatísticas globais
        self.global_stats = {
            'total_content_indexed': 0,
            'total_chunks_created': 0,
            'total_embeddings_generated': 0,
            'last_indexing': None,
            'indexing_sessions': 0,
            'avg_indexing_time': 0
        }
        
        # Carrega estatísticas existentes
        self._load_global_stats()
    
    def _load_global_stats(self):
        """Carrega estatísticas globais do disco"""
        stats_file = self.index_dir / "global_stats.json"
        try:
            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self.global_stats.update(json.load(f))
        except Exception as e:
            self.logger.warning(f"Erro ao carregar estatísticas globais: {str(e)}")
    
    def _save_global_stats(self):
        """Salva estatísticas globais no disco"""
        stats_file = self.index_dir / "global_stats.json"
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.global_stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erro ao salvar estatísticas globais: {str(e)}")
    
    async def index_content(self, contents: List[Dict[str, Any]]) -> IndexingResult:
        """Indexa conteúdo completo (chunking + embeddings + indexação)"""
        start_time = datetime.now()
        errors = []
        
        try:
            self.logger.info(f"Iniciando indexação de {len(contents)} conteúdos")
            
            # 1. Chunking
            self.logger.info("Fase 1: Chunking do conteúdo")
            all_chunks = []
            
            for i, content in enumerate(contents):
                try:
                    chunks = self.chunker.chunk_content(content)
                    all_chunks.extend(chunks)
                    self.logger.debug(f"Conteúdo {i+1}: {len(chunks)} chunks gerados")
                except Exception as e:
                    error_msg = f"Erro no chunking do conteúdo {i+1}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            if not all_chunks:
                return IndexingResult(
                    success=False,
                    chunks_processed=0,
                    chunks_indexed=0,
                    errors=errors + ["Nenhum chunk foi gerado"],
                    processing_time=0,
                    stats={}
                )
            
            self.logger.info(f"Chunking concluído: {len(all_chunks)} chunks gerados")
            
            # 2. Geração de embeddings
            self.logger.info("Fase 2: Geração de embeddings")
            embedding_results = await self.embedding_generator.generate_embeddings(all_chunks)
            
            # Filtra embeddings válidos
            valid_pairs = []
            for chunk, embedding in zip(all_chunks, embedding_results):
                if not embedding.error and embedding.embedding:
                    valid_pairs.append((chunk, embedding))
                else:
                    errors.append(f"Erro no embedding do chunk {chunk.id}: {embedding.error}")
            
            if not valid_pairs:
                return IndexingResult(
                    success=False,
                    chunks_processed=len(all_chunks),
                    chunks_indexed=0,
                    errors=errors + ["Nenhum embedding válido foi gerado"],
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    stats={}
                )
            
            valid_chunks = [pair[0] for pair in valid_pairs]
            valid_embeddings = [pair[1] for pair in valid_pairs]
            
            self.logger.info(f"Embeddings gerados: {len(valid_embeddings)} válidos de {len(all_chunks)} chunks")
            
            # 3. Indexação vetorial
            self.logger.info("Fase 3: Indexação vetorial")
            indexed_chunks = self.vector_indexer.add_chunks(valid_chunks, valid_embeddings)
            
            # 4. Indexação textual
            self.logger.info("Fase 4: Indexação textual")
            text_indexed_count = self.text_indexer.add_chunks(valid_chunks)
            
            # 5. Atualiza estatísticas
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.global_stats['total_content_indexed'] += len(contents)
            self.global_stats['total_chunks_created'] += len(all_chunks)
            self.global_stats['total_embeddings_generated'] += len(valid_embeddings)
            self.global_stats['last_indexing'] = datetime.now().isoformat()
            self.global_stats['indexing_sessions'] += 1
            
            # Atualiza tempo médio
            sessions = self.global_stats['indexing_sessions']
            avg_time = self.global_stats['avg_indexing_time']
            self.global_stats['avg_indexing_time'] = (
                (avg_time * (sessions - 1) + processing_time) / sessions
            )
            
            self._save_global_stats()
            
            # Coleta estatísticas detalhadas
            stats = {
                'chunking_stats': self.chunker.get_chunk_stats(all_chunks),
                'embedding_stats': self.embedding_generator.get_embedding_stats(),
                'vector_index_stats': self.vector_indexer.get_index_stats(),
                'text_index_stats': self.text_indexer.get_index_stats(),
                'global_stats': self.global_stats
            }
            
            result = IndexingResult(
                success=True,
                chunks_processed=len(all_chunks),
                chunks_indexed=len(indexed_chunks),
                errors=errors,
                processing_time=processing_time,
                stats=stats
            )
            
            self.logger.info(
                f"Indexação concluída: {len(indexed_chunks)} chunks indexados em {processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Erro crítico na indexação: {str(e)}"
            self.logger.error(error_msg)
            
            return IndexingResult(
                success=False,
                chunks_processed=0,
                chunks_indexed=0,
                errors=errors + [error_msg],
                processing_time=(datetime.now() - start_time).total_seconds(),
                stats={}
            )
    
    async def search(self, query: str, top_k: int = 8, 
                     search_type: str = "hybrid", 
                     filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Busca unificada (vetorial, textual ou híbrida)"""
        if not query.strip():
            return []
        
        self.logger.debug(f"Busca {search_type}: '{query}' (top_k={top_k})")
        
        try:
            if search_type == "vector":
                return await self._search_vector_only(query, top_k, filters)
            elif search_type == "text":
                return await self._search_text_only(query, top_k, filters)
            elif search_type == "hybrid":
                return await self._search_hybrid(query, top_k, filters)
            else:
                raise ValueError(f"Tipo de busca inválido: {search_type}")
        
        except Exception as e:
            self.logger.error(f"Erro na busca: {str(e)}")
            return []
    
    async def _search_vector_only(self, query: str, top_k: int, 
                                  filters: Optional[Dict[str, Any]]) -> List[SearchResult]:
        """Busca apenas vetorial"""
        # Gera embedding da query
        query_embedding = await self.embedding_generator.generate_single_embedding(query)
        
        if not query_embedding:
            return []
        
        # Busca vetorial
        vector_results = self.vector_indexer.search(query_embedding, top_k, filters)
        
        # Converte para SearchResult
        results = []
        for indexed_chunk, score in vector_results:
            result = SearchResult(
                chunk_id=indexed_chunk.chunk_id,
                content=indexed_chunk.content,
                score=score,
                source="vector",
                metadata=indexed_chunk.metadata,
                highlights=[indexed_chunk.content[:200] + "..." if len(indexed_chunk.content) > 200 else indexed_chunk.content]
            )
            results.append(result)
        
        return results
    
    async def _search_text_only(self, query: str, top_k: int, 
                                filters: Optional[Dict[str, Any]]) -> List[SearchResult]:
        """Busca apenas textual"""
        text_results = self.text_indexer.search(query, top_k, filters)
        
        # Converte para SearchResult
        results = []
        for text_result in text_results:
            result = SearchResult(
                chunk_id=text_result.chunk_id,
                content=text_result.content,
                score=text_result.score,
                source="text",
                metadata=text_result.metadata,
                highlights=text_result.highlights
            )
            results.append(result)
        
        return results
    
    async def _search_hybrid(self, query: str, top_k: int, 
                            filters: Optional[Dict[str, Any]]) -> List[SearchResult]:
        """Busca híbrida (vetorial + textual)"""
        # Executa ambas as buscas em paralelo
        vector_task = self._search_vector_only(query, top_k, filters)
        text_task = self._search_text_only(query, top_k, filters)
        
        vector_results, text_results = await asyncio.gather(vector_task, text_task)
        
        # Combina resultados
        combined_results = self._combine_search_results(
            vector_results, text_results, top_k
        )
        
        return combined_results
    
    def _combine_search_results(self, vector_results: List[SearchResult], 
                               text_results: List[SearchResult], 
                               top_k: int) -> List[SearchResult]:
        """Combina resultados de busca vetorial e textual"""
        # Mapeia resultados por chunk_id
        combined = {}
        
        # Adiciona resultados vetoriais
        for result in vector_results:
            combined[result.chunk_id] = {
                'result': result,
                'vector_score': result.score,
                'text_score': 0,
                'has_vector': True,
                'has_text': False
            }
        
        # Adiciona/atualiza com resultados textuais
        for result in text_results:
            if result.chunk_id in combined:
                # Chunk já existe, atualiza scores
                combined[result.chunk_id]['text_score'] = result.score
                combined[result.chunk_id]['has_text'] = True
                # Usa highlights do texto se disponível
                if result.highlights:
                    combined[result.chunk_id]['result'].highlights = result.highlights
            else:
                # Novo chunk
                combined[result.chunk_id] = {
                    'result': result,
                    'vector_score': 0,
                    'text_score': result.score,
                    'has_vector': False,
                    'has_text': True
                }
        
        # Calcula scores finais e cria lista final
        final_results = []
        
        for chunk_id, info in combined.items():
            # Pesos para combinação (podem ser ajustados)
            vector_weight = 0.7
            text_weight = 0.3
            
            # Bonus por aparecer em ambos os tipos de busca
            both_bonus = 0.2 if info['has_vector'] and info['has_text'] else 0
            
            # Score final
            final_score = (
                vector_weight * info['vector_score'] +
                text_weight * info['text_score'] +
                both_bonus
            )
            
            # Atualiza resultado
            result = info['result']
            result.score = final_score
            result.source = "hybrid"
            
            final_results.append(result)
        
        # Ordena por score final e retorna top_k
        final_results.sort(key=lambda x: x.score, reverse=True)
        return final_results[:top_k]
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[IndexedChunk]:
        """Recupera chunk específico pelo ID"""
        return self.vector_indexer.get_chunk_by_id(chunk_id)
    
    def delete_content_by_source(self, source_url: str) -> Dict[str, int]:
        """Remove todo conteúdo de uma fonte específica"""
        try:
            vector_deleted = self.vector_indexer.delete_chunks_by_source(source_url)
            text_deleted = self.text_indexer.delete_chunks_by_source(source_url)
            
            self.logger.info(f"Removido conteúdo da fonte {source_url}: {vector_deleted} chunks")
            
            return {
                'vector_deleted': vector_deleted,
                'text_deleted': text_deleted
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao remover conteúdo: {str(e)}")
            return {'vector_deleted': 0, 'text_deleted': 0}
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas abrangentes de todos os índices"""
        return {
            'global_stats': self.global_stats,
            'chunker_stats': {},  # Chunker não mantém estado
            'embedding_stats': self.embedding_generator.get_embedding_stats(),
            'vector_index_stats': self.vector_indexer.get_index_stats(),
            'text_index_stats': self.text_indexer.get_index_stats(),
            'index_directory_size_mb': self._get_directory_size(self.index_dir) / (1024 * 1024)
        }
    
    def _get_directory_size(self, path: Path) -> int:
        """Calcula tamanho total de um diretório"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            self.logger.warning(f"Erro ao calcular tamanho do diretório: {str(e)}")
        
        return total_size
    
    def optimize_indices(self):
        """Otimiza todos os índices"""
        try:
            self.logger.info("Otimizando índices...")
            
            # Otimiza índice de texto
            self.text_indexer.optimize_index()
            
            # Para índice vetorial, pode fazer rebuild se necessário
            # self.vector_indexer.rebuild_index()
            
            # Limpa cache de embeddings antigo
            # self.embedding_generator.clear_cache()
            
            self.logger.info("Otimização de índices concluída")
            
        except Exception as e:
            self.logger.error(f"Erro na otimização: {str(e)}")
    
    def backup_indices(self, backup_dir: str) -> bool:
        """Cria backup dos índices"""
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Cria backup com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"rag_indices_backup_{timestamp}"
            full_backup_path = backup_path / backup_name
            
            # Copia diretório de índices
            shutil.copytree(self.index_dir, full_backup_path)
            
            self.logger.info(f"Backup criado em: {full_backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {str(e)}")
            return False
    
    def restore_indices(self, backup_path: str) -> bool:
        """Restaura índices de um backup"""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                self.logger.error(f"Backup não encontrado: {backup_path}")
                return False
            
            # Fecha conexões atuais
            self.close()
            
            # Remove índices atuais
            if self.index_dir.exists():
                shutil.rmtree(self.index_dir)
            
            # Restaura do backup
            shutil.copytree(backup_dir, self.index_dir)
            
            # Reinicializa componentes
            self.vector_indexer = VectorIndexer(str(self.index_dir / "vector"))
            self.text_indexer = TextIndexer(str(self.index_dir / "text"))
            self._load_global_stats()
            
            self.logger.info(f"Índices restaurados de: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup: {str(e)}")
            return False
    
    def close(self):
        """Fecha todas as conexões e salva estado"""
        try:
            self.vector_indexer.close()
            self.text_indexer.close()
            self._save_global_stats()
            
            self.logger.info("IndexManager fechado")
            
        except Exception as e:
            self.logger.error(f"Erro ao fechar IndexManager: {str(e)}")