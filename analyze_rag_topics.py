#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar os assuntos que o RAG está apto a abordar
"""

import requests
import json
import time
from typing import List, Dict, Any

# Configuração da API
RAG_URL = "http://localhost:8000/search"
API_KEY = "050118045"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Categorias de tópicos para testar
TEST_TOPICS = {
    "Web Development": [
        "HTML CSS JavaScript",
        "React components",
        "Vue.js framework",
        "Angular development",
        "Node.js backend",
        "Express.js server",
        "web app builders",
        "frontend frameworks",
        "responsive design",
        "web APIs REST"
    ],
    "Programming Languages": [
        "Python programming",
        "JavaScript ES6",
        "TypeScript types",
        "Ruby on Rails",
        "Java Spring",
        "C++ development",
        "Go programming",
        "Rust language"
    ],
    "Database & Backend": [
        "SQL database",
        "MongoDB NoSQL",
        "PostgreSQL",
        "Redis cache",
        "GraphQL API",
        "microservices architecture",
        "Docker containers",
        "Kubernetes orchestration"
    ],
    "Mobile Development": [
        "React Native",
        "Flutter development",
        "iOS Swift",
        "Android Kotlin",
        "mobile app development",
        "cross-platform development"
    ],
    "DevOps & Tools": [
        "Git version control",
        "CI/CD pipeline",
        "AWS cloud",
        "Azure services",
        "Linux administration",
        "Nginx configuration",
        "monitoring logging"
    ],
    "Data Science & AI": [
        "machine learning",
        "data analysis",
        "artificial intelligence",
        "neural networks",
        "data visualization",
        "pandas numpy",
        "TensorFlow PyTorch"
    ],
    "UI/UX & Design": [
        "user interface design",
        "user experience",
        "CSS animations",
        "design systems",
        "accessibility WCAG",
        "responsive layouts",
        "CSS Grid Flexbox"
    ]
}

def query_rag(query: str, limit: int = 3) -> Dict[str, Any]:
    """Faz uma consulta ao RAG e retorna os resultados"""
    try:
        payload = {
            "query": query,
            "limit": limit,
            "include_metadata": True
        }
        
        response = requests.post(RAG_URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        return {"error": str(e), "query": query}

def analyze_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa a qualidade dos resultados"""
    if "error" in results:
        return {"quality": "error", "relevance": 0, "details": results["error"]}
    
    if "items" not in results or not results["items"]:
        return {"quality": "no_results", "relevance": 0, "details": "Nenhum resultado encontrado"}
    
    items = results["items"]
    total_score = sum(item.get("score", 0) for item in items)
    avg_score = total_score / len(items) if items else 0
    
    # Classifica a qualidade baseada no score médio
    if avg_score >= 0.7:
        quality = "excellent"
    elif avg_score >= 0.5:
        quality = "good"
    elif avg_score >= 0.3:
        quality = "fair"
    elif avg_score >= 0.1:
        quality = "poor"
    else:
        quality = "very_poor"
    
    return {
        "quality": quality,
        "relevance": avg_score,
        "total_results": len(items),
        "details": f"Score médio: {avg_score:.4f}, {len(items)} resultados"
    }

