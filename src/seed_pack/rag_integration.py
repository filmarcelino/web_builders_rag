#!/usr/bin/env python3
"""
Integração do Animation Seed Pack com o Sistema RAG

Este módulo integra o seed pack de animações ao sistema RAG principal,
permitindo indexação e busca das fontes de animação.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from datetime import datetime

from seed_pack.animations import animation_seed_pack, AnimationSource

class AnimationSeedPackRAGIntegration:
    """Integração do Animation Seed Pack com o sistema RAG"""
    
    def __init__(self):
        self.seed_pack = animation_seed_pack
    
    def convert_animation_source_to_document(self, source: AnimationSource) -> Dict[str, Any]:
        """Converte uma AnimationSource para formato de documento RAG"""
        
        # Criar conteúdo textual rico para indexação
        content_parts = [
            f"# {source.name}",
            f"**Categoria:** {source.category}",
            f"**Descrição:** {source.description}",
            f"**Licença:** {source.license}",
            f"**URL:** {source.url}",
            f"**Instalação:** {source.installation}",
            f"**Bundle Size:** {source.bundle_size}"
        ]
        
        if source.use_cases:
            content_parts.append("\n**Casos de uso:**")
            for use_case in source.use_cases:
                content_parts.append(f"- {use_case}")
        
        if source.common_issues:
            content_parts.append("\n**Problemas comuns:**")
            for issue in source.common_issues:
                content_parts.append(f"- {issue}")
        
        if source.examples:
            content_parts.append("\n**Exemplos de código:**")
            for example in source.examples:
                content_parts.append(f"```javascript\n{example}\n```")
        
        if source.performance_notes:
            content_parts.append(f"\n**Performance:** {source.performance_notes}")
        
        if source.accessibility_notes:
            content_parts.append(f"\n**Acessibilidade:** {source.accessibility_notes}")
        
        content = "\n".join(content_parts)
        
        # Criar documento no formato esperado pelo RAG
        document = {
            "id": f"animation_{source.name.lower().replace(' ', '_').replace('/', '_')}",
            "title": f"{source.name} - Animation Library",
            "content": content,
            "url": source.url,
            "source_type": "animation_library",
            "metadata": {
                "category": source.category,
                "license": source.license,
                "bundle_size": source.bundle_size,
                "tags": source.tags,
                "installation": source.installation,
                "last_updated": source.last_updated,
                "priority": "high" if any(tag in ['performance', 'lightweight'] for tag in source.tags) else "medium",
                "use_cases": source.use_cases,
                "common_issues": source.common_issues,
                "examples": source.examples,
                "performance_notes": source.performance_notes,
                "accessibility_notes": source.accessibility_notes,
                "seed_pack": "animations",
                "indexed_at": datetime.now().isoformat()
            }
        }
        
        return document
    
    def index_all_animation_sources(self) -> List[Dict[str, Any]]:
        """Indexa todas as fontes de animação no sistema RAG"""
        documents = []
        
        for source in self.seed_pack.sources:
            document = self.convert_animation_source_to_document(source)
            documents.append(document)
        
        print(f"📦 Convertidas {len(documents)} fontes de animação para documentos RAG")
        return documents
    
    def create_category_overview_documents(self) -> List[Dict[str, Any]]:
        """Cria documentos de visão geral para cada categoria"""
        documents = []
        
        for category_key, category_name in self.seed_pack.categories.items():
            sources = self.seed_pack.get_sources_by_category(category_key)
            if not sources:
                continue
            
            # Criar conteúdo de overview
            content_parts = [
                f"# {category_name} - Visão Geral",
                f"\nEsta categoria contém {len(sources)} fontes de animação especializadas em {category_name.lower()}.",
                "\n## Fontes Disponíveis:\n"
            ]
            
            for source in sources:
                content_parts.extend([
                    f"### {source.name}",
                    f"- **Bundle Size:** {source.bundle_size}",
                    f"- **Licença:** {source.license}",
                    f"- **Tags:** {', '.join(source.tags)}",
                    f"- **Descrição:** {source.description}\n"
                ])
            
            # Adicionar recomendações baseadas na categoria
            if category_key == "react_js":
                content_parts.append("\n## Recomendações para React:")
                content_parts.append("- Para projetos novos: Framer Motion (mais completo)")
                content_parts.append("- Para performance: Motion One (mais leve)")
                content_parts.append("- Para física natural: React Spring")
                content_parts.append("- Para animações complexas: GSAP")
            
            elif category_key == "3d_webgl":
                content_parts.append("\n## Recomendações para 3D:")
                content_parts.append("- Para iniciantes em React: React Three Fiber")
                content_parts.append("- Para projetos complexos: Three.js puro")
                content_parts.append("- Para helpers úteis: @react-three/drei")
            
            elif category_key == "interactive_assets":
                content_parts.append("\n## Recomendações para Assets:")
                content_parts.append("- Para animações de designer: Lottie")
                content_parts.append("- Para interatividade complexa: Rive")
            
            content = "\n".join(content_parts)
            
            document = {
                "id": f"animation_category_{category_key}",
                "title": f"{category_name} - Animation Category Overview",
                "content": content,
                "url": f"#category-{category_key}",
                "source_type": "animation_category",
                "metadata": {
                    "category": category_key,
                    "total_sources": len(sources),
                    "tags": ["overview", "category", "animations", category_key],
                    "seed_pack": "animations",
                    "indexed_at": datetime.now().isoformat()
                }
            }
            
            documents.append(document)
        
        print(f"📋 Criados {len(documents)} documentos de overview de categoria")
        return documents
    
    def create_usage_guide_documents(self) -> List[Dict[str, Any]]:
        """Cria documentos de guias de uso específicos"""
        documents = []
        
        # Guia de Performance
        perf_sources = [s for s in self.seed_pack.sources if 'performance' in s.tags or 'lightweight' in s.tags]
        if perf_sources:
            content = self._create_performance_guide(perf_sources)
            documents.append({
                "id": "animation_performance_guide",
                "title": "Guia de Performance para Animações",
                "content": content,
                "url": "#performance-guide",
                "source_type": "animation_guide",
                "metadata": {
                    "guide_type": "performance",
                    "tags": ["performance", "optimization", "guide", "animations"],
                    "seed_pack": "animations",
                    "indexed_at": datetime.now().isoformat()
                }
            })
        
        # Guia de Acessibilidade
        a11y_sources = [s for s in self.seed_pack.sources if 'accessibility' in s.tags or s.accessibility_notes]
        if a11y_sources:
            content = self._create_accessibility_guide(a11y_sources)
            documents.append({
                "id": "animation_accessibility_guide",
                "title": "Guia de Acessibilidade para Animações",
                "content": content,
                "url": "#accessibility-guide",
                "source_type": "animation_guide",
                "metadata": {
                    "guide_type": "accessibility",
                    "tags": ["accessibility", "a11y", "inclusive", "guide", "animations"],
                    "seed_pack": "animations",
                    "indexed_at": datetime.now().isoformat()
                }
            })
        
        # Guia de Escolha de Biblioteca
        content = self._create_library_selection_guide()
        documents.append({
            "id": "animation_library_selection_guide",
            "title": "Como Escolher a Biblioteca de Animação Certa",
            "content": content,
            "url": "#library-selection-guide",
            "source_type": "animation_guide",
            "metadata": {
                "guide_type": "selection",
                "tags": ["selection", "comparison", "guide", "animations", "decision"],
                "seed_pack": "animations",
                "indexed_at": datetime.now().isoformat()
            }
        })
        
        print(f"📖 Criados {len(documents)} documentos de guia")
        return documents
    
    def _create_performance_guide(self, sources: List[AnimationSource]) -> str:
        """Cria guia de performance"""
        content = [
            "# Guia de Performance para Animações",
            "\nEste guia ajuda a escolher e otimizar bibliotecas de animação para melhor performance.",
            "\n## Bibliotecas Otimizadas para Performance:\n"
        ]
        
        # Ordenar por bundle size (extrair números)
        def extract_size(bundle_str):
            if 'kb' in bundle_str.lower():
                try:
                    return float(bundle_str.lower().split('kb')[0].split('~')[-1])
                except:
                    return 999
            return 999
        
        sorted_sources = sorted(sources, key=lambda s: extract_size(s.bundle_size))
        
        for source in sorted_sources:
            content.extend([
                f"### {source.name}",
                f"- **Bundle Size:** {source.bundle_size}",
                f"- **Performance Notes:** {source.performance_notes or 'N/A'}",
                f"- **Recomendado para:** {', '.join(source.use_cases[:2])}\n"
            ])
        
        content.extend([
            "\n## Dicas Gerais de Performance:",
            "- Prefira `transform` e `opacity` para animações CSS",
            "- Use `will-change` com moderação",
            "- Implemente `prefers-reduced-motion` sempre",
            "- Considere lazy loading para bibliotecas grandes",
            "- Teste performance em dispositivos móveis"
        ])
        
        return "\n".join(content)
    
    def _create_accessibility_guide(self, sources: List[AnimationSource]) -> str:
        """Cria guia de acessibilidade"""
        content = [
            "# Guia de Acessibilidade para Animações",
            "\nAnimações devem ser inclusivas e respeitar as necessidades de todos os usuários.",
            "\n## Bibliotecas com Suporte a Acessibilidade:\n"
        ]
        
        for source in sources:
            if source.accessibility_notes:
                content.extend([
                    f"### {source.name}",
                    f"- **Suporte:** {source.accessibility_notes}",
                    f"- **Implementação:** {source.installation}\n"
                ])
        
        content.extend([
            "\n## Diretrizes Essenciais:",
            "\n### 1. Respeitar prefers-reduced-motion",
            "```css",
            "@media (prefers-reduced-motion: reduce) {",
            "  * {",
            "    animation-duration: 0.01ms !important;",
            "    transition-duration: 0.01ms !important;",
            "  }",
            "}",
            "```",
            "\n### 2. Fornecer controles de pausa",
            "- Animações que duram mais de 5 segundos devem ter controles",
            "- Permitir pausar/retomar animações",
            "\n### 3. Evitar animações que causam convulsões",
            "- Não usar flashes rápidos (mais de 3 por segundo)",
            "- Evitar padrões estroboscópicos",
            "\n### 4. Manter funcionalidade sem animações",
            "- Interface deve funcionar completamente sem animações",
            "- Animações devem ser progressively enhanced"
        ])
        
        return "\n".join(content)
    
    def _create_library_selection_guide(self) -> str:
        """Cria guia de seleção de biblioteca"""
        content = [
            "# Como Escolher a Biblioteca de Animação Certa",
            "\nEste guia ajuda a decidir qual biblioteca usar baseado no seu projeto.",
            "\n## Árvore de Decisão:",
            "\n### 1. Você está usando React?",
            "\n**SIM** → Continue para React-specific",
            "**NÃO** → Considere GSAP, Anime.js ou Motion One",
            "\n### 2. React: Qual o foco do projeto?",
            "\n**Performance crítica** → Motion One (~12kb)",
            "**Animações complexas** → GSAP",
            "**Física natural** → React Spring",
            "**Facilidade de uso** → Framer Motion",
            "\n### 3. Você precisa de 3D?",
            "\n**SIM, com React** → React Three Fiber + Drei",
            "**SIM, vanilla JS** → Three.js",
            "**NÃO** → Continue com 2D",
            "\n### 4. Você tem animações de designer?",
            "\n**After Effects** → Lottie",
            "**Interativas complexas** → Rive",
            "**Simples** → CSS + biblioteca 2D",
            "\n## Comparação Rápida:",
            "\n| Biblioteca | Bundle | Curva | Performance | React |",
            "| --- | --- | --- | --- | --- |",
            "| Motion One | 12kb | Baixa | Alta | ❌ |",
            "| Anime.js | 17kb | Baixa | Média | ❌ |",
            "| React Spring | 25kb | Média | Alta | ✅ |",
            "| GSAP | 35kb+ | Alta | Muito Alta | ⚠️ |",
            "| Framer Motion | 50kb | Baixa | Alta | ✅ |",
            "| Lottie | 150kb+ | Baixa | Média | ✅ |",
            "\n## Recomendações por Cenário:",
            "\n**Landing Page** → Motion One ou Anime.js",
            "**App React** → Framer Motion ou React Spring",
            "**Dashboard** → GSAP para gráficos complexos",
            "**Game/Interactive** → GSAP + Three.js",
            "**Mobile-first** → Motion One ou React Spring"
        ]
        
        return "\n".join(content)
    
    def get_all_rag_documents(self) -> List[Dict[str, Any]]:
        """Retorna todos os documentos para indexação no RAG"""
        documents = []
        
        # Adicionar fontes individuais
        documents.extend(self.index_all_animation_sources())
        
        # Adicionar overviews de categoria
        documents.extend(self.create_category_overview_documents())
        
        # Adicionar guias de uso
        documents.extend(self.create_usage_guide_documents())
        
        print(f"\n📚 Total de documentos RAG criados: {len(documents)}")
        return documents
    
    def export_for_ingestion(self, output_path: str = "data/seed_pack/animations_rag_export.json") -> str:
        """Exporta documentos para ingestão no sistema RAG"""
        documents = self.get_all_rag_documents()
        
        export_data = {
            "export_info": {
                "created_at": datetime.now().isoformat(),
                "source": "animation_seed_pack",
                "total_documents": len(documents),
                "document_types": {
                    "animation_library": len([d for d in documents if d["source_type"] == "animation_library"]),
                    "animation_category": len([d for d in documents if d["source_type"] == "animation_category"]),
                    "animation_guide": len([d for d in documents if d["source_type"] == "animation_guide"])
                }
            },
            "documents": documents
        }
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Salvar arquivo
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Documentos exportados para: {output_path}")
        return output_path

# Instância global
animation_rag_integration = AnimationSeedPackRAGIntegration()

# Funções de conveniência
def export_animations_to_rag(output_path: str = None) -> str:
    """Exporta seed pack de animações para o sistema RAG"""
    if output_path is None:
        output_path = "data/seed_pack/animations_rag_export.json"
    return animation_rag_integration.export_for_ingestion(output_path)

def get_animation_documents_for_rag() -> List[Dict[str, Any]]:
    """Retorna documentos de animação prontos para indexação"""
    return animation_rag_integration.get_all_rag_documents()