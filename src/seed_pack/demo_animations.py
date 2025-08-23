#!/usr/bin/env python3
"""
Demo do Animation Seed Pack

Este script demonstra como usar o novo seed pack de animações,
mostrando busca, filtragem e integração com o sistema RAG.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seed_pack.animations import (
    animation_seed_pack,
    get_react_animation_sources,
    get_3d_sources,
    get_interactive_asset_sources,
    get_micro_interaction_sources,
    get_accessibility_sources,
    search_animation_sources,
    get_sources_for_performance,
    get_accessible_animation_sources
)
from seed_pack.seed_manager import SeedManager, SeedCategory, SeedSource

def demo_animation_seed_pack():
    """Demonstra funcionalidades do Animation Seed Pack"""
    print("🎬 Animation Seed Pack Demo")
    print("=" * 50)
    
    # Estatísticas gerais
    stats = animation_seed_pack.get_statistics()
    print(f"\n📊 Estatísticas:")
    print(f"Total de fontes: {stats['total_sources']}")
    print(f"Categorias: {len(stats['categories'])}")
    
    for category, count in stats['categories'].items():
        category_name = stats['category_names'].get(category, category)
        print(f"  - {category_name}: {count} fontes")
    
    # Demonstrar busca por categoria
    print("\n🎭 Fontes React/JS:")
    react_sources = get_react_animation_sources()
    for source in react_sources[:2]:  # Mostrar apenas 2 para brevidade
        print(f"  - {source.name}: {source.description}")
        print(f"    Bundle: {source.bundle_size}")
        print(f"    Tags: {', '.join(source.tags)}")
    
    # Demonstrar busca por performance
    print("\n⚡ Fontes otimizadas para performance:")
    perf_sources = get_sources_for_performance()
    for source in perf_sources:
        print(f"  - {source.name} ({source.bundle_size})")
        if source.performance_notes:
            print(f"    💡 {source.performance_notes}")
    
    # Demonstrar busca por acessibilidade
    print("\n♿ Fontes com foco em acessibilidade:")
    a11y_sources = get_accessible_animation_sources()
    for source in a11y_sources:
        print(f"  - {source.name}")
        if source.accessibility_notes:
            print(f"    ♿ {source.accessibility_notes}")
    
    # Demonstrar busca por termo
    print("\n🔍 Busca por 'react':")
    search_results = search_animation_sources("react")
    for source in search_results[:3]:
        print(f"  - {source.name}: {source.category}")
    
    # Demonstrar fontes 3D
    print("\n🌀 Fontes 3D/WebGL:")
    sources_3d = get_3d_sources()
    for source in sources_3d:
        print(f"  - {source.name}")
        print(f"    Casos de uso: {', '.join(source.use_cases[:2])}...")
    
    return stats

def demo_integration_with_seed_manager():
    """Demonstra integração com o SeedManager principal"""
    print("\n🔗 Integração com SeedManager")
    print("=" * 50)
    
    # Criar instância do seed manager
    seed_manager = SeedManager()
    
    # Converter algumas fontes de animação para o formato SeedSource
    react_sources = get_react_animation_sources()
    
    for anim_source in react_sources[:2]:  # Converter apenas 2 para demo
        seed_source = SeedSource(
            name=anim_source.name,
            category=SeedCategory.ANIMATIONS,
            url=anim_source.url,
            description=anim_source.description,
            license=anim_source.license,
            priority=1 if 'performance' in anim_source.tags else 2,
            tags=anim_source.tags,
            documentation_url=anim_source.url,
            installation_guide=anim_source.installation,
            common_patterns=anim_source.use_cases,
            known_issues=anim_source.common_issues
        )
        
        seed_manager.add_source(seed_source)
        print(f"✅ Adicionado: {seed_source.name}")
    
    # Buscar fontes de animação no seed manager
    animation_sources = seed_manager.get_sources_by_category(SeedCategory.ANIMATIONS)
    print(f"\n📦 Fontes de animação no SeedManager: {len(animation_sources)}")
    
    # Buscar por tags
    react_tags = seed_manager.get_sources_by_tags(['react', 'animation'])
    print(f"🏷️ Fontes com tags 'react' ou 'animation': {len(react_tags)}")
    
    # Estatísticas
    stats = seed_manager.get_category_stats()
    if 'animations' in stats:
        anim_stats = stats['animations']
        print(f"\n📊 Estatísticas de animações:")
        print(f"  Total: {anim_stats['total_sources']}")
        print(f"  Prioridade 1: {anim_stats['priority_1']}")
        print(f"  Prioridade 2: {anim_stats['priority_2']}")

def demo_markdown_export():
    """Demonstra exportação da documentação"""
    print("\n📝 Exportação de Documentação")
    print("=" * 50)
    
    # Gerar documentação markdown
    markdown_content = animation_seed_pack.export_markdown_documentation()
    
    # Mostrar preview da documentação
    lines = markdown_content.split('\n')
    print("\n📄 Preview da documentação (primeiras 20 linhas):")
    for i, line in enumerate(lines[:20]):
        print(line)
    
    print(f"\n... (total de {len(lines)} linhas)")
    print(f"\n💾 Documentação completa disponível em: animations_documentation.md")

def demo_search_scenarios():
    """Demonstra cenários de busca específicos"""
    print("\n🎯 Cenários de Busca Específicos")
    print("=" * 50)
    
    scenarios = [
        ("performance", "Busca por performance"),
        ("3d", "Busca por 3D"),
        ("accessibility", "Busca por acessibilidade"),
        ("react", "Busca por React"),
        ("lightweight", "Busca por bibliotecas leves"),
        ("svg", "Busca por SVG")
    ]
    
    for query, description in scenarios:
        results = search_animation_sources(query)
        print(f"\n🔍 {description} ('{query}'):")
        print(f"   Encontradas {len(results)} fontes")
        
        for result in results[:2]:  # Mostrar apenas 2 resultados
            print(f"   - {result.name} ({result.category})")
            if hasattr(result, 'bundle_size') and result.bundle_size != "N/A":
                print(f"     Bundle: {result.bundle_size}")

def demo_usage_recommendations():
    """Demonstra recomendações de uso baseadas em cenários"""
    print("\n💡 Recomendações de Uso")
    print("=" * 50)
    
    scenarios = {
        "Projeto React com foco em performance": {
            "sources": get_sources_for_performance(),
            "filter": lambda s: 'react' in s.tags
        },
        "Aplicação 3D interativa": {
            "sources": get_3d_sources(),
            "filter": lambda s: 'interactive' in s.tags or 'react' in s.tags
        },
        "Micro-interações acessíveis": {
            "sources": get_accessible_animation_sources(),
            "filter": lambda s: 'micro-interactions' in s.tags or 'lightweight' in s.tags
        }
    }
    
    for scenario, config in scenarios.items():
        print(f"\n🎯 {scenario}:")
        sources = config['sources']
        if 'filter' in config:
            sources = [s for s in sources if config['filter'](s)]
        
        for source in sources[:2]:  # Mostrar apenas 2 recomendações
            print(f"   ✅ {source.name}")
            print(f"      {source.description}")
            if hasattr(source, 'bundle_size'):
                print(f"      Bundle: {source.bundle_size}")

def main():
    """Função principal da demonstração"""
    try:
        print("🚀 Iniciando demonstração do Animation Seed Pack...\n")
        
        # Executar todas as demonstrações
        demo_animation_seed_pack()
        demo_integration_with_seed_manager()
        demo_markdown_export()
        demo_search_scenarios()
        demo_usage_recommendations()
        
        print("\n✅ Demonstração concluída com sucesso!")
        print("\n📚 Para usar o Animation Seed Pack:")
        print("   from seed_pack.animations import animation_seed_pack")
        print("   sources = animation_seed_pack.search_sources('react')")
        
    except Exception as e:
        print(f"❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)