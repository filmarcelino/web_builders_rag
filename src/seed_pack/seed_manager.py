#!/usr/bin/env python3
"""
Seed Manager - Gerenciador de Fontes Prioritárias

Este módulo gerencia as fontes curadas e prioritárias para desenvolvimento,
organizando-as por categoria e fornecendo acesso estruturado às informações.
"""

import json
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class SeedCategory(Enum):
    """Categorias de fontes do Seed Pack"""
    UI_DESIGN = "ui_design"
    WEB_STACK = "web_stack"
    RECURRING_MODULES = "recurring_modules"
    BOILERPLATES = "boilerplates"
    PATTERNS_FIXES = "patterns_fixes"
    ANIMATIONS = "animations"

@dataclass
class SeedSource:
    """Representa uma fonte prioritária do Seed Pack"""
    name: str
    category: SeedCategory
    url: str
    description: str
    license: str
    priority: int  # 1-5, sendo 1 mais prioritário
    tags: List[str]
    documentation_url: Optional[str] = None
    github_url: Optional[str] = None
    examples_url: Optional[str] = None
    installation_guide: Optional[str] = None
    common_patterns: List[str] = None
    known_issues: List[str] = None
    alternatives: List[str] = None
    last_updated: Optional[str] = None
    
    def __post_init__(self):
        if self.common_patterns is None:
            self.common_patterns = []
        if self.known_issues is None:
            self.known_issues = []
        if self.alternatives is None:
            self.alternatives = []
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()

