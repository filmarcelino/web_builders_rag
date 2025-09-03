#!/usr/bin/env python3
"""
Vibe Content Collector - Coletor especializado para Vibe Creation Platform

Este módulo coleta conteúdo de:
1. Plataformas No-Code/Low-Code (Webflow, Bubble, Framer, etc.)
2. Documentação de IA Generativa (Leonardo AI, DALL-E, Kling AI, etc.)
3. Ferramentas de Design e Deploy (Figma, Vercel, Netlify)
4. Tutoriais de Visual Editing e Workflows modernos
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import tiktoken
from pathlib import Path

@dataclass
class VibeSource:
    """Representa uma fonte de conteúdo para a Vibe Creation Platform"""
    name: str
    category: str  # 'nocode', 'ai_generation', 'design_tools', 'deployment'
    base_url: str
    documentation_urls: List[str]
    api_docs_urls: List[str] = None
    tutorial_urls: List[str] = None
    priority: int = 1  # 1=alta, 2=média, 3=baixa
    rate_limit: float = 1.0  # segundos entre requests
    headers: Dict[str, str] = None
    content_selectors: Dict[str, str] = None
    vibe_relevance: float = 1.0  # 0.0-1.0, relevância para criação visual

class VibeContentCollector:
    """Coletor especializado para conteúdo da Vibe Creation Platform"""
    
    def __init__(self, output_dir: str = "collected_vibe_content"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuração de rate limiting
        self.session = None
        self.last_request_time = {}
        
        # Métricas de coleta
        self.collection_stats = {
            'sources_processed': 0,
            'pages_collected': 0,
            'total_tokens': 0,
            'errors': [],
            'start_time': None,
            'end_time': None
        }
        
        # Encoder para contagem de tokens
        self.encoder = tiktoken.get_encoding("cl100k_base")
        
        # Definir fontes especializadas
        self.vibe_sources = self._define_vibe_sources()
        
        # Estado de inicialização
        self.initialized = False
    
    async def initialize(self):
        """Inicializa o coletor de conteúdo"""
        if self.initialized:
            return
        
        # Configurar sessão HTTP
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'VibeCreationPlatform/1.0'}
        )
        
        # Configurar fontes de conteúdo
        await self._setup_vibe_sources()
        
        # Configurar tokenizer
        self.encoder = tiktoken.get_encoding("cl100k_base")
        
        self.initialized = True
        print(f"📚 Content Collector inicializado com {len(self.vibe_sources)} fontes")
    
    async def cleanup(self):
        """Limpa recursos"""
        if hasattr(self, 'session') and self.session:
            await self.session.close()
        self.initialized = False
    
    async def _setup_vibe_sources(self):
        """Configura as fontes de conteúdo da Vibe Platform"""
        # Verificar disponibilidade das fontes (simulado)
        # As fontes já estão definidas em self.vibe_sources
        print(f"✅ {len(self.vibe_sources)} fontes configuradas e prontas")
        
        # Log das categorias disponíveis
        categories = set(source.category for source in self.vibe_sources)
        print(f"📂 Categorias: {', '.join(categories)}")
    
    def _define_vibe_sources(self) -> List[VibeSource]:
        """Define as fontes especializadas para a Vibe Creation Platform"""
        return [
            # === PLATAFORMAS NO-CODE/LOW-CODE ===
            VibeSource(
                name="Webflow",
                category="nocode",
                base_url="https://webflow.com",
                documentation_urls=[
                    "https://university.webflow.com/",
                    "https://docs.webflow.com/",
                    "https://webflow.com/interactions-animations",
                    "https://webflow.com/ecommerce",
                    "https://webflow.com/cms"
                ],
                api_docs_urls=[
                    "https://developers.webflow.com/",
                    "https://developers.webflow.com/reference"
                ],
                tutorial_urls=[
                    "https://university.webflow.com/courses",
                    "https://webflow.com/blog/category/tutorials"
                ],
                priority=1,
                rate_limit=2.0,
                vibe_relevance=0.95,
                content_selectors={
                    'main_content': 'main, .main-content, .content, article',
                    'title': 'h1, .page-title, .article-title',
                    'description': '.description, .summary, .excerpt'
                }
            ),
            
            VibeSource(
                name="Bubble",
                category="nocode",
                base_url="https://bubble.io",
                documentation_urls=[
                    "https://manual.bubble.io/",
                    "https://bubble.io/academy",
                    "https://bubble.io/plugins"
                ],
                api_docs_urls=[
                    "https://manual.bubble.io/core-resources/api",
                    "https://manual.bubble.io/core-resources/bubble-made-plugins"
                ],
                priority=1,
                rate_limit=1.5,
                vibe_relevance=0.90,
                content_selectors={
                    'main_content': '.manual-content, .academy-content, main',
                    'title': 'h1, .manual-title',
                    'description': '.manual-description, .summary'
                }
            ),
            
            VibeSource(
                name="Framer",
                category="nocode",
                base_url="https://framer.com",
                documentation_urls=[
                    "https://www.framer.com/docs/",
                    "https://www.framer.com/motion/",
                    "https://www.framer.com/docs/components/"
                ],
                tutorial_urls=[
                    "https://www.framer.com/academy/",
                    "https://www.framer.com/blog/"
                ],
                priority=1,
                rate_limit=1.0,
                vibe_relevance=0.98,
                content_selectors={
                    'main_content': '.docs-content, main, article',
                    'title': 'h1, .docs-title',
                    'description': '.docs-description, .summary'
                }
            ),
            
            # === FERRAMENTAS DE IA GENERATIVA ===
            VibeSource(
                name="Leonardo AI",
                category="ai_generation",
                base_url="https://leonardo.ai",
                documentation_urls=[
                    "https://docs.leonardo.ai/",
                    "https://leonardo.ai/blog/"
                ],
                api_docs_urls=[
                    "https://docs.leonardo.ai/reference"
                ],
                priority=1,
                rate_limit=2.0,
                vibe_relevance=0.92,
                content_selectors={
                    'main_content': '.docs-content, main, article',
                    'title': 'h1, .docs-title',
                    'description': '.description, .summary'
                }
            ),
            
            VibeSource(
                name="OpenAI DALL-E",
                category="ai_generation",
                base_url="https://openai.com",
                documentation_urls=[
                    "https://platform.openai.com/docs/guides/images",
                    "https://openai.com/dall-e-3"
                ],
                api_docs_urls=[
                    "https://platform.openai.com/docs/api-reference/images"
                ],
                priority=1,
                rate_limit=1.0,
                vibe_relevance=0.88,
                content_selectors={
                    'main_content': '.docs-content, main, article',
                    'title': 'h1, .page-title',
                    'description': '.description, .summary'
                }
            ),
            
            VibeSource(
                name="Kling AI",
                category="ai_generation",
                base_url="https://klingai.com",
                documentation_urls=[
                    "https://klingai.com/docs/",
                    "https://klingai.com/blog/"
                ],
                priority=2,
                rate_limit=2.0,
                vibe_relevance=0.85,
                content_selectors={
                    'main_content': 'main, .content, article',
                    'title': 'h1, .title',
                    'description': '.description, .summary'
                }
            ),
            
            VibeSource(
                name="HeyGen",
                category="ai_generation",
                base_url="https://heygen.com",
                documentation_urls=[
                    "https://docs.heygen.com/",
                    "https://help.heygen.com/"
                ],
                api_docs_urls=[
                    "https://docs.heygen.com/reference"
                ],
                priority=2,
                rate_limit=1.5,
                vibe_relevance=0.80,
                content_selectors={
                    'main_content': '.docs-content, main',
                    'title': 'h1, .docs-title',
                    'description': '.description'
                }
            ),
            
            # === FERRAMENTAS DE DESIGN ===
            VibeSource(
                name="Figma",
                category="design_tools",
                base_url="https://figma.com",
                documentation_urls=[
                    "https://help.figma.com/",
                    "https://www.figma.com/developers/"
                ],
                api_docs_urls=[
                    "https://www.figma.com/developers/api",
                    "https://www.figma.com/plugin-docs/"
                ],
                priority=1,
                rate_limit=1.0,
                vibe_relevance=0.95,
                content_selectors={
                    'main_content': '.help-content, main, article',
                    'title': 'h1, .help-title',
                    'description': '.help-description, .summary'
                }
            ),
            
            # === FERRAMENTAS DE DEPLOYMENT ===
            VibeSource(
                name="Vercel",
                category="deployment",
                base_url="https://vercel.com",
                documentation_urls=[
                    "https://vercel.com/docs",
                    "https://vercel.com/guides"
                ],
                api_docs_urls=[
                    "https://vercel.com/docs/rest-api"
                ],
                priority=1,
                rate_limit=1.0,
                vibe_relevance=0.85,
                content_selectors={
                    'main_content': '.docs-content, main',
                    'title': 'h1, .docs-title',
                    'description': '.docs-description'
                }
            ),
            
            VibeSource(
                name="Netlify",
                category="deployment",
                base_url="https://netlify.com",
                documentation_urls=[
                    "https://docs.netlify.com/",
                    "https://www.netlify.com/blog/"
                ],
                api_docs_urls=[
                    "https://docs.netlify.com/api/get-started/"
                ],
                priority=2,
                rate_limit=1.0,
                vibe_relevance=0.80,
                content_selectors={
                    'main_content': '.docs-content, main',
                    'title': 'h1, .docs-title',
                    'description': '.docs-description'
                }
            )
        ]
    
    async def collect_all_sources(self) -> Dict:
        """Coleta conteúdo de todas as fontes definidas"""
        print("🎨 Iniciando coleta para Vibe Creation Platform...")
        self.collection_stats['start_time'] = datetime.now()
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'VibeCreationPlatform/1.0 (+https://github.com/vibe-platform)'}
        ) as session:
            self.session = session
            
            # Processar fontes por prioridade
            sources_by_priority = {}
            for source in self.vibe_sources:
                if source.priority not in sources_by_priority:
                    sources_by_priority[source.priority] = []
                sources_by_priority[source.priority].append(source)
            
            # Coletar por ordem de prioridade
            for priority in sorted(sources_by_priority.keys()):
                print(f"\n📋 Processando fontes de prioridade {priority}...")
                sources = sources_by_priority[priority]
                
                tasks = []
                for source in sources:
                    task = asyncio.create_task(self._collect_source(source))
                    tasks.append(task)
                
                # Executar em paralelo com limite
                semaphore = asyncio.Semaphore(3)  # Máximo 3 fontes simultâneas
                async def bounded_collect(task):
                    async with semaphore:
                        return await task
                
                results = await asyncio.gather(
                    *[bounded_collect(task) for task in tasks],
                    return_exceptions=True
                )
                
                # Processar resultados
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        error_msg = f"Erro ao processar {sources[i].name}: {str(result)}"
                        print(f"❌ {error_msg}")
                        self.collection_stats['errors'].append(error_msg)
                    else:
                        print(f"✅ {sources[i].name}: {result['pages_collected']} páginas coletadas")
        
        self.collection_stats['end_time'] = datetime.now()
        
        # Salvar metadados da coleta
        await self._save_collection_metadata()
        
        print(f"\n🎉 Coleta concluída!")
        print(f"📊 Fontes processadas: {self.collection_stats['sources_processed']}")
        print(f"📄 Páginas coletadas: {self.collection_stats['pages_collected']}")
        print(f"🔤 Total de tokens: {self.collection_stats['total_tokens']:,}")
        
        return self.collection_stats
    
    async def _collect_source(self, source: VibeSource) -> Dict:
        """Coleta conteúdo de uma fonte específica"""
        print(f"🔍 Coletando {source.name} ({source.category})...")
        
        source_stats = {
            'name': source.name,
            'category': source.category,
            'pages_collected': 0,
            'tokens_collected': 0,
            'errors': []
        }
        
        # Criar diretório para a fonte
        source_dir = self.output_dir / source.category / source.name.lower().replace(' ', '_')
        source_dir.mkdir(parents=True, exist_ok=True)
        
        # Coletar todas as URLs
        all_urls = []
        if source.documentation_urls:
            all_urls.extend(source.documentation_urls)
        if source.api_docs_urls:
            all_urls.extend(source.api_docs_urls)
        if source.tutorial_urls:
            all_urls.extend(source.tutorial_urls)
        
        # Processar cada URL
        for url in all_urls:
            try:
                await self._respect_rate_limit(source)
                content = await self._fetch_page_content(url, source)
                
                if content:
                    # Salvar conteúdo
                    filename = self._generate_filename(url)
                    file_path = source_dir / f"{filename}.json"
                    
                    # Contar tokens
                    token_count = len(self.encoder.encode(content['text']))
                    content['token_count'] = token_count
                    content['vibe_relevance'] = source.vibe_relevance
                    content['collection_timestamp'] = datetime.now().isoformat()
                    
                    # Salvar arquivo
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(content, f, indent=2, ensure_ascii=False)
                    
                    source_stats['pages_collected'] += 1
                    source_stats['tokens_collected'] += token_count
                    
                    print(f"  📄 {url} -> {token_count:,} tokens")
                
            except Exception as e:
                error_msg = f"Erro ao processar {url}: {str(e)}"
                source_stats['errors'].append(error_msg)
                print(f"  ❌ {error_msg}")
        
        # Atualizar estatísticas globais
        self.collection_stats['sources_processed'] += 1
        self.collection_stats['pages_collected'] += source_stats['pages_collected']
        self.collection_stats['total_tokens'] += source_stats['tokens_collected']
        
        # Salvar metadados da fonte
        metadata_path = source_dir / "source_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'source_info': asdict(source),
                'collection_stats': source_stats,
                'collection_timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        return source_stats
    
    async def _fetch_page_content(self, url: str, source: VibeSource) -> Optional[Dict]:
        """Busca e extrai conteúdo de uma página"""
        try:
            headers = source.headers or {}
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._extract_content(html, url, source)
                else:
                    print(f"  ⚠️ Status {response.status} para {url}")
                    return None
                    
        except Exception as e:
            print(f"  ❌ Erro ao buscar {url}: {str(e)}")
            return None
    
    def _extract_content(self, html: str, url: str, source: VibeSource) -> Dict:
        """Extrai conteúdo relevante do HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remover elementos desnecessários
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Extrair título
        title = ""
        if source.content_selectors and 'title' in source.content_selectors:
            title_elem = soup.select_one(source.content_selectors['title'])
            if title_elem:
                title = title_elem.get_text(strip=True)
        
        if not title:
            title_elem = soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)
        
        # Extrair conteúdo principal
        main_content = ""
        if source.content_selectors and 'main_content' in source.content_selectors:
            content_elem = soup.select_one(source.content_selectors['main_content'])
            if content_elem:
                main_content = content_elem.get_text(separator='\n', strip=True)
        
        if not main_content:
            # Fallback para body
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator='\n', strip=True)
        
        # Extrair descrição
        description = ""
        if source.content_selectors and 'description' in source.content_selectors:
            desc_elem = soup.select_one(source.content_selectors['description'])
            if desc_elem:
                description = desc_elem.get_text(strip=True)
        
        # Limpar texto
        text = f"{title}\n\n{description}\n\n{main_content}"
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        return {
            'url': url,
            'title': title,
            'description': description,
            'text': text,
            'source_name': source.name,
            'source_category': source.category,
            'vibe_relevance': source.vibe_relevance,
            'content_length': len(text)
        }
    
    async def _respect_rate_limit(self, source: VibeSource):
        """Respeita o rate limit da fonte"""
        now = time.time()
        last_request = self.last_request_time.get(source.name, 0)
        
        time_since_last = now - last_request
        if time_since_last < source.rate_limit:
            sleep_time = source.rate_limit - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time[source.name] = time.time()
    
    def _generate_filename(self, url: str) -> str:
        """Gera nome de arquivo baseado na URL"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path:
            return "index"
        
        # Limpar e truncar path
        filename = path.replace('/', '_').replace('-', '_')
        filename = ''.join(c for c in filename if c.isalnum() or c == '_')
        
        return filename[:50]  # Limitar tamanho
    
    def _json_serializer(self, obj):
        """Serializador personalizado para objetos datetime"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    async def _save_collection_metadata(self):
        """Salva metadados da coleta completa"""
        metadata = {
            'collection_stats': self.collection_stats,
            'sources_info': [asdict(source) for source in self.vibe_sources],
            'collection_timestamp': datetime.now().isoformat(),
            'platform_version': '1.0.0'
        }
        
        metadata_path = self.output_dir / "vibe_collection_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=self._json_serializer)
        
        print(f"💾 Metadados salvos em: {metadata_path}")

# Função principal para execução
async def main():
    """Função principal para coleta de conteúdo da Vibe Creation Platform"""
    collector = VibeContentCollector()
    
    try:
        stats = await collector.collect_all_sources()
        print("\n🎨 Coleta da Vibe Creation Platform concluída com sucesso!")
        return stats
    except Exception as e:
        print(f"❌ Erro durante a coleta: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())