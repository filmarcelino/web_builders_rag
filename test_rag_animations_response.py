#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar especificamente as respostas do RAG sobre animações CSS
"""

import json
import os
from datetime import datetime
import subprocess
import sys

def test_animation_queries():
    """Testa o RAG com consultas específicas sobre animações"""
    
    # Consultas específicas sobre animações
    animation_queries = [
        "Como criar animações CSS avançadas com keyframes e transformações?",
        "Quais são as melhores práticas para efeitos de transição suaves?",
        "Como implementar animações de hover e focus em botões?",
        "Como criar animações de loading e spinners com CSS?",
        "Quais propriedades CSS usar para animações performáticas?"
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(animation_queries),
        "queries_tested": [],
        "animation_coverage_analysis": {},
        "summary": {}
    }
    
    print("🎬 Testando respostas do RAG para consultas sobre animações...")
    
    for i, query in enumerate(animation_queries, 1):
        print(f"\n📝 Testando consulta {i}/{len(animation_queries)}: {query[:50]}...")
        
        try:
            # Executa o script de simulação RAG
            result = subprocess.run([
                sys.executable, "simulate_rag_response.py", 
                "--query", query
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Carrega a resposta gerada
                if os.path.exists("rag_dashboard_demonstration.json"):
                    with open("rag_dashboard_demonstration.json", "r", encoding="utf-8") as f:
                        response_data = json.load(f)
                    
                    # Analisa a resposta para conteúdo de animação
                    animation_analysis = analyze_animation_content(response_data.get("rag_response", ""))
                    
                    query_result = {
                        "query": query,
                        "response_length": len(response_data.get("rag_response", "")),
                        "chunks_retrieved": response_data.get("relevant_chunks_count", 0),
                        "animation_keywords_found": animation_analysis["keywords_found"],
                        "animation_score": animation_analysis["score"],
                        "has_css_code": "```css" in response_data.get("rag_response", ""),
                        "has_keyframes": "@keyframes" in response_data.get("rag_response", ""),
                        "has_transitions": "transition" in response_data.get("rag_response", "").lower(),
                        "has_transforms": "transform" in response_data.get("rag_response", "").lower(),
                        "status": "success"
                    }
                    
                    results["queries_tested"].append(query_result)
                    print(f"   ✅ Sucesso - Score de animação: {animation_analysis['score']:.1f}/10")
                    
                else:
                    print(f"   ❌ Arquivo de resposta não encontrado")
                    results["queries_tested"].append({
                        "query": query,
                        "status": "file_not_found"
                    })
            else:
                print(f"   ❌ Erro na execução: {result.stderr}")
                results["queries_tested"].append({
                    "query": query,
                    "status": "execution_error",
                    "error": result.stderr
                })
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout na consulta")
            results["queries_tested"].append({
                "query": query,
                "status": "timeout"
            })
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            results["queries_tested"].append({
                "query": query,
                "status": "error",
                "error": str(e)
            })
    
    # Calcula estatísticas gerais
    successful_queries = [q for q in results["queries_tested"] if q.get("status") == "success"]
    
    if successful_queries:
        avg_animation_score = sum(q.get("animation_score", 0) for q in successful_queries) / len(successful_queries)
        avg_response_length = sum(q.get("response_length", 0) for q in successful_queries) / len(successful_queries)
        
        css_code_percentage = sum(1 for q in successful_queries if q.get("has_css_code", False)) / len(successful_queries) * 100
        keyframes_percentage = sum(1 for q in successful_queries if q.get("has_keyframes", False)) / len(successful_queries) * 100
        transitions_percentage = sum(1 for q in successful_queries if q.get("has_transitions", False)) / len(successful_queries) * 100
        transforms_percentage = sum(1 for q in successful_queries if q.get("has_transforms", False)) / len(successful_queries) * 100
        
        results["summary"] = {
            "successful_queries": len(successful_queries),
            "success_rate": len(successful_queries) / len(animation_queries) * 100,
            "average_animation_score": avg_animation_score,
            "average_response_length": avg_response_length,
            "css_code_coverage": css_code_percentage,
            "keyframes_coverage": keyframes_percentage,
            "transitions_coverage": transitions_percentage,
            "transforms_coverage": transforms_percentage,
            "overall_animation_quality": calculate_overall_quality(avg_animation_score, css_code_percentage, keyframes_percentage)
        }
        
        print(f"\n📊 RESULTADOS FINAIS:")
        print(f"   • Consultas bem-sucedidas: {len(successful_queries)}/{len(animation_queries)} ({len(successful_queries) / len(animation_queries) * 100:.1f}%)")
        print(f"   • Score médio de animação: {avg_animation_score:.1f}/10")
        print(f"   • Cobertura de código CSS: {css_code_percentage:.1f}%")
        print(f"   • Cobertura de keyframes: {keyframes_percentage:.1f}%")
        print(f"   • Cobertura de transitions: {transitions_percentage:.1f}%")
        print(f"   • Cobertura de transforms: {transforms_percentage:.1f}%")
        print(f"   • Qualidade geral: {results['summary']['overall_animation_quality']}")
    
    # Salva os resultados
    with open("rag_animations_response_test.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em 'rag_animations_response_test.json'")
    return results

def analyze_animation_content(response_text):
    """Analisa o conteúdo da resposta para palavras-chave de animação"""
    
    animation_keywords = {
        "keyframes": ["@keyframes", "keyframes", "animation-name"],
        "transitions": ["transition", "transition-duration", "transition-timing-function", "transition-delay"],
        "transforms": ["transform", "translate", "rotate", "scale", "skew"],
        "animations": ["animation", "animation-duration", "animation-iteration-count", "animation-direction"],
        "easing": ["ease", "ease-in", "ease-out", "ease-in-out", "cubic-bezier"],
        "effects": ["hover", "focus", "active", "opacity", "visibility"]
    }
    
    response_lower = response_text.lower()
    keywords_found = []
    category_scores = {}
    
    for category, keywords in animation_keywords.items():
        found_keywords = [kw for kw in keywords if kw.lower() in response_lower]
        keywords_found.extend(found_keywords)
        category_scores[category] = len(found_keywords)
    
    # Calcula score baseado na diversidade e quantidade de palavras-chave
    total_categories = len([cat for cat, score in category_scores.items() if score > 0])
    total_keywords = len(keywords_found)
    
    # Score de 0-10 baseado na cobertura
    score = min(10, (total_categories * 1.5) + (total_keywords * 0.3))
    
    return {
        "keywords_found": keywords_found,
        "category_scores": category_scores,
        "total_categories_covered": total_categories,
        "total_keywords_found": total_keywords,
        "score": score
    }

def calculate_overall_quality(animation_score, css_coverage, keyframes_coverage):
    """Calcula a qualidade geral das respostas sobre animações"""
    
    # Peso para diferentes aspectos
    weighted_score = (animation_score * 0.4) + (css_coverage * 0.03) + (keyframes_coverage * 0.05)
    
    if weighted_score >= 8:
        return "EXCELENTE"
    elif weighted_score >= 6:
        return "BOM"
    elif weighted_score >= 4:
        return "REGULAR"
    else:
        return "INSUFICIENTE"

if __name__ == "__main__":
    test_animation_queries()