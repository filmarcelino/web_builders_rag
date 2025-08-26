#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico do RAG para análise de conteúdo sobre animações e efeitos visuais
"""

import json
import os
from datetime import datetime
from collections import Counter
import re

def analyze_animation_content():
    """Analisa o conteúdo do corpus para avaliar cobertura de animações"""
    
    print("🎬 Analisando conteúdo sobre animações no corpus RAG...\n")
    
    try:
        # Carregar metadados dos chunks
        with open("rag_data/chunk_metadata.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"✅ Carregados {len(metadata)} chunks para análise")
    except Exception as e:
        print(f"❌ Erro ao carregar metadados: {e}")
        return
    
    # Palavras-chave relacionadas a animações
    animation_keywords = {
        'css_animations': ['animation', '@keyframes', 'keyframe', 'animate', 'animation-duration', 'animation-delay'],
        'transitions': ['transition', 'transition-duration', 'transition-property', 'ease', 'ease-in', 'ease-out'],
        'transforms': ['transform', 'translate', 'rotate', 'scale', 'skew', 'matrix'],
        'effects': ['hover', 'focus', 'active', 'effect', 'fade', 'slide', 'bounce'],
        'js_animations': ['requestAnimationFrame', 'setTimeout', 'setInterval', 'gsap', 'framer-motion'],
        'performance': ['will-change', 'transform3d', 'translateZ', 'gpu', 'hardware-acceleration']
    }
    
    # Análise por categoria
    category_stats = {}
    animation_chunks = []
    total_animation_content = 0
    
    for category, keywords in animation_keywords.items():
        matching_chunks = []
        
        for i, chunk in enumerate(metadata):
            content_lower = chunk['content'].lower()
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            
            if matches > 0:
                chunk_info = {
                    'index': i,
                    'source': chunk.get('source', 'unknown'),
                    'content_preview': chunk['content'][:300] + "...",
                    'keyword_matches': matches,
                    'matched_keywords': [kw for kw in keywords if kw in content_lower]
                }
                matching_chunks.append(chunk_info)
        
        category_stats[category] = {
            'chunks_count': len(matching_chunks),
            'percentage': round((len(matching_chunks) / len(metadata)) * 100, 2),
            'chunks': matching_chunks[:5]  # Top 5 para economizar espaço
        }
        
        total_animation_content += len(matching_chunks)
        animation_chunks.extend(matching_chunks)
    
    # Remover duplicatas (chunks que aparecem em múltiplas categorias)
    unique_animation_chunks = {}
    for chunk in animation_chunks:
        idx = chunk['index']
        if idx not in unique_animation_chunks:
            unique_animation_chunks[idx] = chunk
        else:
            # Combinar keywords matched
            existing = unique_animation_chunks[idx]
            existing['matched_keywords'] = list(set(existing['matched_keywords'] + chunk['matched_keywords']))
            existing['keyword_matches'] += chunk['keyword_matches']
    
    unique_count = len(unique_animation_chunks)
    
    # Análise de fontes
    source_analysis = Counter()
    for chunk in unique_animation_chunks.values():
        source_analysis[chunk['source']] += 1
    
    # Consultas de teste simuladas
    test_queries = [
        "Como criar animações CSS suaves?",
        "Efeitos de transição em JavaScript",
        "Animações performáticas para web",
        "Keyframes e transformações CSS",
        "Bibliotecas de animação modernas"
    ]
    
    # Simular relevância para cada consulta
    query_relevance = []
    for query in test_queries:
        query_words = query.lower().split()
        relevant_chunks = 0
        
        for chunk in unique_animation_chunks.values():
            content_lower = chunk['content_preview'].lower()
            relevance_score = sum(1 for word in query_words if word in content_lower)
            if relevance_score > 0:
                relevant_chunks += 1
        
        query_relevance.append({
            'query': query,
            'relevant_chunks': relevant_chunks,
            'relevance_percentage': round((relevant_chunks / unique_count) * 100, 1) if unique_count > 0 else 0
        })
    
    # Compilar resultados
    results = {
        'timestamp': datetime.now().isoformat(),
        'corpus_stats': {
            'total_chunks': len(metadata),
            'animation_related_chunks': unique_count,
            'animation_coverage_percentage': round((unique_count / len(metadata)) * 100, 2)
        },
        'category_breakdown': category_stats,
        'source_distribution': dict(source_analysis.most_common()),
        'query_simulation': query_relevance,
        'top_animation_chunks': list(unique_animation_chunks.values())[:10]
    }
    
    # Salvar resultados
    output_file = "rag_animations_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Exibir resumo
    print("📊 ANÁLISE DE CONTEÚDO SOBRE ANIMAÇÕES:")
    print(f"   📦 Total de chunks no corpus: {len(metadata)}")
    print(f"   🎬 Chunks relacionados a animações: {unique_count}")
    print(f"   📈 Cobertura de animações: {results['corpus_stats']['animation_coverage_percentage']}%")
    print()
    
    print("🎯 BREAKDOWN POR CATEGORIA:")
    for category, stats in category_stats.items():
        print(f"   {category.replace('_', ' ').title()}: {stats['chunks_count']} chunks ({stats['percentage']}%)")
    print()
    
    print("📚 TOP FONTES COM CONTEÚDO DE ANIMAÇÃO:")
    for source, count in list(source_analysis.most_common(5)):
        print(f"   {source}: {count} chunks")
    print()
    
    print("🔍 SIMULAÇÃO DE CONSULTAS:")
    avg_relevance = sum(q['relevance_percentage'] for q in query_relevance) / len(query_relevance)
    for query_result in query_relevance:
        print(f"   '{query_result['query']}': {query_result['relevant_chunks']} chunks relevantes ({query_result['relevance_percentage']}%)")
    print(f"   📊 Relevância média: {avg_relevance:.1f}%")
    print()
    
    # Avaliação final
    coverage = results['corpus_stats']['animation_coverage_percentage']
    if coverage >= 15:
        assessment = "🌟 EXCELENTE - Boa cobertura de conteúdo sobre animações!"
    elif coverage >= 10:
        assessment = "👍 BOM - Cobertura adequada de animações."
    elif coverage >= 5:
        assessment = "⚠️  MODERADO - Cobertura limitada, pode precisar de mais conteúdo."
    else:
        assessment = "❌ BAIXO - Pouco conteúdo sobre animações no corpus."
    
    print(f"🎯 AVALIAÇÃO GERAL: {assessment}")
    print(f"💾 Análise detalhada salva em: {output_file}")
    
    return results

if __name__ == "__main__":
    analyze_animation_content()