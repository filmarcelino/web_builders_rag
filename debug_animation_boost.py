#!/usr/bin/env python3
"""
Debug detalhado do sistema de boost de animação
"""

import json
from src.prompts.animation_prompt_enhancer import AnimationPromptEnhancer

def debug_boost_system():
    """Debug detalhado do sistema de boost"""
    enhancer = AnimationPromptEnhancer()
    
    # Chunks de teste com conteúdo específico
    test_chunks = [
        {
            'content': '@keyframes fadeIn { 0% { opacity: 0; } 100% { opacity: 1; } }',
            'source': 'CSS Animation Guide',
            'similarity_score': 0.85,
            'metadata': {'type': 'animation', 'technique': 'keyframes'}
        },
        {
            'content': '.element { transition: all 0.3s ease-in-out; transform: scale(1.1); }',
            'source': 'CSS Transitions Tutorial',
            'similarity_score': 0.80,
            'metadata': {'type': 'animation', 'technique': 'transition'}
        },
        {
            'content': '.rotate { transform: rotate(45deg); animation: spin 2s linear infinite; }',
            'source': 'CSS Transform Examples',
            'similarity_score': 0.75,
            'metadata': {'type': 'animation', 'technique': 'transform'}
        },
        {
            'content': '.container { display: flex; justify-content: center; }',
            'source': 'Flexbox Guide',
            'similarity_score': 0.70,
            'metadata': {'type': 'layout'}
        },
        {
            'content': '.grid { display: grid; grid-template-columns: 1fr 1fr; }',
            'source': 'CSS Grid Tutorial',
            'similarity_score': 0.65,
            'metadata': {'type': 'layout'}
        }
    ]
    
    print("🔍 DEBUG: Sistema de Boost de Animação")
    print("=" * 60)
    
    print("\n📋 CHUNKS ORIGINAIS:")
    for i, chunk in enumerate(test_chunks):
        print(f"  {i+1}. Score: {chunk['similarity_score']:.3f} | {chunk['content'][:50]}...")
    
    # Aplicar boost
    print("\n🚀 APLICANDO BOOST...")
    boosted_chunks = enhancer.get_animation_context_boost(test_chunks.copy())
    
    print("\n📈 CHUNKS APÓS BOOST:")
    total_boost_applied = 0
    for i, chunk in enumerate(boosted_chunks):
        original_score = test_chunks[i]['similarity_score']
        new_score = chunk['similarity_score']
        boost_applied = chunk.get('animation_boost_applied', False)
        animation_score = chunk.get('animation_score', 0)
        
        if boost_applied:
            total_boost_applied += 1
            boost_ratio = new_score / original_score if original_score > 0 else 1.0
            print(f"  {i+1}. Score: {original_score:.3f} → {new_score:.3f} (x{boost_ratio:.2f}) | Anim Score: {animation_score} | ✅")
        else:
            print(f"  {i+1}. Score: {original_score:.3f} → {new_score:.3f} (sem boost) | ❌")
        
        print(f"      Content: {chunk['content'][:60]}...")
    
    # Análise detalhada
    print("\n🔬 ANÁLISE DETALHADA:")
    
    # Verificar keywords
    print("\n🔑 Keywords de animação configuradas:")
    for keyword in enhancer.config.animation_keywords:
        print(f"  - {keyword}")
    
    # Verificar detecção por chunk
    print("\n🎯 Detecção por chunk:")
    for i, chunk in enumerate(test_chunks):
        content_lower = chunk['content'].lower()
        detected_keywords = []
        
        for keyword in enhancer.config.animation_keywords:
            if keyword.lower() in content_lower:
                detected_keywords.append(keyword)
        
        # Verificar padrões especiais
        special_patterns = []
        if 'keyframes' in content_lower:
            special_patterns.append('keyframes (+3)')
        if '@keyframes' in content_lower:
            special_patterns.append('@keyframes (+4)')
        if 'transform' in content_lower:
            special_patterns.append('transform (+2)')
        
        print(f"  Chunk {i+1}:")
        print(f"    Keywords: {detected_keywords}")
        print(f"    Especiais: {special_patterns}")
        
        # Calcular score esperado
        expected_animation_score = len(detected_keywords)
        if 'keyframes' in content_lower:
            expected_animation_score += 3
        if 'transform' in content_lower:
            expected_animation_score += 2
        if '@keyframes' in content_lower:
            expected_animation_score += 4
        
        if expected_animation_score > 0:
            boost_factor = 1 + (expected_animation_score * 0.1)
            expected_new_score = min(chunk['similarity_score'] * boost_factor, 1.0)
            print(f"    Score esperado: {chunk['similarity_score']:.3f} × {boost_factor:.2f} = {expected_new_score:.3f}")
        else:
            print(f"    Sem boost esperado")
    
    # Estatísticas finais
    original_avg = sum(c['similarity_score'] for c in test_chunks) / len(test_chunks)
    boosted_avg = sum(c['similarity_score'] for c in boosted_chunks) / len(boosted_chunks)
    improvement_ratio = boosted_avg / original_avg if original_avg > 0 else 1.0
    
    print("\n📊 ESTATÍSTICAS FINAIS:")
    print(f"  Chunks com boost aplicado: {total_boost_applied}/{len(test_chunks)}")
    print(f"  Score médio original: {original_avg:.3f}")
    print(f"  Score médio após boost: {boosted_avg:.3f}")
    print(f"  Ratio de melhoria: {improvement_ratio:.3f}x")
    print(f"  Meta de 3x alcançada: {'✅ SIM' if improvement_ratio >= 3.0 else '❌ NÃO'}")
    
    # Sugestões de melhoria
    print("\n💡 SUGESTÕES DE MELHORIA:")
    if improvement_ratio < 3.0:
        print("  - Aumentar o boost_factor de 0.1 para 0.5 ou mais")
        print("  - Adicionar boost específico para consultas de animação")
        print("  - Implementar boost multiplicativo em vez de aditivo")
        print("  - Considerar boost baseado na relevância da consulta")
    else:
        print("  - Sistema funcionando adequadamente!")

if __name__ == "__main__":
    debug_boost_system()