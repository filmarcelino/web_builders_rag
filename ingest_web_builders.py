#!/usr/bin/env python3
"""
Script para ingerir dados sobre Web App Builders no sistema RAG
Utiliza o arquivo inject_rag.json como fonte de dados
"""

import os
import sys
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Imports do sistema RAG
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from config.config import RAGConfig
from indexing.chunker import ContentChunker
from indexing.embeddings import EmbeddingGenerator
from indexing.index_manager import IndexManager
from ingestion.collector import SourceCollector
import aiohttp
import requests
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebBuilderIngestor:
    """Ingestor especializado para dados de Web App Builders"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Obter API key do ambiente
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        
        # Inicializar componentes do RAG
        self.chunker = ContentChunker()
        self.embedding_generator = EmbeddingGenerator(api_key)
        self.index_manager = IndexManager(api_key)
        
        # Diretório de dados
        self.data_path = Path("rag_data")
        self.data_path.mkdir(exist_ok=True)
        
        # Estatísticas
        self.stats = {
            "total_sources": 0,
            "processed_sources": 0,
            "failed_sources": 0,
            "total_chunks": 0,
            "start_time": datetime.now().isoformat()
        }
    
    async def fetch_content(self, session: aiohttp.ClientSession, source: Dict[str, Any]) -> str:
        """Buscar conteúdo de uma fonte"""
        try:
            url = source["url"]
            fetch_type = source.get("fetch", "http")
            
            if fetch_type == "http":
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"✅ Fetched: {source['title']}")
                        return content
                    else:
                        logger.warning(f"❌ HTTP {response.status}: {source['title']}")
                        return ""
            
            elif fetch_type == "git":
                # Para repositórios Git, usar apenas README por enquanto
                readme_url = url.replace("github.com", "raw.githubusercontent.com") + "/main/README.md"
                try:
                    async with session.get(readme_url, timeout=30) as response:
                        if response.status == 200:
                            content = await response.text()
                            logger.info(f"✅ Fetched README: {source['title']}")
                            return content
                except:
                    pass
                
                # Fallback para página do GitHub
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"✅ Fetched GitHub page: {source['title']}")
                        return content
            
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error fetching {source['title']}: {str(e)}")
            return ""
    
    def clean_content(self, content: str, source: Dict[str, Any]) -> str:
        """Limpar e preparar conteúdo para ingestão"""
        if not content:
            return ""
        
        # Remover HTML tags se necessário
        if source.get("format_hint") == "html":
            import re
            # Remover scripts e styles
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            # Remover tags HTML básicas
            content = re.sub(r'<[^>]+>', ' ', content)
            # Limpar espaços extras
            content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def create_metadata(self, source: Dict[str, Any], chunk_index: int) -> Dict[str, Any]:
        """Criar metadata para um chunk"""
        return {
            "source_title": source["title"],
            "source_url": source["url"],
            "source_type": source["type"],
            "tags": source.get("tags", []),
            "priority": source.get("priority", "medium"),
            "license": source.get("license", "unknown"),
            "notes": source.get("notes", ""),
            "chunk_index": chunk_index,
            "ingestion_date": datetime.now().isoformat(),
            "category": "web_app_builders"
        }
    
    async def process_source(self, session: aiohttp.ClientSession, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processar uma fonte individual"""
        try:
            # Buscar conteúdo
            raw_content = await self.fetch_content(session, source)
            if not raw_content:
                self.stats["failed_sources"] += 1
                return []
            
            # Limpar conteúdo
            clean_content = self.clean_content(raw_content, source)
            if not clean_content or len(clean_content) < 100:
                logger.warning(f"⚠️ Content too short: {source['title']}")
                self.stats["failed_sources"] += 1
                return []
            
            # Prepara conteúdo estruturado para chunking
            content_data = {
                'title': source['title'],
                'metadata': {
                    'source_title': source['title'],
                    'source_url': source['url'],
                    'source_type': source['type'],
                    'tags': source.get('tags', []),
                    'priority': source.get('priority', 'medium'),
                    'ingestion_date': datetime.now().isoformat()
                },
                'sections': [{
                    'title': source['title'],
                    'content': clean_content,
                    'section_type': 'main',
                    'importance_score': 0.8
                }]
            }
            
            # Chunka o conteúdo
            chunks = self.chunker.chunk_content(content_data)
            
            # Converte chunks para formato estruturado
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                    "source_id": source["url"],
                    "chunk_id": chunk.id or f"{source['url']}#{i}"
                }
                processed_chunks.append(chunk_data)
            
            self.stats["processed_sources"] += 1
            self.stats["total_chunks"] += len(processed_chunks)
            
            logger.info(f"✅ Processed {len(processed_chunks)} chunks from: {source['title']}")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"❌ Error processing {source['title']}: {str(e)}")
            self.stats["failed_sources"] += 1
            return []
    
    async def ingest_sources(self, sources: List[Dict[str, Any]]) -> None:
        """Ingerir todas as fontes"""
        self.stats["total_sources"] = len(sources)
        
        # Filtrar por prioridade (high primeiro)
        high_priority = [s for s in sources if s.get("priority") == "high"]
        medium_priority = [s for s in sources if s.get("priority") == "medium"]
        low_priority = [s for s in sources if s.get("priority") == "low"]
        
        ordered_sources = high_priority + medium_priority + low_priority
        
        logger.info(f"🚀 Starting ingestion of {len(ordered_sources)} sources...")
        logger.info(f"📊 Priority breakdown: High={len(high_priority)}, Medium={len(medium_priority)}, Low={len(low_priority)}")
        
        all_chunks = []
        
        async with aiohttp.ClientSession() as session:
            # Processar em lotes para evitar sobrecarga
            batch_size = 5
            for i in range(0, len(ordered_sources), batch_size):
                batch = ordered_sources[i:i + batch_size]
                logger.info(f"📦 Processing batch {i//batch_size + 1}/{(len(ordered_sources) + batch_size - 1)//batch_size}")
                
                # Processar lote
                tasks = [self.process_source(session, source) for source in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Coletar chunks válidos
                for result in batch_results:
                    if isinstance(result, list):
                        all_chunks.extend(result)
                
                # Pequena pausa entre lotes
                await asyncio.sleep(1)
        
        # Indexar todos os chunks
        if all_chunks:
            logger.info(f"📚 Indexing {len(all_chunks)} chunks...")
            await self.index_chunks(all_chunks)
        
        # Salvar estatísticas
        self.stats["end_time"] = datetime.now().isoformat()
        stats_file = self.data_path / "web_builders_ingestion_stats.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Ingestion completed!")
        logger.info(f"📊 Stats: {self.stats['processed_sources']}/{self.stats['total_sources']} sources, {self.stats['total_chunks']} chunks")
    
    async def index_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Indexar chunks no sistema RAG"""
        try:
            # Preparar dados para indexação
            texts = [chunk["content"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            # Gerar embeddings
            logger.info("🔄 Generating embeddings...")
            embeddings = await self.embedding_generator.generate_embeddings(texts)
            
            # Indexar no vector store
            logger.info("🔄 Indexing vectors...")
            self.vector_indexer.add_vectors(embeddings, metadatas)
            
            # Indexar no text store
            logger.info("🔄 Indexing text...")
            for chunk in chunks:
                self.text_indexer.add_document(
                    doc_id=chunk["chunk_id"],
                    content=chunk["content"],
                    metadata=chunk["metadata"]
                )
            
            # Salvar índices
            logger.info("💾 Saving indices...")
            self.vector_indexer.save_index()
            self.text_indexer.save_index()
            
            logger.info("✅ Indexing completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error during indexing: {str(e)}")
            raise

async def main():
    """Função principal"""
    # Carregar dados do inject_rag.json
    inject_file = Path("inject_rag.json")
    if not inject_file.exists():
        logger.error(f"❌ File not found: {inject_file}")
        return
    
    with open(inject_file, "r", encoding="utf-8") as f:
        sources = json.load(f)
    
    logger.info(f"📋 Loaded {len(sources)} sources from {inject_file}")
    
    # Criar ingestor e processar
    ingestor = WebBuilderIngestor()
    await ingestor.ingest_sources(sources)
    
    logger.info("🎉 Web App Builders data ingestion completed!")

if __name__ == "__main__":
    asyncio.run(main())