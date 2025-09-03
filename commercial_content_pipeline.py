#!/usr/bin/env python3
"""
Pipeline de ingestão para conteúdo comercial.
Extende o sistema existente para processar documentação de ferramentas comerciais.
"""

import os
import json
import asyncio
import logging
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib
from datetime import datetime
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import markdown
import tiktoken

# Imports do sistema existente
from ingest_to_rag import RAGIngestor
from process_corpus import CorpusProcessor, DocumentChunk

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('commercial_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CommercialSource:
    """Representa uma fonte de conteúdo comercial."""
    name: str
    category: str  # 'web_builder', 'game_engine', 'ai_tool', etc.
    base_url: str
    documentation_urls: List[str]
    api_docs_urls: List[str]
    tutorial_urls: List[str]
    priority: str  # 'high', 'medium', 'low'
    rate_limit: float  # segundos entre requests
    headers: Dict[str, str]
    content_selectors: Dict[str, str]  # CSS selectors para extrair conteúdo

class CommercialContentCollector:
    """Coleta conteúdo de ferramentas comerciais."""
    
    def __init__(self, output_dir: str = "corpus/commercial_tools"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações de coleta
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Rate limiting
        self.last_request_time = {}
        
        # Tokenizer para contagem
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def get_commercial_sources(self) -> List[CommercialSource]:
        """Define as fontes de conteúdo comercial para coleta."""
        return [
            # Web Builders - Tier 1
            CommercialSource(
                name="webflow",
                category="web_builder",
                base_url="https://webflow.com",
                documentation_urls=[
                    "https://university.webflow.com/",
                    "https://developers.webflow.com/docs"
                ],
                api_docs_urls=[
                    "https://developers.webflow.com/reference"
                ],
                tutorial_urls=[
                    "https://university.webflow.com/courses"
                ],
                priority="high",
                rate_limit=2.0,
                headers={},
                content_selectors={
                    "main_content": ".main-content, .content, article",
                    "code_blocks": "pre, code",
                    "headings": "h1, h2, h3, h4"
                }
            ),
            
            CommercialSource(
                name="bubble",
                category="web_builder",
                base_url="https://bubble.io",
                documentation_urls=[
                    "https://manual.bubble.io/"
                ],
                api_docs_urls=[
                    "https://manual.bubble.io/core-resources/api"
                ],
                tutorial_urls=[
                    "https://manual.bubble.io/getting-started"
                ],
                priority="high",
                rate_limit=2.0,
                headers={},
                content_selectors={
                    "main_content": ".content, .main, article",
                    "code_blocks": "pre, code",
                    "headings": "h1, h2, h3, h4"
                }
            ),
            
            CommercialSource(
                name="framer",
                category="web_builder",
                base_url="https://framer.com",
                documentation_urls=[
                    "https://www.framer.com/developers/"
                ],
                api_docs_urls=[
                    "https://www.framer.com/developers/api/"
                ],
                tutorial_urls=[
                    "https://www.framer.com/academy/"
                ],
                priority="high",
                rate_limit=2.0,
                headers={},
                content_selectors={
                    "main_content": ".content, .main, article",
                    "code_blocks": "pre, code",
                    "headings": "h1, h2, h3, h4"
                }
            ),
            
            # Game Engines - Tier 1
            CommercialSource(
                name="unity",
                category="game_engine",
                base_url="https://unity.com",
                documentation_urls=[
                    "https://docs.unity3d.com/Manual/",
                    "https://learn.unity.com/"
                ],
                api_docs_urls=[
                    "https://docs.unity3d.com/ScriptReference/"
                ],
                tutorial_urls=[
                    "https://learn.unity.com/courses"
                ],
                priority="high",
                rate_limit=1.0,
                headers={},
                content_selectors={
                    "main_content": ".content, .main, article",
                    "code_blocks": "pre, code",
                    "headings": "h1, h2, h3, h4"
                }
            ),
            
            CommercialSource(
                name="godot",
                category="game_engine",
                base_url="https://godotengine.org",
                documentation_urls=[
                    "https://docs.godotengine.org/"
                ],
                api_docs_urls=[
                    "https://docs.godotengine.org/en/stable/classes/"
                ],
                tutorial_urls=[
                    "https://docs.godotengine.org/en/stable/getting_started/"
                ],
                priority="high",
                rate_limit=1.0,
                headers={},
                content_selectors={
                    "main_content": ".content, .main, article",
                    "code_blocks": "pre, code",
                    "headings": "h1, h2, h3, h4"
                }
            ),
            
            # AI Tools - Tier 1
            CommercialSource(
                name="cursor",
                category="ai_tool",
                base_url="https://cursor.sh",
                documentation_urls=[
                    "https://cursor.sh/docs"
                ],
                api_docs_urls=[],
                tutorial_urls=[
                    "https://cursor.sh/docs/getting-started"
                ],
                priority="high",
                rate_limit=2.0,
                headers={},
                content_selectors={
                    "main_content": ".content, .main, article",
                    "code_blocks": "pre, code",
                    "headings": "h1, h2, h3, h4"
                }
            ),
            
            # Backend Services - Tier 1
            CommercialSource(
                name="supabase",
                category="backend_service",
                base_url="https://supabase.com",
                documentation_urls=[
                    "https://supabase.com/docs"
                ],
                api_docs_urls=[
                    "https://supabase.com/docs/reference"
                ],
                tutorial_urls=[
                    "https://supabase.com/docs/guides"
                ],
                priority="high",
                rate_limit=1.0,
                headers={},
                content_selectors={
                    "main_content": ".content, .main, article",
                    "code_blocks": "pre, code",
                    "headings": "h1, h2, h3, h4"
                }
            ),
            
            CommercialSource(
                name="firebase",
                category="backend_service",
                base_url="https://firebase.google.com",
                documentation_urls=[
                    "https://firebase.google.com/docs"
                ],
                api_docs_urls=[
                    "https://firebase.google.com/docs/reference"
                ],
                tutorial_urls=[
                    "https://firebase.google.com/docs/guides"
                ],
                priority="high",
                rate_limit=1.0,
                headers={},
                content_selectors={
                    "main_content": ".content, .main, article",
                    "code_blocks": "pre, code",
                    "headings": "h1, h2, h3, h4"
                }
            )
        ]
    
    def respect_rate_limit(self, source_name: str, rate_limit: float):
        """Respeita o rate limit para uma fonte."""
        if source_name in self.last_request_time:
            elapsed = time.time() - self.last_request_time[source_name]
            if elapsed < rate_limit:
                sleep_time = rate_limit - elapsed
                logger.info(f"Rate limiting {source_name}: aguardando {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        self.last_request_time[source_name] = time.time()
    
    def fetch_page_content(self, url: str, source: CommercialSource) -> Optional[str]:
        """Faz download do conteúdo de uma página."""
        try:
            self.respect_rate_limit(source.name, source.rate_limit)
            
            headers = {**self.session.headers, **source.headers}
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Erro ao fazer download de {url}: {e}")
            return None
    
    def extract_content_from_html(self, html: str, source: CommercialSource) -> Dict[str, str]:
        """Extrai conteúdo estruturado do HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remover elementos desnecessários
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        extracted = {
            'title': '',
            'main_content': '',
            'code_blocks': [],
            'headings': []
        }
        
        # Extrair título
        title_tag = soup.find('title')
        if title_tag:
            extracted['title'] = title_tag.get_text().strip()
        
        # Extrair conteúdo principal
        main_selector = source.content_selectors.get('main_content', '.content')
        main_content = soup.select_one(main_selector)
        if main_content:
            extracted['main_content'] = main_content.get_text().strip()
        else:
            # Fallback para body
            body = soup.find('body')
            if body:
                extracted['main_content'] = body.get_text().strip()
        
        # Extrair blocos de código
        code_selector = source.content_selectors.get('code_blocks', 'pre, code')
        code_blocks = soup.select(code_selector)
        extracted['code_blocks'] = [block.get_text().strip() for block in code_blocks]
        
        # Extrair headings
        heading_selector = source.content_selectors.get('headings', 'h1, h2, h3, h4')
        headings = soup.select(heading_selector)
        extracted['headings'] = [h.get_text().strip() for h in headings]
        
        return extracted
    
    def collect_source_content(self, source: CommercialSource) -> List[Dict]:
        """Coleta todo o conteúdo de uma fonte comercial."""
        logger.info(f"Coletando conteúdo de {source.name} ({source.category})")
        
        collected_content = []
        all_urls = source.documentation_urls + source.api_docs_urls + source.tutorial_urls
        
        for url in all_urls:
            logger.info(f"Processando: {url}")
            
            html_content = self.fetch_page_content(url, source)
            if not html_content:
                continue
            
            extracted = self.extract_content_from_html(html_content, source)
            
            if extracted['main_content']:
                # Calcular tokens
                token_count = len(self.tokenizer.encode(extracted['main_content']))
                
                content_item = {
                    'source_name': source.name,
                    'category': source.category,
                    'url': url,
                    'title': extracted['title'],
                    'content': extracted['main_content'],
                    'code_blocks': extracted['code_blocks'],
                    'headings': extracted['headings'],
                    'token_count': token_count,
                    'collected_at': datetime.now().isoformat(),
                    'priority': source.priority
                }
                
                collected_content.append(content_item)
                logger.info(f"Coletado: {extracted['title'][:50]}... ({token_count} tokens)")
        
        return collected_content
    
    def save_collected_content(self, source_name: str, content: List[Dict]):
        """Salva conteúdo coletado em arquivos."""
        if not content:
            return
        
        # Criar diretório para a fonte
        source_dir = self.output_dir / source_name
        source_dir.mkdir(exist_ok=True)
        
        # Salvar conteúdo raw
        raw_file = source_dir / "raw_content.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        
        # Salvar metadados
        metadata = {
            'source_name': source_name,
            'total_items': len(content),
            'total_tokens': sum(item['token_count'] for item in content),
            'collected_at': datetime.now().isoformat(),
            'urls_processed': list(set(item['url'] for item in content))
        }
        
        metadata_file = source_dir / "collection_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Salvos {len(content)} itens para {source_name} ({metadata['total_tokens']} tokens)")

class CommercialContentProcessor(CorpusProcessor):
    """Processa conteúdo comercial coletado em chunks para RAG."""
    
    def __init__(self, 
                 commercial_dir: str = "corpus/commercial_tools",
                 output_dir: str = "processed_corpus/commercial"):
        
        # Inicializar classe pai com configurações específicas
        super().__init__(corpus_dir=commercial_dir, output_dir=output_dir)
        
        # Configurações específicas para conteúdo comercial
        self.max_chunk_size = 800  # Chunks maiores para documentação técnica
        self.chunk_overlap = 150   # Overlap maior para manter contexto
    
    def process_commercial_content(self) -> Dict:
        """Processa todo o conteúdo comercial coletado."""
        logger.info("Iniciando processamento de conteúdo comercial...")
        
        all_chunks = []
        processing_stats = {
            'sources_processed': 0,
            'total_chunks': 0,
            'total_tokens': 0,
            'categories': {}
        }
        
        # Processar cada fonte
        for source_dir in self.corpus_dir.iterdir():
            if not source_dir.is_dir():
                continue
            
            raw_file = source_dir / "raw_content.json"
            if not raw_file.exists():
                continue
            
            logger.info(f"Processando fonte: {source_dir.name}")
            
            # Carregar conteúdo raw
            with open(raw_file, 'r', encoding='utf-8') as f:
                raw_content = json.load(f)
            
            # Processar em chunks
            source_chunks = self._process_source_content(source_dir.name, raw_content)
            all_chunks.extend(source_chunks)
            
            # Atualizar estatísticas
            processing_stats['sources_processed'] += 1
            processing_stats['total_chunks'] += len(source_chunks)
            
            # Estatísticas por categoria
            for item in raw_content:
                category = item.get('category', 'unknown')
                if category not in processing_stats['categories']:
                    processing_stats['categories'][category] = 0
                processing_stats['categories'][category] += 1
        
        # Salvar chunks processados
        self._save_commercial_chunks(all_chunks)
        
        processing_stats['total_tokens'] = sum(chunk.token_count for chunk in all_chunks)
        
        logger.info(f"Processamento concluído: {len(all_chunks)} chunks de {processing_stats['sources_processed']} fontes")
        
        return processing_stats
    
    def _process_source_content(self, source_name: str, raw_content: List[Dict]) -> List[DocumentChunk]:
        """Processa conteúdo de uma fonte específica."""
        chunks = []
        
        for item in raw_content:
            content = item['content']
            if len(content.strip()) < 100:  # Ignorar conteúdo muito pequeno
                continue
            
            # Criar chunks do conteúdo
            item_chunks = self._create_commercial_chunks(
                content=content,
                source_name=source_name,
                metadata=item
            )
            
            chunks.extend(item_chunks)
        
        return chunks
    
    def _create_commercial_chunks(self, content: str, source_name: str, metadata: Dict) -> List[DocumentChunk]:
        """Cria chunks específicos para conteúdo comercial."""
        chunks = []
        
        # Tokenizar o conteúdo
        tokens = self.tokenizer.encode(content)
        
        # Dividir em chunks com overlap
        for i in range(0, len(tokens), self.max_chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.max_chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            if len(chunk_text.strip()) < 50:
                continue
            
            # Criar ID único
            chunk_id = hashlib.md5(f"{source_name}_{metadata['url']}_{i}".encode()).hexdigest()[:12]
            
            chunk = DocumentChunk(
                id=f"comm_{chunk_id}",
                source_file=metadata['url'],
                source_type='commercial_documentation',
                title=metadata.get('title', f"{source_name} Documentation"),
                content=chunk_text,
                metadata={
                    'source_name': source_name,
                    'category': metadata['category'],
                    'url': metadata['url'],
                    'priority': metadata['priority'],
                    'collected_at': metadata['collected_at'],
                    'commercial_tool': True
                },
                token_count=len(chunk_tokens),
                chunk_index=len(chunks),
                total_chunks=0  # Será atualizado depois
            )
            
            chunks.append(chunk)
        
        # Atualizar total_chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        return chunks
    
    def _save_commercial_chunks(self, chunks: List[DocumentChunk]):
        """Salva chunks comerciais processados."""
        logger.info(f"Salvando {len(chunks)} chunks comerciais...")
        
        # Converter para formato JSON
        chunks_data = []
        for chunk in chunks:
            chunk_dict = {
                'id': chunk.id,
                'source_file': chunk.source_file,
                'source_type': chunk.source_type,
                'title': chunk.title,
                'content': chunk.content,
                'metadata': chunk.metadata,
                'token_count': chunk.token_count,
                'chunk_index': chunk.chunk_index,
                'total_chunks': chunk.total_chunks
            }
            chunks_data.append(chunk_dict)
        
        # Salvar em batches
        batch_size = 1000
        for i in range(0, len(chunks_data), batch_size):
            batch = chunks_data[i:i + batch_size]
            batch_num = i // batch_size
            
            batch_file = self.output_dir / f"commercial_chunks_batch_{batch_num:04d}.json"
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(batch, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Batch {batch_num} salvo: {len(batch)} chunks")
        
        # Salvar metadados de processamento
        metadata = {
            'total_chunks': len(chunks),
            'processing_date': datetime.now().isoformat(),
            'chunk_size': self.max_chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'sources': list(set(chunk.metadata['source_name'] for chunk in chunks)),
            'categories': list(set(chunk.metadata['category'] for chunk in chunks))
        }
        
        metadata_file = self.output_dir / "commercial_processing_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

class CommercialRAGPipeline:
    """Pipeline completo para ingestão de conteúdo comercial no RAG."""
    
    def __init__(self):
        self.collector = CommercialContentCollector()
        self.processor = CommercialContentProcessor()
        self.ingestor = RAGIngestor(
            processed_corpus_dir="processed_corpus",
            rag_data_dir="rag_data"
        )
    
    async def run_full_pipeline(self, sources_to_collect: Optional[List[str]] = None):
        """Executa o pipeline completo de coleta, processamento e ingestão."""
        logger.info("=== INICIANDO PIPELINE COMERCIAL COMPLETO ===")
        
        # 1. Coleta de conteúdo
        logger.info("Fase 1: Coleta de conteúdo")
        await self.collect_commercial_content(sources_to_collect)
        
        # 2. Processamento
        logger.info("Fase 2: Processamento de conteúdo")
        processing_stats = self.processor.process_commercial_content()
        
        # 3. Ingestão no RAG
        logger.info("Fase 3: Ingestão no RAG")
        await self.ingestor.run_ingestion()
        
        logger.info("=== PIPELINE COMERCIAL CONCLUÍDO ===")
        return processing_stats
    
    async def collect_commercial_content(self, sources_to_collect: Optional[List[str]] = None):
        """Coleta conteúdo de fontes comerciais."""
        sources = self.collector.get_commercial_sources()
        
        if sources_to_collect:
            sources = [s for s in sources if s.name in sources_to_collect]
        
        for source in sources:
            if source.priority == 'high':  # Processar apenas alta prioridade por enquanto
                content = self.collector.collect_source_content(source)
                self.collector.save_collected_content(source.name, content)
    
    async def test_commercial_rag(self, queries: List[str]) -> Dict:
        """Testa o RAG com queries específicas de ferramentas comerciais."""
        logger.info("Testando capacidades comerciais do RAG...")
        
        results = {}
        
        for query in queries:
            logger.info(f"Testando query: {query}")
            
            search_results = self.ingestor.test_search(query, top_k=5)
            
            # Analisar resultados
            commercial_chunks = 0
            sources_found = set()
            
            for result in search_results:
                metadata = result.get('metadata', {})
                if metadata.get('commercial_tool', False):
                    commercial_chunks += 1
                    sources_found.add(metadata.get('source_name', 'unknown'))
            
            results[query] = {
                'total_results': len(search_results),
                'commercial_chunks': commercial_chunks,
                'commercial_sources': list(sources_found),
                'commercial_percentage': (commercial_chunks / len(search_results)) * 100 if search_results else 0
            }
        
        return results

# Função principal para execução
async def main():
    """Função principal para testar o pipeline."""
    pipeline = CommercialRAGPipeline()
    
    # Testar com algumas fontes primeiro
    test_sources = ['webflow', 'supabase', 'godot']
    
    try:
        # Executar pipeline
        stats = await pipeline.run_full_pipeline(test_sources)
        
        print("\n=== ESTATÍSTICAS DE PROCESSAMENTO ===")
        print(f"Fontes processadas: {stats['sources_processed']}")
        print(f"Total de chunks: {stats['total_chunks']}")
        print(f"Total de tokens: {stats['total_tokens']}")
        print(f"Categorias: {stats['categories']}")
        
        # Testar capacidades
        test_queries = [
            "Como criar um componente no Webflow?",
            "Como configurar autenticação no Supabase?",
            "Como criar um script em GDScript no Godot?",
            "Como fazer deploy de uma aplicação web?"
        ]
        
        test_results = await pipeline.test_commercial_rag(test_queries)
        
        print("\n=== RESULTADOS DOS TESTES ===")
        for query, result in test_results.items():
            print(f"\nQuery: {query}")
            print(f"  - Resultados totais: {result['total_results']}")
            print(f"  - Chunks comerciais: {result['commercial_chunks']} ({result['commercial_percentage']:.1f}%)")
            print(f"  - Fontes encontradas: {result['commercial_sources']}")
        
    except Exception as e:
        logger.error(f"Erro no pipeline: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())