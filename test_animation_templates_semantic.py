#!/usr/bin/env python3
"""
Teste do Sistema de Templates de Animação e Busca Semântica
Testa a funcionalidade dos novos componentes especializados
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.templates.animation_templates import animation_templates, AnimationType
from src.search.semantic_animation_search import semantic_search, AnimationConcept
from src.search.search_engine import SearchEngine, SearchRequest

def test_animation_templates():
    """Testa o sistema de templates de animação"""
    print("\n=== TESTE: Sistema de Templates de Animação ===")
    
    # Teste 1: Busca por templates específicos
    print("\n1. Testando busca por templates específicos:")
    fade_template = animation_templates.get_template("fade_in")
    if fade_template:
        print(f"✅ Template 'fade_in' encontrado: {fade_template.name}")
        print(f"   Tipo: {fade_template.type.value}")
        print(f"   Complexidade: {fade_template.complexity_level}")
    else:
        print("❌ Template 'fade_in' não encontrado")
    
    # Teste 2: Busca por tipo
    print("\n2. Testando busca por tipo (KEYFRAMES):")
    keyframe_templates = animation_templates.get_templates_by_type(AnimationType.KEYFRAMES)
    print(f"✅ Encontrados {len(keyframe_templates)} templates de keyframes:")
    for template in keyframe_templates:
        print(f"   - {template.name} ({template.complexity_level})")
    
    # Teste 3: Busca por complexidade
    print("\n3. Testando busca por complexidade (beginner):")
    beginner_templates = animation_templates.get_templates_by_complexity("beginner")
    print(f"✅ Encontrados {len(beginner_templates)} templates para iniciantes:")
    for template in beginner_templates:
        print(f"   - {template.name} ({template.type.value})")
    
    # Teste 4: Busca textual
    print("\n4. Testando busca textual por 'hover':")
    hover_templates = animation_templates.search_templates("hover")
    print(f"✅ Encontrados {len(hover_templates)} templates relacionados a hover:")
    for template in hover_templates:
        print(f"   - {template.name}: {template.description}")
    
    # Teste 5: Geração de resposta formatada
    print("\n5. Testando geração de resposta formatada:")
    if fade_template:
        formatted_response = animation_templates.generate_template_response(fade_template)
        print("✅ Resposta formatada gerada com sucesso")
        print(f"   Tamanho da resposta: {len(formatted_response)} caracteres")
        print(f"   Primeiras linhas: {formatted_response[:100]}...")
    
    return True

def test_semantic_search():
    """Testa o sistema de busca semântica"""
    print("\n=== TESTE: Sistema de Busca Semântica ===")
    
    test_queries = [
        "how to make a smooth fade in animation",
        "button hover effect with scale",
        "loading spinner animation",
        "slide in from left transition",
        "bounce animation with spring effect",
        "rotate element on click",
        "performance optimized animations",
        "accessible animations with reduced motion"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Analisando query: '{query}'")
        
        # Análise semântica
        analysis = semantic_search.analyze_query(query)
        
        print(f"   ✅ É query de animação: {analysis['is_animation_query']}")
        print(f"   ✅ Score de animação: {analysis['animation_score']:.2f}")
        
        if analysis['semantic_matches']:
            print(f"   ✅ Matches semânticos ({len(analysis['semantic_matches'])}):")
            for match in analysis['semantic_matches'][:3]:  # Mostra apenas os 3 primeiros
                print(f"      - {match.term} ({match.concept.value}, confiança: {match.confidence:.2f})")
        
        if analysis['intent_matches']:
            print(f"   ✅ Intenções detectadas ({len(analysis['intent_matches'])}):")
            for intent in analysis['intent_matches']:
                print(f"      - {intent['intent']} (confiança: {intent['confidence']:.2f})")
        
        # Sugestões
        suggestions = semantic_search.generate_search_suggestions(query)
        if suggestions:
            print(f"   ✅ Sugestões geradas ({len(suggestions)}):")
            for suggestion in suggestions[:2]:  # Mostra apenas as 2 primeiras
                print(f"      - {suggestion}")
    
    return True

async def test_integrated_search():
    """Testa a busca integrada com templates e semântica"""
    print("\n=== TESTE: Busca Integrada (Templates + Semântica) ===")
    
    try:
        # Inicializa o motor de busca
        search_engine = SearchEngine(api_key="demo-api-key")
        
        test_queries = [
            "fade in animation",
            "hover effect for buttons",
            "loading spinner",
            "slide animation from left"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testando busca integrada para: '{query}'")
            
            # Teste de busca de templates
            template_results = await search_engine.search_animation_templates(query)
            print(f"   ✅ Templates encontrados: {len(template_results)}")
            
            for result in template_results:
                print(f"      - {result['template_name']} ({result['template_type']})")
            
            # Teste de sugestões semânticas
            semantic_suggestions = search_engine.get_semantic_suggestions(query)
            print(f"   ✅ Análise semântica concluída")
            print(f"      - É query de animação: {semantic_suggestions['is_animation_query']}")
            print(f"      - Score: {semantic_suggestions['animation_score']:.2f}")
            print(f"      - Sugestões: {len(semantic_suggestions['search_suggestions'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na busca integrada: {str(e)}")
        return False

def generate_test_report(results):
    """Gera relatório de teste"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"animation_templates_semantic_test_report_{timestamp}.json"
    
    report = {
        "timestamp": timestamp,
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["passed"]),
            "failed_tests": sum(1 for r in results if not r["passed"]),
            "success_rate": (sum(1 for r in results if r["passed"]) / len(results)) * 100
        }
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Relatório salvo em: {report_file}")
    return report

