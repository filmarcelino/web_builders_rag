#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar o conteúdo dos chunks do RAG
"""

import json
import os
from collections import Counter
import re

def analyze_chunks():
    print("🔍 Analisando conteúdo dos chunks do RAG...\n")
    
    # Lista arquivos de chunks
    chunk_files = [f for f in os.listdir('processed_corpus') 
                   if f.startswith('chunks_batch_') and f.endswith('.json')]
    
    if not chunk_files:
        print("❌ Nenhum arquivo de chunks encontrado!")
        return
    
    print(f"📁 Encontrados {len(chunk_files)} arquivos de chunks")
    
    # Analisa uma amostra de arquivos
    sample_files = chunk_files[:5]  # Primeiros 5 arquivos
    
    all_chunks = []
    content_types = Counter()
    topics_found = Counter()
    
    for file_name in sample_files:
        try:
            with open(f'processed_corpus/{file_name}', 'r', encoding='utf-8') as f:
                chunks = json.load(f)  # Os chunks são uma lista direta
                if isinstance(chunks, list):
                    all_chunks.extend(chunks)
                    print(f"📄 {file_name}: {len(chunks)} chunks")
                else:
                    print(f"⚠️  {file_name}: formato inesperado")
                
        except Exception as e:
            print(f"❌ Erro ao processar {file_name}: {e}")
    
    print(f"\n📊 Total de chunks analisados: {len(all_chunks)}")
    
    # Analisa tipos de conteúdo
    for chunk in all_chunks:
        content_type = chunk.get('content_type', 'unknown')
        content_types[content_type] += 1
        
        # Analisa tópicos no conteúdo
        content = chunk.get('content', '').lower()
        
        # Procura por tópicos relacionados a desenvolvimento web
        web_topics = {
            'javascript': ['javascript', 'js', 'node.js', 'nodejs'],
            'react': ['react', 'jsx', 'react native'],
            'html': ['html', 'html5', 'markup'],
            'css': ['css', 'css3', 'stylesheet', 'styling'],
            'python': ['python', 'django', 'flask'],
            'web_development': ['web development', 'frontend', 'backend', 'fullstack'],
            'frameworks': ['framework', 'library', 'angular', 'vue'],
            'database': ['database', 'sql', 'mongodb', 'postgresql'],
            'api': ['api', 'rest', 'graphql', 'endpoint'],
            'mobile': ['mobile', 'android', 'ios', 'app development']
        }
        
        for topic, keywords in web_topics.items():
            if any(keyword in content for keyword in keywords):
                topics_found[topic] += 1
    
    # Relatório
    print("\n" + "="*60)
    print("📋 RELATÓRIO DE ANÁLISE DE CONTEÚDO")
    print("="*60)
    
    print("\n🏷️  Tipos de Conteúdo:")
    for content_type, count in content_types.most_common():
        percentage = (count / len(all_chunks)) * 100
        print(f"  • {content_type}: {count} ({percentage:.1f}%)")
    
    print("\n🎯 Tópicos Identificados:")
    for topic, count in topics_found.most_common():
        percentage = (count / len(all_chunks)) * 100
        print(f"  • {topic.replace('_', ' ').title()}: {count} chunks ({percentage:.1f}%)")
    
    # Mostra exemplos de chunks
    print("\n📝 Exemplos de Chunks:")
    
    sample_chunks = all_chunks[:3]
    for i, chunk in enumerate(sample_chunks, 1):
        title = chunk.get('title', 'Sem título')[:50]
        content_preview = chunk.get('content', '')[:200].replace('\n', ' ')
        source = chunk.get('source', {}).get('url', 'Fonte não disponível')[:50]
        
        print(f"\n  📄 Chunk {i}:")
        print(f"    Título: {title}...")
        print(f"    Fonte: {source}...")
        print(f"    Prévia: {content_preview}...")
    
    # Análise específica para web app builders
    print("\n🏗️  ANÁLISE ESPECÍFICA: Web App Builders")
    
    web_builder_keywords = ['web app builder', 'website builder', 'drag and drop', 'no-code', 'low-code']
    web_builder_chunks = []
    
    for chunk in all_chunks:
        content = chunk.get('content', '').lower()
        if any(keyword in content for keyword in web_builder_keywords):
            web_builder_chunks.append(chunk)
    
    print(f"  • Chunks relacionados a web app builders: {len(web_builder_chunks)}")
    
    if web_builder_chunks:
        print(f"  • Exemplos encontrados:")
        for i, chunk in enumerate(web_builder_chunks[:2], 1):
            title = chunk.get('title', 'Sem título')[:60]
            print(f"    {i}. {title}...")
    else:
        print(f"  ⚠️  Poucos ou nenhum chunk específico sobre web app builders encontrado")
    
    # Recomendações
    print("\n💡 Recomendações:")
    
    total_web_related = sum(count for topic, count in topics_found.items() 
                           if topic in ['javascript', 'react', 'html', 'css', 'web_development', 'frameworks'])
    
    web_coverage = (total_web_related / len(all_chunks)) * 100 if all_chunks else 0
    
    print(f"  • Cobertura de desenvolvimento web: {web_coverage:.1f}%")
    
    if web_coverage > 30:
        print(f"  ✅ Boa cobertura de tópicos de desenvolvimento web")
    elif web_coverage > 15:
        print(f"  ⚠️  Cobertura moderada de tópicos de desenvolvimento web")
    else:
        print(f"  ❌ Cobertura limitada de tópicos de desenvolvimento web")
    
    if len(web_builder_chunks) < 5:
        print(f"  ⚠️  Conteúdo específico sobre web app builders é limitado")
        print(f"  💡 Considere adicionar mais conteúdo sobre ferramentas de criação de web apps")
    
    print(f"\n" + "="*60)
    print("Análise concluída! 🎉")

if __name__ == "__main__":
    analyze_chunks()