class SeedManager:
    """Gerenciador das fontes prioritárias do Seed Pack"""
    
    def __init__(self, data_dir: str = "data/seed_pack"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.sources: Dict[str, SeedSource] = {}
        self.categories: Dict[SeedCategory, List[SeedSource]] = {
            category: [] for category in SeedCategory
        }
        
        self._load_sources()
    
    def add_source(self, source: SeedSource) -> None:
        """Adiciona uma nova fonte ao Seed Pack"""
        try:
            self.sources[source.name] = source
            self.categories[source.category].append(source)
            
            # Ordena por prioridade
            self.categories[source.category].sort(key=lambda x: x.priority)
            
            logger.info(f"Fonte adicionada: {source.name} ({source.category.value})")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar fonte {source.name}: {e}")
            raise
    
    def get_source(self, name: str) -> Optional[SeedSource]:
        """Obtém uma fonte específica pelo nome"""
        return self.sources.get(name)
    
    def get_sources_by_category(self, category: SeedCategory) -> List[SeedSource]:
        """Obtém todas as fontes de uma categoria específica"""
        return self.categories.get(category, [])
    
    def get_sources_by_tags(self, tags: List[str]) -> List[SeedSource]:
        """Obtém fontes que contêm pelo menos uma das tags especificadas"""
        matching_sources = []
        tag_set = set(tags)
        
        for source in self.sources.values():
            source_tags = set(source.tags)
            if tag_set.intersection(source_tags):
                matching_sources.append(source)
        
        # Ordena por prioridade
        matching_sources.sort(key=lambda x: x.priority)
        return matching_sources
    
    def get_priority_sources(self, max_priority: int = 2) -> List[SeedSource]:
        """Obtém fontes de alta prioridade"""
        priority_sources = [
            source for source in self.sources.values()
            if source.priority <= max_priority
        ]
        
        priority_sources.sort(key=lambda x: x.priority)
        return priority_sources
    
    def search_sources(self, query: str) -> List[SeedSource]:
        """Busca fontes por termo de pesquisa"""
        query_lower = query.lower()
        matching_sources = []
        
        for source in self.sources.values():
            # Busca no nome, descrição e tags
            if (query_lower in source.name.lower() or
                query_lower in source.description.lower() or
                any(query_lower in tag.lower() for tag in source.tags)):
                matching_sources.append(source)
        
        matching_sources.sort(key=lambda x: x.priority)
        return matching_sources
    
    def get_category_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas das categorias"""
        stats = {}
        
        for category in SeedCategory:
            sources = self.categories[category]
            stats[category.value] = {
                "total_sources": len(sources),
                "priority_1": len([s for s in sources if s.priority == 1]),
                "priority_2": len([s for s in sources if s.priority == 2]),
                "priority_3_plus": len([s for s in sources if s.priority >= 3]),
                "most_recent": max([s.last_updated for s in sources]) if sources else None
            }
        
        return stats
    
    def export_sources(self, filepath: Optional[str] = None) -> str:
        """Exporta todas as fontes para JSON"""
        if filepath is None:
            filepath = self.data_dir / "seed_sources_export.json"
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_sources": len(self.sources),
            "categories": {},
            "sources": {}
        }
        
        # Exporta por categoria
        for category in SeedCategory:
            sources = self.categories[category]
            export_data["categories"][category.value] = [
                asdict(source) for source in sources
            ]
        
        # Exporta todas as fontes
        for name, source in self.sources.items():
            export_data["sources"][name] = asdict(source)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Fontes exportadas para: {filepath}")
        return str(filepath)
    
    def generate_documentation(self) -> str:
        """Gera documentação das fontes em formato Markdown"""
        doc_lines = [
            "# Seed Pack - Fontes Prioritárias\n",
            f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"Total de fontes: {len(self.sources)}\n\n"
        ]
        
        for category in SeedCategory:
            sources = self.categories[category]
            if not sources:
                continue
            
            doc_lines.append(f"## {category.value.replace('_', ' ').title()}\n\n")
            
            for source in sources:
                doc_lines.extend([
                    f"### {source.name}\n\n",
                    f"**Prioridade:** {source.priority}\n\n",
                    f"**Descrição:** {source.description}\n\n",
                    f"**URL:** [{source.url}]({source.url})\n\n",
                    f"**Licença:** {source.license}\n\n",
                    f"**Tags:** {', '.join(source.tags)}\n\n"
                ])
                
                if source.documentation_url:
                    doc_lines.append(f"**Documentação:** [{source.documentation_url}]({source.documentation_url})\n\n")
                
                if source.github_url:
                    doc_lines.append(f"**GitHub:** [{source.github_url}]({source.github_url})\n\n")
                
                if source.installation_guide:
                    doc_lines.append(f"**Instalação:** {source.installation_guide}\n\n")
                
                if source.common_patterns:
                    doc_lines.append("**Padrões Comuns:**\n")
                    for pattern in source.common_patterns:
                        doc_lines.append(f"- {pattern}\n")
                    doc_lines.append("\n")
                
                if source.known_issues:
                    doc_lines.append("**Problemas Conhecidos:**\n")
                    for issue in source.known_issues:
                        doc_lines.append(f"- {issue}\n")
                    doc_lines.append("\n")
                
                doc_lines.append("---\n\n")
        
        documentation = "".join(doc_lines)
        
        # Salva documentação
        doc_path = self.data_dir / "seed_pack_documentation.md"
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(documentation)
        
        logger.info(f"Documentação gerada: {doc_path}")
        return documentation
    
    def _load_sources(self) -> None:
        """Carrega fontes salvas anteriormente"""
        sources_file = self.data_dir / "seed_sources.json"
        
        if sources_file.exists():
            try:
                with open(sources_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for source_data in data.get("sources", []):
                    # Converte category string para enum
                    category = SeedCategory(source_data["category"])
                    source_data["category"] = category
                    
                    source = SeedSource(**source_data)
                    self.add_source(source)
                
                logger.info(f"Carregadas {len(self.sources)} fontes do arquivo")
                
            except Exception as e:
                logger.warning(f"Erro ao carregar fontes: {e}")
    
    def save_sources(self) -> None:
        """Salva todas as fontes em arquivo"""
        sources_file = self.data_dir / "seed_sources.json"
        
        try:
            data = {
                "saved_at": datetime.now().isoformat(),
                "total_sources": len(self.sources),
                "sources": []
            }
            
            for source in self.sources.values():
                source_dict = asdict(source)
                source_dict["category"] = source.category.value
                data["sources"].append(source_dict)
            
            with open(sources_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Fontes salvas em: {sources_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar fontes: {e}")
            raise

# Instância global
seed_manager = SeedManager()