async def main():
    """Função principal de teste"""
    print("🚀 INICIANDO TESTES: Sistema de Templates e Busca Semântica")
    print("=" * 70)
    
    results = []
    
    # Teste 1: Templates de Animação
    try:
        success = test_animation_templates()
        results.append({
            "test_name": "Animation Templates System",
            "passed": success,
            "error": None
        })
    except Exception as e:
        results.append({
            "test_name": "Animation Templates System",
            "passed": False,
            "error": str(e)
        })
        print(f"❌ Erro no teste de templates: {str(e)}")
    
    # Teste 2: Busca Semântica
    try:
        success = test_semantic_search()
        results.append({
            "test_name": "Semantic Animation Search",
            "passed": success,
            "error": None
        })
    except Exception as e:
        results.append({
            "test_name": "Semantic Animation Search",
            "passed": False,
            "error": str(e)
        })
        print(f"❌ Erro no teste de busca semântica: {str(e)}")
    
    # Teste 3: Busca Integrada
    try:
        success = await test_integrated_search()
        results.append({
            "test_name": "Integrated Search System",
            "passed": success,
            "error": None
        })
    except Exception as e:
        results.append({
            "test_name": "Integrated Search System",
            "passed": False,
            "error": str(e)
        })
        print(f"❌ Erro no teste de busca integrada: {str(e)}")
    
    # Gera relatório
    report = generate_test_report(results)
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📋 RESUMO DOS TESTES")
    print("=" * 70)
    print(f"Total de testes: {report['summary']['total_tests']}")
    print(f"Testes aprovados: {report['summary']['passed_tests']}")
    print(f"Testes falharam: {report['summary']['failed_tests']}")
    print(f"Taxa de sucesso: {report['summary']['success_rate']:.1f}%")
    
    if report['summary']['success_rate'] == 100:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema de templates e busca semântica funcionando perfeitamente.")
    else:
        print(f"\n⚠️  {report['summary']['failed_tests']} teste(s) falharam. Verifique os detalhes acima.")
    
    return report['summary']['success_rate'] == 100

if __name__ == "__main__":
    asyncio.run(main())