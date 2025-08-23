import os
import requests
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import RAGConfig

@dataclass
class SourceInfo:
    """Informações sobre uma fonte de dados"""
    url: str
    source_type: str  # 'documentation', 'repository', 'example'
    stack: str
    category: str
    license: str
    priority: int = 1  # 1=high, 2=medium, 3=low
    last_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = None

class SourceCollector:
    """Coletor de fontes aprovadas para o sistema RAG"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.collected_sources = []
        
    async def __aenter__(self):
        """Context manager para sessão async"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup da sessão"""
        if self.session:
            await self.session.close()
    
    def get_seed_sources(self) -> List[SourceInfo]:
        """Retorna lista de fontes seed iniciais"""
        return [
            # Shadcn/UI Documentation
            SourceInfo(
                url="https://ui.shadcn.com/docs",
                source_type="documentation",
                stack="shadcn",
                category="ui_design",
                license="MIT",
                priority=1
            ),
            
            # Radix UI Documentation
            SourceInfo(
                url="https://www.radix-ui.com/primitives/docs",
                source_type="documentation",
                stack="radix",
                category="ui_design",
                license="MIT",
                priority=1
            ),
            
            # Next.js Documentation
            SourceInfo(
                url="https://nextjs.org/docs",
                source_type="documentation",
                stack="nextjs",
                category="web_stack",
                license="MIT",
                priority=1
            ),
            
            # React Documentation
            SourceInfo(
                url="https://react.dev/learn",
                source_type="documentation",
                stack="react",
                category="web_stack",
                license="MIT",
                priority=1
            ),
            
            # Tailwind CSS Documentation
            SourceInfo(
                url="https://tailwindcss.com/docs",
                source_type="documentation",
                stack="tailwind",
                category="web_stack",
                license="MIT",
                priority=1
            ),
            
            # Prisma Documentation
            SourceInfo(
                url="https://www.prisma.io/docs",
                source_type="documentation",
                stack="prisma",
                category="database",
                license="Apache-2.0",
                priority=1
            ),
            
            # NextAuth.js Documentation
            SourceInfo(
                url="https://next-auth.js.org/getting-started/introduction",
                source_type="documentation",
                stack="nextjs",
                category="auth",
                license="ISC",
                priority=2
            )
        ]
    
    async def collect_source(self, source: SourceInfo) -> Dict[str, Any]:
        """Coleta conteúdo de uma fonte específica"""
        try:
            self.logger.info(f"Coletando fonte: {source.url}")
            
            if source.source_type == "documentation":
                content = await self._collect_documentation(source)
            elif source.source_type == "repository":
                content = await self._collect_repository(source)
            elif source.source_type == "example":
                content = await self._collect_example(source)
            else:
                raise ValueError(f"Tipo de fonte não suportado: {source.source_type}")
            
            # Adiciona metadados obrigatórios
            content["metadata"] = {
                "source_url": source.url,
                "license": source.license,
                "updated_at": datetime.now().isoformat(),
                "stack": source.stack,
                "category": source.category,
                "language": "pt-br",  # Detectar automaticamente
                "maturity": self._assess_maturity(source),
                "quality_score": 0.0,  # Será calculado posteriormente
                "source_type": source.source_type,
                "priority": source.priority
            }
            
            return content
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar {source.url}: {str(e)}")
            return None
    
    async def _collect_documentation(self, source: SourceInfo) -> Dict[str, Any]:
        """Coleta documentação de uma URL"""
        async with self.session.get(source.url) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status} para {source.url}")
            
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove elementos de navegação e ruído
            for element in soup.find_all(['nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Extrai conteúdo principal
            main_content = soup.find('main') or soup.find('article') or soup.body
            
            if not main_content:
                raise Exception("Não foi possível encontrar conteúdo principal")
            
            # Extrai seções específicas
            sections = self._extract_sections(main_content)
            
            return {
                "title": soup.title.string if soup.title else "Sem título",
                "url": source.url,
                "content_type": "documentation",
                "sections": sections,
                "raw_html": str(main_content),
                "collected_at": datetime.now().isoformat()
            }
    
    async def _collect_repository(self, source: SourceInfo) -> Dict[str, Any]:
        """Coleta conteúdo de repositório GitHub"""
        # Implementar coleta via GitHub API
        # Por enquanto, placeholder
        return {
            "title": f"Repository: {source.url}",
            "url": source.url,
            "content_type": "repository",
            "sections": [],
            "collected_at": datetime.now().isoformat()
        }
    
    async def _collect_example(self, source: SourceInfo) -> Dict[str, Any]:
        """Coleta exemplos de código"""
        # Implementar coleta de exemplos
        # Por enquanto, placeholder
        return {
            "title": f"Example: {source.url}",
            "url": source.url,
            "content_type": "example",
            "sections": [],
            "collected_at": datetime.now().isoformat()
        }
    
    def _extract_sections(self, content) -> List[Dict[str, Any]]:
        """Extrai seções úteis do conteúdo"""
        sections = []
        
        # Procura por seções específicas
        target_sections = [
            'usage', 'props', 'accessibility', 'examples', 
            'api', 'installation', 'configuration', 'gotchas'
        ]
        
        for heading in content.find_all(['h1', 'h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower().strip()
            
            # Verifica se é uma seção de interesse
            section_type = None
            for target in target_sections:
                if target in heading_text:
                    section_type = target
                    break
            
            if section_type:
                # Coleta conteúdo até próximo heading do mesmo nível
                section_content = self._get_section_content(heading)
                
                sections.append({
                    "type": section_type,
                    "title": heading.get_text().strip(),
                    "content": section_content,
                    "level": int(heading.name[1])  # h1=1, h2=2, etc.
                })
        
        return sections
    
    def _get_section_content(self, heading) -> str:
        """Extrai conteúdo de uma seção até o próximo heading"""
        content_parts = []
        current = heading.next_sibling
        
        while current:
            if current.name and current.name.startswith('h'):
                # Parou em outro heading
                break
            
            if hasattr(current, 'get_text'):
                text = current.get_text().strip()
                if text:
                    content_parts.append(text)
            
            current = current.next_sibling
        
        return '\n'.join(content_parts)
    
    def _assess_maturity(self, source: SourceInfo) -> str:
        """Avalia maturidade da fonte"""
        # Lógica simples baseada na prioridade e stack
        if source.priority == 1 and source.stack in ['react', 'nextjs', 'tailwind']:
            return 'stable'
        elif source.priority <= 2:
            return 'beta'
        else:
            return 'alpha'
    
    async def collect_all_seeds(self) -> List[Dict[str, Any]]:
        """Coleta todas as fontes seed"""
        seed_sources = self.get_seed_sources()
        collected = []
        
        for source in seed_sources:
            content = await self.collect_source(source)
            if content:
                collected.append(content)
                
                # Salva conteúdo bruto
                await self._save_raw_content(content)
        
        self.collected_sources = collected
        return collected
    
    async def _save_raw_content(self, content: Dict[str, Any]):
        """Salva conteúdo bruto no diretório data/raw"""
        try:
            # Cria nome de arquivo baseado na URL
            url_parts = urlparse(content["url"])
            filename = f"{url_parts.netloc}_{url_parts.path.replace('/', '_')}.json"
            filename = filename.replace('__', '_').strip('_')
            
            filepath = os.path.join(RAGConfig.RAW_DATA_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Conteúdo salvo em: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar conteúdo: {str(e)}")