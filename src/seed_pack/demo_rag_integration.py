#!/usr/bin/env python3
"""
Demonstração da Integração RAG do Animation Seed Pack

Este script demonstra como o seed pack de animações se integra
completamente ao sistema RAG para busca e recomendações.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seed_pack.rag_integration import animation_rag_integration, export_animations_to_rag
from seed_pack.animations import animation_seed_pack
from datetime import datetime

def demonstrate_rag_integration():
    """Demonstra a integração completa com o sistema RAG"""
    print("🎬 DEMONSTRAÇÃO: Animation Seed Pack + Sistema RAG")
    print("=" * 60)
    
    # 1. Mostrar estatísticas do seed pack
    print("\n📊 ESTATÍSTICAS DO SEED PACK:")
    stats = animation_seed_pack.get_statistics()
    print(f"Total de fontes: {stats['total_sources']}")
    print(f"Categorias: {len(stats['categories'])}")
    for category, count in stats['categories'].items():
        category_name = stats['category_names'].get(category, category)
        print(f"  - {category_name}: {count} fontes")
    
    # 2. Converter para documentos RAG
    print("\n🔄 CONVERSÃO PARA DOCUMENTOS RAG:")
    documents = animation_rag_integration.get_all_rag_documents()
    
    doc_types = {}
    for doc in documents:
        doc_type = doc['source_type']
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
    
    print(f"Total de documentos RAG: {len(documents)}")
    for doc_type, count in doc_types.items():
        print(f"  - {doc_type}: {count} documentos")
    
    # 3. Mostrar exemplos de documentos
    print("\n📄 EXEMPLOS DE DOCUMENTOS RAG:")
    
    # Exemplo: Framer Motion
    framer_doc = next((d for d in documents if 'framer_motion' in d['id']), None)
    if framer_doc:
        print("\n🎭 Exemplo - Framer Motion:")
        print(f"ID: {framer_doc['id']}")
        print(f"Título: {framer_doc['title']}")
        print(f"Tags: {framer_doc['metadata']['tags']}")
        print(f"Bundle Size: {framer_doc['metadata']['bundle_size']}")
        print(f"Conteúdo (primeiras 200 chars): {framer_doc['content'][:200]}...")
    
    # Exemplo: Guia de Performance
    perf_guide = next((d for d in documents if 'performance_guide' in d['id']), None)
    if perf_guide:
        print("\n⚡ Exemplo - Guia de Performance:")
        print(f"ID: {perf_guide['id']}")
        print(f"Título: {perf_guide['title']}")
        print(f"Tipo de guia: {perf_guide['metadata']['guide_type']}")
        print(f"Tags: {perf_guide['metadata']['tags']}")
    
    # 4. Simular buscas RAG
    print("\n🔍 SIMULAÇÃO DE BUSCAS RAG:")
    
    search_queries = [
        "animação React performance",
        "biblioteca 3D WebGL",
        "acessibilidade motion reduced",
        "bundle size pequeno animação",
        "After Effects Lottie"
    ]
    
    for query in search_queries:
        print(f"\n🔎 Busca: '{query}'")
        relevant_docs = simulate_rag_search(documents, query)
        print(f"   Documentos relevantes encontrados: {len(relevant_docs)}")
        
        if relevant_docs:
            top_doc = relevant_docs[0]
            print(f"   📌 Mais relevante: {top_doc['title']}")
            print(f"   📂 Tipo: {top_doc['source_type']}")
            if 'bundle_size' in top_doc['metadata']:
                print(f"   📦 Bundle: {top_doc['metadata']['bundle_size']}")
    
    # 5. Exportar para sistema RAG
    print("\n💾 EXPORTAÇÃO PARA SISTEMA RAG:")
    export_path = export_animations_to_rag()
    print(f"Arquivo exportado: {export_path}")
    
    # Verificar se arquivo foi criado
    if os.path.exists(export_path):
        file_size = os.path.getsize(export_path)
        print(f"Tamanho do arquivo: {file_size:,} bytes")
        
        # Mostrar estrutura do arquivo exportado
        import json
        with open(export_path, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        print("\n📋 Estrutura do arquivo exportado:")
        print(f"  - Data de criação: {export_data['export_info']['created_at']}")
        print(f"  - Total de documentos: {export_data['export_info']['total_documents']}")
        print("  - Tipos de documento:")
        for doc_type, count in export_data['export_info']['document_types'].items():
            print(f"    • {doc_type}: {count}")
    
    # 6. Demonstrar casos de uso específicos
    print("\n🎯 CASOS DE USO ESPECÍFICOS:")
    
    demonstrate_use_case_scenarios(documents)
    
    print("\n✅ DEMONSTRAÇÃO CONCLUÍDA!")
    print("\nO Animation Seed Pack está totalmente integrado ao sistema RAG.")
    print("Agora as fontes de animação podem ser:")
    print("  • Indexadas no sistema de busca")
    print("  • Encontradas via busca híbrida (keyword + vetorial)")
    print("  • Rerankeadas pelo GPT-5 com rationale")
    print("  • Filtradas por metadados (categoria, bundle size, etc.)")
    print("  • Recomendadas contextualmente pelo agente")

def simulate_rag_search(documents, query):
    """Simula uma busca RAG simples baseada em keywords"""
    query_lower = query.lower()
    relevant_docs = []
    
    for doc in documents:
        score = 0
        
        # Buscar no título
        if any(word in doc['title'].lower() for word in query_lower.split()):
            score += 3
        
        # Buscar no conteúdo
        if any(word in doc['content'].lower() for word in query_lower.split()):
            score += 2
        
        # Buscar nas tags
        if 'tags' in doc['metadata']:
            if any(word in ' '.join(doc['metadata']['tags']).lower() for word in query_lower.split()):
                score += 2
        
        # Buscar em metadados específicos
        metadata = doc['metadata']
        searchable_fields = ['category', 'bundle_size', 'license']
        for field in searchable_fields:
            if field in metadata and any(word in str(metadata[field]).lower() for word in query_lower.split()):
                score += 1
        
        if score > 0:
            doc_with_score = doc.copy()
            doc_with_score['_search_score'] = score
            relevant_docs.append(doc_with_score)
    
    # Ordenar por score
    relevant_docs.sort(key=lambda x: x['_search_score'], reverse=True)
    return relevant_docs

def demonstrate_use_case_scenarios(documents):
    """Demonstra cenários específicos de uso"""
    
    scenarios = [
        {
            "name": "Desenvolvedor React procurando animação leve",
            "query": "React animation lightweight performance",
            "context": "Projeto mobile-first que precisa de animações suaves"
        },
        {
            "name": "Designer implementando animações do After Effects",
            "query": "After Effects Lottie JSON animation",
            "context": "Animações complexas criadas no AE precisam ser web"
        },
        {
            "name": "Desenvolvedor criando experiência 3D",
            "query": "3D WebGL Three.js React",
            "context": "App React que precisa de elementos 3D interativos"
        },
        {
            "name": "Equipe focada em acessibilidade",
            "query": "accessibility reduced motion inclusive",
            "context": "Garantir que animações sejam inclusivas"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎭 Cenário: {scenario['name']}")
        print(f"   Contexto: {scenario['context']}")
        print(f"   Busca: '{scenario['query']}'")
        
        results = simulate_rag_search(documents, scenario['query'])
        
        if results:
            top_result = results[0]
            print(f"   💡 Recomendação: {top_result['title']}")
            
            # Extrair recomendação específica baseada no tipo
            if top_result['source_type'] == 'animation_library':
                bundle_size = top_result['metadata'].get('bundle_size', 'N/A')
                license = top_result['metadata'].get('license', 'N/A')
                print(f"   📦 Bundle: {bundle_size} | Licença: {license}")
            elif top_result['source_type'] == 'animation_guide':
                guide_type = top_result['metadata'].get('guide_type', 'N/A')
                print(f"   📖 Tipo de guia: {guide_type}")
        else:
            print("   ❌ Nenhum resultado encontrado")

if __name__ == "__main__":
    demonstrate_rag_integration()