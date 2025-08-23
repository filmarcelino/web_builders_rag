import asyncio
import aiohttp
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor

from config.config import RAGConfig
from .chunker import Chunk

@dataclass
class EmbeddingResult:
    """Resultado de embedding para um chunk"""
    chunk_id: str
    embedding: List[float]
    model: str
    dimensions: int
    created_at: str
    processing_time: float
    error: Optional[str] = None

class EmbeddingGenerator:
    """Gerador de embeddings para chunks de conteúdo"""
    
    def __init__(self, api_key: str, model: str = None):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.model = model or RAGConfig.EMBEDDING_MODEL
        self.dimensions = RAGConfig.EMBEDDING_DIMENSIONS
        self.batch_size = RAGConfig.EMBEDDING_BATCH_SIZE
        
        # URLs da API
        self.openai_url = "https://api.openai.com/v1/embeddings"
        
        # Cache de embeddings
        self.embedding_cache = {}
        
        # Rate limiting
        self.requests_per_minute = 3000  # Limite da OpenAI
        self.request_times = []
        
        # Estatísticas
        self.stats = {
            'total_requests': 0,
            'total_tokens': 0,
            'cache_hits': 0,
            'errors': 0,
            'avg_processing_time': 0
        }
    
    async def generate_embeddings(self, chunks: List[Chunk]) -> List[EmbeddingResult]:
        """Gera embeddings para uma lista de chunks"""
        if not chunks:
            return []
        
        self.logger.info(f"Gerando embeddings para {len(chunks)} chunks")
        start_time = time.time()
        
        # Divide em batches
        batches = self._create_batches(chunks)
        all_results = []
        
        # Processa batches em paralelo (com limite)
        semaphore = asyncio.Semaphore(5)  # Máximo 5 batches simultâneos
        
        async def process_batch_with_semaphore(batch):
            async with semaphore:
                return await self._process_batch(batch)
        
        # Executa todos os batches
        batch_tasks = [process_batch_with_semaphore(batch) for batch in batches]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Coleta resultados
        for result in batch_results:
            if isinstance(result, Exception):
                self.logger.error(f"Erro em batch: {str(result)}")
                continue
            all_results.extend(result)
        
        # Atualiza estatísticas
        processing_time = time.time() - start_time
        self.stats['avg_processing_time'] = processing_time / len(chunks) if chunks else 0
        
        self.logger.info(
            f"Embeddings gerados: {len(all_results)}/{len(chunks)} chunks em {processing_time:.2f}s"
        )
        
        return all_results
    
    def _create_batches(self, chunks: List[Chunk]) -> List[List[Chunk]]:
        """Divide chunks em batches para processamento"""
        batches = []
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batches.append(batch)
        return batches
    
    async def _process_batch(self, chunks: List[Chunk]) -> List[EmbeddingResult]:
        """Processa um batch de chunks"""
        results = []
        
        # Verifica cache primeiro
        chunks_to_process = []
        for chunk in chunks:
            cache_key = self._get_cache_key(chunk.content)
            if cache_key in self.embedding_cache:
                # Cache hit
                cached_embedding = self.embedding_cache[cache_key]
                result = EmbeddingResult(
                    chunk_id=chunk.id,
                    embedding=cached_embedding,
                    model=self.model,
                    dimensions=len(cached_embedding),
                    created_at=datetime.now().isoformat(),
                    processing_time=0.0
                )
                results.append(result)
                self.stats['cache_hits'] += 1
            else:
                chunks_to_process.append(chunk)
        
        # Processa chunks que não estão no cache
        if chunks_to_process:
            api_results = await self._call_embedding_api(chunks_to_process)
            results.extend(api_results)
        
        return results
    
    async def _call_embedding_api(self, chunks: List[Chunk]) -> List[EmbeddingResult]:
        """Chama a API de embeddings"""
        # Rate limiting
        await self._wait_for_rate_limit()
        
        # Prepara textos
        texts = [self._prepare_text_for_embedding(chunk) for chunk in chunks]
        
        # Payload da API
        payload = {
            "input": texts,
            "model": self.model,
            "encoding_format": "float"
        }
        
        if self.dimensions:
            payload["dimensions"] = self.dimensions
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.openai_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Erro na API: {response.status} - {error_text}")
                        self.stats['errors'] += 1
                        return self._create_error_results(chunks, f"API Error: {response.status}")
                    
                    data = await response.json()
                    processing_time = time.time() - start_time
                    
                    # Atualiza estatísticas
                    self.stats['total_requests'] += 1
                    self.stats['total_tokens'] += data.get('usage', {}).get('total_tokens', 0)
                    
                    # Processa resultados
                    return self._process_api_response(chunks, data, processing_time)
        
        except asyncio.TimeoutError:
            self.logger.error("Timeout na API de embeddings")
            self.stats['errors'] += 1
            return self._create_error_results(chunks, "Timeout")
        
        except Exception as e:
            self.logger.error(f"Erro ao chamar API de embeddings: {str(e)}")
            self.stats['errors'] += 1
            return self._create_error_results(chunks, str(e))
    
    def _prepare_text_for_embedding(self, chunk: Chunk) -> str:
        """Prepara texto do chunk para embedding"""
        # Combina título da seção com conteúdo
        text_parts = []
        
        if chunk.section_title and chunk.section_title != "Sem título":
            text_parts.append(f"Seção: {chunk.section_title}")
        
        if chunk.section_type and chunk.section_type != "general":
            text_parts.append(f"Tipo: {chunk.section_type}")
        
        # Adiciona contexto de metadados importantes
        metadata = chunk.metadata
        if metadata.get('stack'):
            text_parts.append(f"Stack: {metadata['stack']}")
        
        if metadata.get('categoria'):
            text_parts.append(f"Categoria: {metadata['categoria']}")
        
        # Adiciona conteúdo principal
        text_parts.append(chunk.content)
        
        # Junta tudo
        full_text = "\n".join(text_parts)
        
        # Limita tamanho (OpenAI tem limite de ~8191 tokens)
        max_chars = 30000  # Aproximadamente 8000 tokens
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "..."
        
        return full_text
    
    def _process_api_response(self, chunks: List[Chunk], data: Dict[str, Any], 
                             processing_time: float) -> List[EmbeddingResult]:
        """Processa resposta da API"""
        results = []
        embeddings_data = data.get('data', [])
        
        for i, chunk in enumerate(chunks):
            if i < len(embeddings_data):
                embedding = embeddings_data[i]['embedding']
                
                # Adiciona ao cache
                cache_key = self._get_cache_key(chunk.content)
                self.embedding_cache[cache_key] = embedding
                
                result = EmbeddingResult(
                    chunk_id=chunk.id,
                    embedding=embedding,
                    model=self.model,
                    dimensions=len(embedding),
                    created_at=datetime.now().isoformat(),
                    processing_time=processing_time / len(chunks)
                )
                results.append(result)
            else:
                # Embedding não encontrado
                result = EmbeddingResult(
                    chunk_id=chunk.id,
                    embedding=[],
                    model=self.model,
                    dimensions=0,
                    created_at=datetime.now().isoformat(),
                    processing_time=0.0,
                    error="Embedding não encontrado na resposta"
                )
                results.append(result)
        
        return results
    
    def _create_error_results(self, chunks: List[Chunk], error_msg: str) -> List[EmbeddingResult]:
        """Cria resultados de erro para chunks"""
        results = []
        for chunk in chunks:
            result = EmbeddingResult(
                chunk_id=chunk.id,
                embedding=[],
                model=self.model,
                dimensions=0,
                created_at=datetime.now().isoformat(),
                processing_time=0.0,
                error=error_msg
            )
            results.append(result)
        return results
    
    def _get_cache_key(self, text: str) -> str:
        """Gera chave de cache para texto"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    async def _wait_for_rate_limit(self):
        """Implementa rate limiting"""
        now = time.time()
        
        # Remove requests antigas (mais de 1 minuto)
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # Se estamos no limite, espera
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                self.logger.info(f"Rate limit atingido, aguardando {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
        
        # Adiciona request atual
        self.request_times.append(now)
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calcula similaridade coseno entre dois embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
        try:
            # Converte para numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calcula similaridade coseno
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular similaridade: {str(e)}")
            return 0.0
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do gerador de embeddings"""
        return {
            'total_requests': self.stats['total_requests'],
            'total_tokens': self.stats['total_tokens'],
            'cache_hits': self.stats['cache_hits'],
            'cache_size': len(self.embedding_cache),
            'errors': self.stats['errors'],
            'avg_processing_time': self.stats['avg_processing_time'],
            'model': self.model,
            'dimensions': self.dimensions
        }
    
    def clear_cache(self):
        """Limpa cache de embeddings"""
        self.embedding_cache.clear()
        self.logger.info("Cache de embeddings limpo")
    
    def save_cache(self, filepath: str):
        """Salva cache em arquivo"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.embedding_cache, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Cache salvo em {filepath}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar cache: {str(e)}")
    
    def load_cache(self, filepath: str):
        """Carrega cache de arquivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.embedding_cache = json.load(f)
            self.logger.info(f"Cache carregado de {filepath}: {len(self.embedding_cache)} entradas")
        except FileNotFoundError:
            self.logger.info(f"Arquivo de cache não encontrado: {filepath}")
        except Exception as e:
            self.logger.error(f"Erro ao carregar cache: {str(e)}")
    
    async def generate_single_embedding(self, text: str) -> Optional[List[float]]:
        """Gera embedding para um texto único"""
        # Verifica cache
        cache_key = self._get_cache_key(text)
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        # Cria chunk temporário
        temp_chunk = Chunk(
            id="temp",
            content=text,
            tokens=0,
            start_char=0,
            end_char=len(text),
            section_title="",
            section_type="general",
            metadata={}
        )
        
        # Gera embedding
        results = await self._call_embedding_api([temp_chunk])
        
        if results and not results[0].error:
            return results[0].embedding
        
        return None
    
    def batch_similarity_search(self, query_embedding: List[float], 
                               candidate_embeddings: List[List[float]], 
                               top_k: int = 10) -> List[Tuple[int, float]]:
        """Busca por similaridade em lote"""
        if not query_embedding or not candidate_embeddings:
            return []
        
        similarities = []
        
        for i, candidate in enumerate(candidate_embeddings):
            similarity = self.calculate_similarity(query_embedding, candidate)
            similarities.append((i, similarity))
        
        # Ordena por similaridade (maior primeiro)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]