def main():
    print("🔍 Analisando assuntos que o RAG está apto a abordar...\n")
    
    category_results = {}
    overall_stats = {
        "total_queries": 0,
        "successful_queries": 0,
        "quality_distribution": {"excellent": 0, "good": 0, "fair": 0, "poor": 0, "very_poor": 0, "error": 0, "no_results": 0}
    }
    
    for category, topics in TEST_TOPICS.items():
        print(f"📂 Categoria: {category}")
        category_results[category] = []
        
        for topic in topics:
            print(f"  🔎 Testando: {topic}")
            
            # Faz a consulta
            results = query_rag(topic)
            analysis = analyze_results(results)
            
            # Atualiza estatísticas
            overall_stats["total_queries"] += 1
            if "error" not in results:
                overall_stats["successful_queries"] += 1
            
            quality = analysis["quality"]
            overall_stats["quality_distribution"][quality] += 1
            
            # Armazena resultado
            category_results[category].append({
                "topic": topic,
                "quality": quality,
                "relevance": analysis["relevance"],
                "details": analysis["details"]
            })
            
            # Mostra resultado resumido
            quality_emoji = {
                "excellent": "🟢",
                "good": "🟡",
                "fair": "🟠",
                "poor": "🔴",
                "very_poor": "⚫",
                "error": "❌",
                "no_results": "⭕"
            }
            
            print(f"    {quality_emoji.get(quality, '❓')} {quality.upper()} - {analysis['details']}")
            
            # Pequena pausa para não sobrecarregar o sistema
            time.sleep(0.5)
        
        print()
    
    # Relatório final
    print("\n" + "="*80)
    print("📊 RELATÓRIO FINAL - CAPACIDADES DO RAG")
    print("="*80)
    
    print(f"\n📈 Estatísticas Gerais:")
    print(f"  • Total de consultas: {overall_stats['total_queries']}")
    print(f"  • Consultas bem-sucedidas: {overall_stats['successful_queries']}")
    print(f"  • Taxa de sucesso: {(overall_stats['successful_queries']/overall_stats['total_queries']*100):.1f}%")
    
    print(f"\n🎯 Distribuição de Qualidade:")
    for quality, count in overall_stats["quality_distribution"].items():
        if count > 0:
            percentage = (count / overall_stats["total_queries"]) * 100
            print(f"  • {quality.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
    
    print(f"\n📋 Análise por Categoria:")
    for category, results in category_results.items():
        excellent_count = sum(1 for r in results if r["quality"] == "excellent")
        good_count = sum(1 for r in results if r["quality"] == "good")
        total_count = len(results)
        
        coverage_score = (excellent_count * 2 + good_count) / (total_count * 2) * 100
        
        print(f"\n  🏷️  {category}:")
        print(f"    • Cobertura: {coverage_score:.1f}% ({excellent_count} excelentes, {good_count} bons de {total_count})")
        
        # Mostra os melhores tópicos da categoria
        best_topics = sorted(results, key=lambda x: x["relevance"], reverse=True)[:3]
        print(f"    • Melhores tópicos:")
        for topic in best_topics:
            print(f"      - {topic['topic']}: {topic['quality']} (score: {topic['relevance']:.4f})")
    
    print(f"\n🎯 Recomendações:")
    
    # Identifica categorias com boa cobertura
    good_categories = []
    poor_categories = []
    
    for category, results in category_results.items():
        excellent_count = sum(1 for r in results if r["quality"] in ["excellent", "good"])
        coverage = excellent_count / len(results)
        
        if coverage >= 0.5:
            good_categories.append(category)
        elif coverage < 0.3:
            poor_categories.append(category)
    
    if good_categories:
        print(f"  ✅ Categorias com boa cobertura: {', '.join(good_categories)}")
    
    if poor_categories:
        print(f"  ⚠️  Categorias com cobertura limitada: {', '.join(poor_categories)}")
    
    # Análise específica sobre web app builders
    print(f"\n🏗️  ANÁLISE ESPECÍFICA: Web App Builders")
    web_builder_topics = [r for r in category_results["Web Development"] if "web app builders" in r["topic"]]
    
    if web_builder_topics:
        topic = web_builder_topics[0]
        print(f"  • Qualidade: {topic['quality'].upper()}")
        print(f"  • Score de relevância: {topic['relevance']:.4f}")
        print(f"  • Detalhes: {topic['details']}")
        
        if topic["quality"] in ["excellent", "good"]:
            print(f"  ✅ O RAG tem boa capacidade para abordar web app builders")
        elif topic["quality"] in ["fair", "poor"]:
            print(f"  ⚠️  O RAG tem capacidade limitada para abordar web app builders")
        else:
            print(f"  ❌ O RAG tem dificuldades para abordar web app builders")
    
    print(f"\n" + "="*80)
    print("Análise concluída! 🎉")

if __name__ == "__main__":
    main()