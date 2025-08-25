#!/usr/bin/env python3
"""
Sistema de ingestão para processar e indexar dados no RAG.
Carrega chunks processados e os adiciona ao sistema de busca vetorial.
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime
import hashlib

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv não instalado. Execute: pip install python-dotenv")

# Imports para RAG
try:
    import openai
    from openai import OpenAI
except ImportError:
    print("OpenAI não instalado. Execute: pip install openai")
    exit(1)

try:
    import faiss
except ImportError:
    print("FAISS não instalado. Execute: pip install faiss-cpu")
    exit(1)

try:
    import redis
except ImportError:
    print("Redis não instalado. Execute: pip install redis")
    exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddedChunk:
    """Representa um chunk com embedding."""
    id: str
    content: str
    embedding: np.ndarray
    metadata: Dict
    source_file: str
    title: str
    token_count: int

class RAGIngestor:
    def __init__(self, 
                 processed_corpus_dir: str = "processed_corpus",
                 rag_data_dir: str = "rag_data",
                 openai_api_key: Optional[str] = None,
                 redis_url: Optional[str] = None):
        
        self.processed_corpus_dir = Path(processed_corpus_dir)
        self.rag_data_dir = Path(rag_data_dir)
        self.rag_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar OpenAI
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não encontrada")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Configurar Redis (opcional)
        self.redis_url = redis_url or os.getenv('REDIS_URL')
        self.redis_client = None
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                self.redis_client.ping()
                logger.info("Conectado ao Redis para cache")
            except Exception as e:
                logger.warning(f"Não foi possível conectar ao Redis: {e}")
                self.redis_client = None
        
        # Configurações de embedding
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        self.batch_size = 1  # Processar um por vez para evitar limite de tokens
        
        # Inicializar FAISS
        self.index = None
        self.chunk_metadata = []  # Metadados dos chunks indexados
        
        # Arquivo de índice
        self.index_file = self.rag_data_dir / "faiss_index.bin"
        self.metadata_file = self.rag_data_dir / "chunk_metadata.json"
        self.ingestion_log_file = self.rag_data_dir / "ingestion_log.json"
    
    def load_existing_index(self) -> bool:
        """Carrega índice existente se disponível."""
        try:
            if self.index_file.exists() and self.metadata_file.exists():
                logger.info("Carregando índice existente...")
                
                # Carregar índice FAISS
                self.index = faiss.read_index(str(self.index_file))
                
                # Carregar metadados
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata_data = json.load(f)
                    # Se for dict, converter para lista
                    if isinstance(metadata_data, dict):
                        self.chunk_metadata = list(metadata_data.values())
                    else:
                        self.chunk_metadata = metadata_data
                
                logger.info(f"Índice carregado com {self.index.ntotal} vetores")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao carregar índice existente: {e}")
            return False
    
    def create_new_index(self) -> None:
        """Cria um novo índice FAISS."""
        logger.info("Criando novo índice FAISS...")
        
        # Usar IndexFlatIP para busca por similaridade de cosseno
        self.index = faiss.IndexFlatIP(self.embedding_dimension)
        self.chunk_metadata = []
    
    def get_embedding_from_cache(self, text: str) -> Optional[np.ndarray]:
        """Obtém embedding do cache Redis se disponível."""
        if not self.redis_client:
            return None
        
        try:
            # Usar hash do texto como chave
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_key = f"embedding:{text_hash}"
            
            cached = self.redis_client.get(cache_key)
            if cached:
                return np.frombuffer(cached, dtype=np.float32)
            
            return None
            
        except Exception as e:
            logger.warning(f"Erro ao acessar cache: {e}")
            return None
    
    def cache_embedding(self, text: str, embedding: np.ndarray) -> None:
        """Salva embedding no cache Redis."""
        if not self.redis_client:
            return
        
        try:
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_key = f"embedding:{text_hash}"
            
            # Cache por 7 dias
            self.redis_client.setex(
                cache_key, 
                7 * 24 * 3600, 
                embedding.astype(np.float32).tobytes()
            )
            
        except Exception as e:
            logger.warning(f"Erro ao salvar no cache: {e}")
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Obtém embeddings para um batch de textos."""
        embeddings = []
        texts_to_embed = []
        cached_indices = []
        
        # Verificar cache primeiro
        for i, text in enumerate(texts):
            cached_embedding = self.get_embedding_from_cache(text)
            if cached_embedding is not None:
                embeddings.append(cached_embedding)
                cached_indices.append(i)
            else:
                embeddings.append(None)
                texts_to_embed.append((i, text))
        
        # Obter embeddings não cacheados
        if texts_to_embed:
            try:
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=[text for _, text in texts_to_embed]
                )
                
                for j, (original_index, text) in enumerate(texts_to_embed):
                    embedding = np.array(response.data[j].embedding, dtype=np.float32)
                    
                    # Normalizar para busca por cosseno
                    embedding = embedding / np.linalg.norm(embedding)
                    
                    embeddings[original_index] = embedding
                    
                    # Salvar no cache
                    self.cache_embedding(text, embedding)
                
            except Exception as e:
                logger.error(f"Erro ao obter embeddings: {e}")
                raise
        
        return embeddings
    
    def load_processed_chunks(self) -> List[Dict]:
        """Carrega todos os chunks processados."""
        logger.info("Carregando chunks processados...")
        
        all_chunks = []
        
        # Carregar todos os arquivos de batch
        batch_files = list(self.processed_corpus_dir.glob("chunks_batch_*.json"))
        batch_files.sort()
        
        for batch_file in batch_files:
            try:
                with open(batch_file, 'r', encoding='utf-8') as f:
                    batch_chunks = json.load(f)
                    all_chunks.extend(batch_chunks)
                    
                logger.info(f"Carregados {len(batch_chunks)} chunks de {batch_file.name}")
                
            except Exception as e:
                logger.error(f"Erro ao carregar {batch_file}: {e}")
        
        logger.info(f"Total de chunks carregados: {len(all_chunks)}")
        return all_chunks
    
    def filter_existing_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Filtra chunks que já foram indexados."""
        if not self.chunk_metadata:
            return chunks
        
        existing_ids = {chunk['id'] for chunk in self.chunk_metadata}
        new_chunks = [chunk for chunk in chunks if chunk['id'] not in existing_ids]
        
        logger.info(f"Filtrando: {len(chunks)} total, {len(new_chunks)} novos")
        return new_chunks
    
    async def process_chunks_batch(self, chunks: List[Dict]) -> List[EmbeddedChunk]:
        """Processa um batch de chunks para criar embeddings."""
        if not chunks:
            return []
        
        # Preparar textos para embedding
        texts = []
        for chunk in chunks:
            # Combinar título e conteúdo para melhor contexto
            title = chunk.get('title', '')
            content = chunk.get('content', '')
            
            if title and title not in content:
                text = f"{title}\n\n{content}"
            else:
                text = content
            
            # Truncar texto se for muito longo (limite de ~2000 tokens para segurança)
            if len(text) > 8000:  # Aproximadamente 2000 tokens
                text = text[:8000] + "..."
            
            texts.append(text)
        
        # Obter embeddings
        embeddings = await self.get_embeddings_batch(texts)
        
        # Criar objetos EmbeddedChunk
        embedded_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            if embedding is not None:
                embedded_chunk = EmbeddedChunk(
                    id=chunk['id'],
                    content=chunk['content'],
                    embedding=embedding,
                    metadata=chunk['metadata'],
                    source_file=chunk['source_file'],
                    title=chunk['title'],
                    token_count=chunk['token_count']
                )
                embedded_chunks.append(embedded_chunk)
        
        return embedded_chunks
    
    def add_chunks_to_index(self, embedded_chunks: List[EmbeddedChunk]) -> None:
        """Adiciona chunks ao índice FAISS."""
        if not embedded_chunks:
            return
        
        # Preparar embeddings para FAISS
        embeddings_matrix = np.vstack([chunk.embedding for chunk in embedded_chunks])
        
        # Adicionar ao índice
        self.index.add(embeddings_matrix)
        
        # Adicionar metadados
        for chunk in embedded_chunks:
            metadata = {
                'id': chunk.id,
                'content': chunk.content,
                'title': chunk.title,
                'source_file': chunk.source_file,
                'metadata': chunk.metadata,
                'token_count': chunk.token_count,
                'indexed_at': datetime.now().isoformat()
            }
            self.chunk_metadata.append(metadata)
        
        logger.info(f"Adicionados {len(embedded_chunks)} chunks ao índice")
    
    def save_index(self) -> None:
        """Salva o índice e metadados."""
        logger.info("Salvando índice...")
        
        try:
            # Criar diretórios se não existirem
            logger.info(f"Criando diretório: {self.rag_data_dir}")
            self.rag_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Verificar se o índice existe
            if self.index is None:
                logger.error("Índice FAISS não foi inicializado")
                return
            
            # Salvar índice FAISS
            logger.info(f"Salvando índice FAISS em: {self.index_file}")
            faiss.write_index(self.index, str(self.index_file))
            
            # Salvar metadados
            logger.info(f"Salvando metadados em: {self.metadata_file}")
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.chunk_metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Índice salvo com {self.index.ntotal} vetores")
            
        except Exception as e:
            logger.error(f"Erro ao salvar índice: {e}")
            raise
    
    def log_ingestion(self, stats: Dict) -> None:
        """Registra estatísticas da ingestão."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'stats': stats
        }
        
        # Carregar log existente
        ingestion_log = []
        if self.ingestion_log_file.exists():
            try:
                with open(self.ingestion_log_file, 'r', encoding='utf-8') as f:
                    ingestion_log = json.load(f)
            except:
                pass
        
        # Adicionar nova entrada
        ingestion_log.append(log_entry)
        
        # Manter apenas últimas 100 entradas
        ingestion_log = ingestion_log[-100:]
        
        # Salvar log
        with open(self.ingestion_log_file, 'w', encoding='utf-8') as f:
            json.dump(ingestion_log, f, ensure_ascii=False, indent=2)
    
    async def run_ingestion(self, force_reindex: bool = False) -> None:
        """Executa todo o processo de ingestão."""
        logger.info("=== INICIANDO INGESTÃO NO RAG ===")
        
        try:
            # Verificar se diretório de chunks processados existe
            if not self.processed_corpus_dir.exists():
                logger.error(f"Diretório não encontrado: {self.processed_corpus_dir}")
                return
            
            # Carregar ou criar índice
            if not force_reindex and self.load_existing_index():
                logger.info("Usando índice existente")
            else:
                self.create_new_index()
            
            # Carregar chunks processados
            all_chunks = self.load_processed_chunks()
            
            if not all_chunks:
                logger.warning("Nenhum chunk encontrado para processar")
                return
            
            # Filtrar chunks já indexados (se não for reindexação forçada)
            if not force_reindex:
                chunks_to_process = self.filter_existing_chunks(all_chunks)
            else:
                chunks_to_process = all_chunks
                self.create_new_index()  # Recriar índice
            
            if not chunks_to_process:
                logger.info("Todos os chunks já foram indexados")
                return
            
            logger.info(f"Processando {len(chunks_to_process)} chunks...")
            
            # Processar em batches
            total_processed = 0
            
            for i in range(0, len(chunks_to_process), self.batch_size):
                batch = chunks_to_process[i:i + self.batch_size]
                
                logger.info(f"Processando batch {i // self.batch_size + 1}...")
                
                # Processar batch
                embedded_chunks = await self.process_chunks_batch(batch)
                
                # Adicionar ao índice
                self.add_chunks_to_index(embedded_chunks)
                
                total_processed += len(embedded_chunks)
                
                # Salvar progresso a cada 5 batches
                if (i // self.batch_size + 1) % 5 == 0:
                    self.save_index()
                    logger.info(f"Progresso salvo: {total_processed} chunks processados")
            
            # Salvar índice final
            self.save_index()
            
            # Estatísticas finais
            stats = {
                'total_chunks_processed': total_processed,
                'total_chunks_in_index': self.index.ntotal,
                'embedding_model': self.embedding_model,
                'embedding_dimension': self.embedding_dimension,
                'force_reindex': force_reindex
            }
            
            # Registrar ingestão
            self.log_ingestion(stats)
            
            logger.info("=== ESTATÍSTICAS DA INGESTÃO ===")
            logger.info(f"Chunks processados nesta execução: {total_processed:,}")
            logger.info(f"Total de chunks no índice: {self.index.ntotal:,}")
            logger.info(f"Modelo de embedding: {self.embedding_model}")
            logger.info("=== INGESTÃO CONCLUÍDA ===")
            
        except Exception as e:
            logger.error(f"Erro durante a ingestão: {e}")
            raise
    
    def test_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Testa a busca no índice criado."""
        if not self.index or self.index.ntotal == 0:
            logger.error("Índice não carregado ou vazio")
            return []
        
        try:
            # Obter embedding da query
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=[query]
            )
            
            query_embedding = np.array(response.data[0].embedding, dtype=np.float32)
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # Buscar no índice
            scores, indices = self.index.search(query_embedding.reshape(1, -1), top_k)
            
            # Preparar resultados
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.chunk_metadata):
                    result = self.chunk_metadata[idx].copy()
                    result['similarity_score'] = float(score)
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro durante teste de busca: {e}")
            return []

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingestão de dados no RAG')
    parser.add_argument('--force-reindex', action='store_true', 
                       help='Forçar reindexação completa')
    parser.add_argument('--test-query', type=str, 
                       help='Testar busca com uma query')
    
    args = parser.parse_args()
    
    # Criar ingestor
    ingestor = RAGIngestor()
    
    if args.test_query:
        # Testar busca
        if not ingestor.load_existing_index():
            logger.error("Nenhum índice encontrado para testar")
            return
        
        logger.info(f"Testando busca: '{args.test_query}'")
        results = ingestor.test_search(args.test_query)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']} (Score: {result['similarity_score']:.3f})")
            print(f"   Fonte: {result['source_file']}")
            print(f"   Conteúdo: {result['content'][:200]}...")
    
    else:
        # Executar ingestão
        asyncio.run(ingestor.run_ingestion(force_reindex=args.force_reindex))

if __name__ == "__main__":
    main()