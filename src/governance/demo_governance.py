#!/usr/bin/env python3
"""
Demo do Sistema de Governança RAG

Este script demonstra o uso completo do sistema de governança,
incluindo monitoramento de cobertura, análise de fontes,
detecção de obsolescência e dashboard unificado.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(str(Path(__file__).parent.parent))

from governance import (
    coverage_monitor,
    source_analyzer, 
    obsolescence_detector,
    governance_dashboard
)

def demo_coverage_monitoring():
    """Demonstra o monitoramento de cobertura"""
    print("\n" + "="*60)
    print("📊 DEMONSTRAÇÃO: MONITORAMENTO DE COBERTURA")
    print("="*60)
    
    # Simula algumas consultas
    sample_queries = [
        "Como implementar autenticação JWT em Next.js?",
        "Configurar Tailwind CSS com componentes Shadcn/UI",
        "Melhores práticas para testes E2E com Playwright",
        "Como otimizar performance em React com useMemo?",
        "Implementar dark mode com Tailwind CSS",
        "Configurar ESLint e Prettier em projeto TypeScript",
        "Como usar React Query para cache de dados?",
        "Implementar upload de arquivos com Next.js API"
    ]
    
    print("\n🔍 Registrando consultas de exemplo...")
    for query in sample_queries:
        # Simula resultados para a query
        mock_results = [
            {"id": f"result_{i}", "score": 0.8 - (i * 0.1), "content": f"Resultado {i+1} para: {query[:30]}"}
            for i in range(3)  # 3 resultados por query
        ]
        coverage_monitor.analyze_query_coverage(query, mock_results)
        print(f"  ✓ {query[:50]}...")
    
    # Gera relatório de cobertura
    print("\n📈 Gerando relatório de cobertura...")
    coverage_report = coverage_monitor.generate_coverage_report()
    
    print(f"\n📊 RESULTADOS DE COBERTURA:")
    print(f"  • Cobertura Geral: {coverage_report.overall_coverage:.1%}")
    print(f"  • Total de Tópicos: {coverage_report.total_topics}")
    print(f"  • Tópicos Bem Cobertos: {coverage_report.well_covered_topics}")
    print(f"  • Tópicos Mal Cobertos: {coverage_report.poorly_covered_topics}")
    print(f"  • Lacunas de Cobertura: {len(coverage_report.coverage_gaps)}")
    
    if coverage_report.trending_topics:
        print(f"\n🔥 Tópicos em Alta:")
        for topic in coverage_report.trending_topics[:5]:
            print(f"  • {topic}")
    
    if coverage_report.coverage_gaps:
        print(f"\n⚠️ Principais Lacunas:")
        for gap in coverage_report.coverage_gaps[:3]:
            print(f"  • {gap}")
    
    if coverage_report.recommendations:
        print(f"\n💡 Recomendações:")
        for rec in coverage_report.recommendations[:3]:
            print(f"  • {rec}")

def demo_source_analysis():
    """Demonstra a análise de fontes"""
    print("\n" + "="*60)
    print("📚 DEMONSTRAÇÃO: ANÁLISE DE FONTES")
    print("="*60)
    
    # Simula dados de acesso a fontes
    sample_sources = [
        {"id": "nextjs-docs", "category": "framework", "access_count": 150, "last_accessed": datetime.now() - timedelta(hours=2)},
        {"id": "react-docs", "category": "library", "access_count": 200, "last_accessed": datetime.now() - timedelta(hours=1)},
        {"id": "tailwind-docs", "category": "styling", "access_count": 120, "last_accessed": datetime.now() - timedelta(hours=3)},
        {"id": "shadcn-ui", "category": "components", "access_count": 80, "last_accessed": datetime.now() - timedelta(hours=4)},
        {"id": "old-jquery-guide", "category": "library", "access_count": 5, "last_accessed": datetime.now() - timedelta(days=30)},
        {"id": "deprecated-api", "category": "api", "access_count": 2, "last_accessed": datetime.now() - timedelta(days=60)},
        {"id": "playwright-docs", "category": "testing", "access_count": 45, "last_accessed": datetime.now() - timedelta(hours=6)},
        {"id": "typescript-handbook", "category": "language", "access_count": 90, "last_accessed": datetime.now() - timedelta(hours=5)}
    ]
    
    print("\n📝 Registrando acessos a fontes...")
    for source in sample_sources:
        # Simula múltiplos acessos
        for _ in range(source["access_count"]):
            source_analyzer.record_source_access(
                source["id"], 
                source["category"],
                source["last_accessed"]
            )
        print(f"  ✓ {source['id']} ({source['access_count']} acessos)")
    
    # Gera relatório de análise
    print("\n📊 Gerando relatório de análise de fontes...")
    analysis_report = source_analyzer.generate_analysis_report()
    
    print(f"\n📈 RESULTADOS DA ANÁLISE:")
    print(f"  • Total de Fontes: {analysis_report.total_sources}")
    print(f"  • Fontes Ativas: {analysis_report.active_sources}")
    print(f"  • Fontes Obsoletas: {analysis_report.obsolete_sources}")
    print(f"  • Fontes de Alto Valor: {analysis_report.high_value_sources}")
    print(f"  • Fontes de Baixo Valor: {analysis_report.low_value_sources}")
    
    # Mostra fontes de alto valor
    high_value = source_analyzer.identify_high_value_sources()
    if high_value:
        print(f"\n⭐ Fontes de Alto Valor:")
        for source in high_value[:5]:
            print(f"  • {source['source_id']}: {source['usage_count']} acessos, score {source['overall_score']:.2f}")
    
    # Mostra fontes obsoletas
    obsolete = source_analyzer.identify_obsolete_sources()
    if obsolete:
        print(f"\n🗑️ Fontes Obsoletas:")
        for source in obsolete[:3]:
            print(f"  • {source['source_id']}: {', '.join(source['reasons'])}")
    
    if analysis_report.recommendations:
        print(f"\n💡 Recomendações:")
        for rec in analysis_report.recommendations[:3]:
            print(f"  • {rec}")

def demo_obsolescence_detection():
    """Demonstra a detecção de obsolescência"""
    print("\n" + "="*60)
    print("⚠️ DEMONSTRAÇÃO: DETECÇÃO DE OBSOLESCÊNCIA")
    print("="*60)
    
    # Simula fontes com conteúdo potencialmente obsoleto
    sample_sources = [
        {
            "id": "react-class-components",
            "content": "Como criar componentes React usando class components e componentDidMount",
            "metadata": {"category": "react", "last_updated": "2020-01-15"}
        },
        {
            "id": "jquery-ajax", 
            "content": "Fazendo requisições AJAX com jQuery $.ajax() e callbacks",
            "metadata": {"category": "javascript", "last_updated": "2019-06-10"}
        },
        {
            "id": "webpack-v4",
            "content": "Configurando Webpack 4 com babel-loader e css-loader",
            "metadata": {"category": "build-tools", "last_updated": "2021-03-20"}
        },
        {
            "id": "modern-react-hooks",
            "content": "Usando React Hooks: useState, useEffect, useContext e custom hooks",
            "metadata": {"category": "react", "last_updated": "2023-08-15"}
        },
        {
            "id": "nextjs-13-app-router",
            "content": "Next.js 13 App Router com Server Components e streaming",
            "metadata": {"category": "nextjs", "last_updated": "2023-10-01"}
        },
        {
            "id": "node-callbacks",
            "content": "Programação assíncrona em Node.js usando callbacks e error-first pattern",
            "metadata": {"category": "nodejs", "last_updated": "2018-12-05"}
        }
    ]
    
    print("\n🔍 Analisando fontes para detecção de obsolescência...")
    
    all_detections = []
    for source in sample_sources:
        detections = obsolescence_detector.scan_source(
            source["id"],
            source["content"],
            source["metadata"]
        )
        all_detections.extend(detections)
        
        if detections:
            print(f"  ⚠️ {source['id']}: {len(detections)} problemas detectados")
        else:
            print(f"  ✅ {source['id']}: nenhum problema detectado")
    
    # Gera relatório de obsolescência
    print("\n📊 Gerando relatório de obsolescência...")
    obsolescence_report = obsolescence_detector.generate_obsolescence_report()
    
    print(f"\n🚨 RESULTADOS DA DETECÇÃO:")
    print(f"  • Total de Detecções: {obsolescence_report.total_detections}")
    print(f"  • Problemas Críticos: {obsolescence_report.critical_issues}")
    print(f"  • Problemas de Alta Prioridade: {obsolescence_report.high_issues}")
    print(f"  • Problemas de Média Prioridade: {obsolescence_report.medium_issues}")
    print(f"  • Fontes Afetadas: {obsolescence_report.sources_with_issues}")
    
    # Mostra resumo por regra
    if obsolescence_report.summary_by_rule:
        print(f"\n📋 Resumo por Tipo de Problema:")
        for rule_id, count in list(obsolescence_report.summary_by_rule.items())[:5]:
            print(f"  • {rule_id}: {count} ocorrências")
    
    # Mostra detecções críticas
    critical_detections = [d for d in all_detections if d.severity == "critical"]
    if critical_detections:
        print(f"\n🔴 Problemas Críticos Detectados:")
        for detection in critical_detections[:3]:
            print(f"  • {detection.source_id}: {detection.rule_id}")
            print(f"    Descrição: {detection.description}")
            if detection.suggestion:
                print(f"    Sugestão: {detection.suggestion}")
    
    if obsolescence_report.recommendations:
        print(f"\n💡 Recomendações:")
        for rec in obsolescence_report.recommendations[:3]:
            print(f"  • {rec}")

def demo_governance_dashboard():
    """Demonstra o dashboard de governança unificado"""
    print("\n" + "="*60)
    print("🎛️ DEMONSTRAÇÃO: DASHBOARD DE GOVERNANÇA")
    print("="*60)
    
    print("\n🔄 Gerando dashboard unificado...")
    dashboard = governance_dashboard.generate_dashboard()
    
    print(f"\n📊 MÉTRICAS CONSOLIDADAS:")
    print(f"  • Score de Governança: {dashboard.metrics.governance_score:.1%}")
    print(f"  • Score de Saúde: {dashboard.metrics.health_score:.1%}")
    print(f"  • Score de Qualidade: {dashboard.metrics.quality_score:.1%}")
    
    print(f"\n🎯 Resumo de Cobertura:")
    print(f"  • Cobertura Geral: {dashboard.coverage_summary['overall_coverage']}")
    print(f"  • Total de Tópicos: {dashboard.coverage_summary['total_topics']}")
    print(f"  • Lacunas: {dashboard.coverage_summary['gaps_count']}")
    
    print(f"\n📚 Resumo de Fontes:")
    print(f"  • Total: {dashboard.source_summary['total_sources']}")
    print(f"  • Ativas: {dashboard.source_summary['active_sources']}")
    print(f"  • Obsoletas: {dashboard.source_summary['obsolete_sources']}")
    print(f"  • Alto Valor: {dashboard.source_summary['high_value_sources']}")
    
    print(f"\n⚠️ Resumo de Obsolescência:")
    print(f"  • Total de Detecções: {dashboard.obsolescence_summary['total_detections']}")
    print(f"  • Problemas Críticos: {dashboard.obsolescence_summary['critical_issues']}")
    print(f"  • Fontes Afetadas: {dashboard.obsolescence_summary['sources_affected']}")
    
    # Mostra alertas
    if dashboard.alerts:
        print(f"\n🚨 Alertas Ativos:")
        for alert in dashboard.alerts:
            icon = "🔴" if alert["type"] == "critical" else "🟡"
            print(f"  {icon} {alert['category'].title()}: {alert['message']}")
    else:
        print(f"\n✅ Nenhum alerta ativo")
    
    # Mostra recomendações principais
    if dashboard.recommendations:
        print(f"\n💡 Principais Recomendações:")
        for i, rec in enumerate(dashboard.recommendations[:5], 1):
            print(f"  {i}. {rec}")
    
    # Status de saúde
    print("\n🏥 Verificando status de saúde...")
    health_status = governance_dashboard.get_health_status()
    
    status_icons = {
        "excellent": "🟢",
        "good": "🟡", 
        "warning": "🟠",
        "critical": "🔴",
        "unknown": "⚪",
        "error": "❌"
    }
    
    icon = status_icons.get(health_status["status"], "❓")
    print(f"  {icon} Status: {health_status['status'].upper()}")
    print(f"  📝 {health_status['message']}")
    
    if "overall_health" in health_status:
        print(f"  📊 Saúde Geral: {health_status['overall_health']:.1%}")
    
    # Ações prioritárias
    print("\n🎯 Verificando ações prioritárias...")
    priority_actions = governance_dashboard.get_priority_actions()
    
    if priority_actions:
        print(f"\n⚡ Ações Prioritárias:")
        for i, action in enumerate(priority_actions[:5], 1):
            priority_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            icon = priority_icons.get(action["priority"], "⚪")
            print(f"  {i}. {icon} {action['action']}")
            print(f"     {action['description']} (Esforço: {action['estimated_effort']})")
    else:
        print(f"  ✅ Nenhuma ação prioritária necessária")

def demo_export_reports():
    """Demonstra a exportação de relatórios"""
    print("\n" + "="*60)
    print("📄 DEMONSTRAÇÃO: EXPORTAÇÃO DE RELATÓRIOS")
    print("="*60)
    
    print("\n📊 Exportando relatórios em diferentes formatos...")
    
    try:
        # Exporta em JSON
        print("\n📋 Exportando relatório JSON...")
        json_file = governance_dashboard.export_governance_report("json")
        print(f"  ✅ Relatório JSON salvo: {Path(json_file).name}")
        
        # Exporta em Markdown
        print("\n📝 Exportando relatório Markdown...")
        md_file = governance_dashboard.export_governance_report("markdown")
        print(f"  ✅ Relatório Markdown salvo: {Path(md_file).name}")
        
        # Exporta em HTML
        print("\n🌐 Exportando relatório HTML...")
        html_file = governance_dashboard.export_governance_report("html")
        print(f"  ✅ Relatório HTML salvo: {Path(html_file).name}")
        
        print(f"\n📁 Todos os relatórios foram salvos no diretório: data/governance/")
        
    except Exception as e:
        print(f"  ❌ Erro ao exportar relatórios: {e}")

def main():
    """Função principal da demonstração"""
    print("🎛️ SISTEMA DE GOVERNANÇA RAG - DEMONSTRAÇÃO COMPLETA")
    print("=" * 80)
    print("\nEste demo mostra todas as funcionalidades do sistema de governança:")
    print("• Monitoramento de cobertura de tópicos")
    print("• Análise de utilidade e relevância de fontes")
    print("• Detecção automática de conteúdo obsoleto")
    print("• Dashboard unificado com métricas consolidadas")
    print("• Exportação de relatórios em múltiplos formatos")
    
    try:
        # Executa todas as demonstrações
        demo_coverage_monitoring()
        demo_source_analysis()
        demo_obsolescence_detection()
        demo_governance_dashboard()
        demo_export_reports()
        
        print("\n" + "="*80)
        print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\n🎯 O sistema de governança está funcionando corretamente e oferece:")
        print("  • Monitoramento contínuo da qualidade do conhecimento")
        print("  • Identificação proativa de problemas e oportunidades")
        print("  • Métricas consolidadas para tomada de decisão")
        print("  • Relatórios detalhados para análise e auditoria")
        print("  • Alertas automáticos para problemas críticos")
        print("\n🚀 O sistema está pronto para integração com o RAG principal!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE A DEMONSTRAÇÃO: {e}")
        print("\n🔧 Verifique se todos os módulos estão instalados corretamente.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())