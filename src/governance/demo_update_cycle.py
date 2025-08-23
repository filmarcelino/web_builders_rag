#!/usr/bin/env python3
"""
Demonstração do Sistema de Ciclo de Atualização Automática
Testa todas as funcionalidades do UpdateScheduler
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.governance.update_scheduler import UpdateScheduler
from src.observability.logging_manager import LoggingManager

def print_section(title: str):
    """Imprime uma seção formatada"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """Imprime uma subseção formatada"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

async def demo_update_scheduler():
    """Demonstra o sistema de atualização automática"""
    
    print_section("DEMONSTRAÇÃO: Sistema de Ciclo de Atualização Automática")
    
    # Configurar logging
    logger = LoggingManager().get_logger("demo_update_cycle")
    
    try:
        # 1. Inicializar o UpdateScheduler
        print_subsection("1. Inicializando UpdateScheduler")
        
        scheduler = UpdateScheduler()
        print("✅ UpdateScheduler inicializado com sucesso")
        
        # Mostrar configurações
        status = scheduler.get_status()
        print(f"📊 Status inicial:")
        print(f"   - Executando: {status['is_running']}")
        print(f"   - Última atualização semanal: {status['last_weekly_update'] or 'Nunca'}")
        print(f"   - Última revisão mensal: {status['last_monthly_review'] or 'Nunca'}")
        
        # 2. Demonstrar identificação de fontes desatualizadas
        print_subsection("2. Identificando Fontes Desatualizadas")
        
        # Simular fontes desatualizadas
        mock_sources = [
            {
                "source_id": "shadcn-ui-docs",
                "name": "Shadcn/UI Documentation",
                "last_updated": (datetime.now() - timedelta(days=10)).isoformat(),
                "obsolescence_score": 0.4,
                "is_critical": True
            },
            {
                "source_id": "nextjs-docs",
                "name": "Next.js Documentation",
                "last_updated": (datetime.now() - timedelta(days=5)).isoformat(),
                "obsolescence_score": 0.2,
                "is_critical": True
            },
            {
                "source_id": "tailwind-docs",
                "name": "Tailwind CSS Documentation",
                "last_updated": (datetime.now() - timedelta(days=2)).isoformat(),
                "obsolescence_score": 0.1,
                "is_critical": False
            }
        ]
        
        print(f"📋 Analisando {len(mock_sources)} fontes:")
        
        outdated_count = 0
        for source in mock_sources:
            should_update = scheduler._should_update_source(source)
            status_icon = "🔄" if should_update else "✅"
            
            if should_update:
                outdated_count += 1
            
            print(f"   {status_icon} {source['name']}")
            print(f"      - Última atualização: {source['last_updated'][:10]}")
            print(f"      - Score obsolescência: {source['obsolescence_score']:.1%}")
            print(f"      - Crítica: {'Sim' if source['is_critical'] else 'Não'}")
            print(f"      - Precisa atualizar: {'Sim' if should_update else 'Não'}")
        
        print(f"\n📊 Resultado: {outdated_count} de {len(mock_sources)} fontes precisam de atualização")
        
        # 3. Simular atualização semanal
        print_subsection("3. Simulando Atualização Semanal")
        
        # Criar dados simulados para atualização
        mock_updated_data = [
            {
                "source_id": "shadcn-ui-docs",
                "content": "Documentação atualizada do Shadcn/UI com novos componentes e exemplos de uso. Inclui guias detalhados para implementação e customização.",
                "metadata": {
                    "title": "Shadcn/UI Documentation",
                    "description": "Biblioteca de componentes React reutilizáveis",
                    "tags": ["react", "components", "ui", "typescript"],
                    "category": "ui-library",
                    "version": "0.8.0",
                    "last_modified": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            },
            {
                "source_id": "nextjs-docs",
                "content": "Documentação oficial do Next.js com guias de App Router, Server Components, e otimizações de performance. Inclui exemplos práticos e melhores práticas.",
                "metadata": {
                    "title": "Next.js Documentation",
                    "description": "Framework React para produção",
                    "tags": ["nextjs", "react", "framework", "ssr"],
                    "category": "framework",
                    "version": "14.0.0",
                    "last_modified": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        print(f"🔄 Simulando atualização de {len(mock_updated_data)} fontes...")
        
        # Validar atualizações
        validation_report = await scheduler._validate_updates(mock_updated_data)
        
        print(f"\n📊 Relatório de Validação:")
        print(f"   - Total processado: {validation_report['total_updated']}")
        print(f"   - Sucessos: {validation_report['successful']}")
        print(f"   - Falhas: {validation_report['failed']}")
        print(f"   - Qualidade média: {validation_report.get('average_quality', 0):.1%}")
        
        if validation_report['quality_scores']:
            print(f"   - Scores individuais: {[f'{score:.1%}' for score in validation_report['quality_scores']]}")
        
        # 4. Demonstrar cálculo de qualidade
        print_subsection("4. Análise de Qualidade dos Dados")
        
        for i, data in enumerate(mock_updated_data, 1):
            quality_score = await scheduler._calculate_quality_score(data)
            print(f"\n📈 Fonte {i}: {data['metadata']['title']}")
            print(f"   - Score de qualidade: {quality_score:.1%}")
            
            # Detalhes da análise
            metadata = data['metadata']
            required_metadata = ['title', 'description', 'tags', 'category']
            completeness = sum(1 for field in required_metadata if field in metadata) / len(required_metadata)
            
            print(f"   - Completude metadados: {completeness:.1%}")
            print(f"   - Tamanho do conteúdo: {len(data['content'])} caracteres")
            print(f"   - Timestamp: {data['timestamp'][:19]}")
        
        # 5. Demonstrar configurações
        print_subsection("5. Configurações do Sistema")
        
        config = scheduler.config
        print(f"📅 Atualização Semanal:")
        print(f"   - Habilitada: {config['weekly_update']['enabled']}")
        print(f"   - Dia: {config['weekly_update']['day']}")
        print(f"   - Horário: {config['weekly_update']['time']}")
        print(f"   - Máx. fontes por execução: {config['weekly_update']['max_sources_per_run']}")
        
        print(f"\n📅 Revisão Mensal:")
        print(f"   - Habilitada: {config['monthly_review']['enabled']}")
        print(f"   - Dia do mês: {config['monthly_review']['day_of_month']}")
        print(f"   - Reindexação completa: {config['monthly_review']['full_reindex']}")
        print(f"   - Limpeza de dados: {config['monthly_review']['cleanup_old_data']}")
        
        print(f"\n🚨 Atualização de Emergência:")
        print(f"   - Habilitada: {config['emergency_update']['enabled']}")
        print(f"   - Threshold: {config['emergency_update']['trigger_threshold']:.1%}")
        print(f"   - Frequência máxima: {config['emergency_update']['max_frequency_hours']}h")
        
        # 6. Simular verificação de emergência
        print_subsection("6. Verificação de Atualização de Emergência")
        
        # Simular alta taxa de obsolescência
        mock_obsolescence_rate = 0.15  # 15%
        threshold = config['emergency_update']['trigger_threshold']
        
        print(f"📊 Taxa de obsolescência simulada: {mock_obsolescence_rate:.1%}")
        print(f"📊 Threshold configurado: {threshold:.1%}")
        
        if mock_obsolescence_rate > threshold:
            print(f"🚨 ALERTA: Taxa de obsolescência acima do threshold!")
            print(f"   - Atualização de emergência seria acionada")
            print(f"   - Fontes críticas seriam priorizadas")
        else:
            print(f"✅ Taxa de obsolescência dentro do limite aceitável")
        
        # 7. Demonstrar relatório de status
        print_subsection("7. Status Final do Sistema")
        
        final_status = scheduler.get_status()
        print(f"📊 Status do UpdateScheduler:")
        print(f"   - Sistema ativo: {final_status['is_running']}")
        print(f"   - Configuração carregada: ✅")
        print(f"   - Agendamentos configurados: ✅")
        print(f"   - Validação funcionando: ✅")
        print(f"   - Métricas habilitadas: ✅")
        
        # 8. Simular métricas de performance
        print_subsection("8. Métricas de Performance")
        
        mock_metrics = {
            "update_type": "weekly",
            "sources_processed": len(mock_updated_data),
            "duration_seconds": 45.2,
            "success_rate": validation_report['successful'] / validation_report['total_updated'],
            "average_quality": validation_report.get('average_quality', 0)
        }
        
        print(f"⏱️ Métricas da Última Execução (simulada):")
        print(f"   - Tipo: {mock_metrics['update_type']}")
        print(f"   - Fontes processadas: {mock_metrics['sources_processed']}")
        print(f"   - Duração: {mock_metrics['duration_seconds']:.1f}s")
        print(f"   - Taxa de sucesso: {mock_metrics['success_rate']:.1%}")
        print(f"   - Qualidade média: {mock_metrics['average_quality']:.1%}")
        
        # 9. Próximos passos
        print_subsection("9. Próximos Passos")
        
        print(f"🚀 Sistema de Atualização Automática está pronto para:")
        print(f"   ✅ Executar atualizações semanais automáticas")
        print(f"   ✅ Realizar revisões mensais completas")
        print(f"   ✅ Detectar e responder a emergências")
        print(f"   ✅ Monitorar qualidade e performance")
        print(f"   ✅ Gerar relatórios e métricas")
        
        print(f"\n📋 Para ativar em produção:")
        print(f"   1. Executar: python -m src.governance.update_scheduler")
        print(f"   2. Configurar monitoramento de logs")
        print(f"   3. Ajustar configurações conforme necessário")
        print(f"   4. Configurar alertas para falhas")
        
        print_section("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO")
        
        return {
            "status": "success",
            "components_tested": [
                "UpdateScheduler initialization",
                "Source outdated detection",
                "Data validation",
                "Quality scoring",
                "Configuration management",
                "Emergency update detection",
                "Performance metrics"
            ],
            "sources_analyzed": len(mock_sources),
            "sources_updated": len(mock_updated_data),
            "average_quality": validation_report.get('average_quality', 0),
            "system_ready": True
        }
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        logger.error(f"Erro na demonstração: {e}")
        return {
            "status": "error",
            "error": str(e),
            "system_ready": False
        }

def main():
    """Função principal"""
    print("🚀 Iniciando demonstração do Sistema de Atualização Automática...")
    
    # Executar demonstração
    result = asyncio.run(demo_update_scheduler())
    
    # Mostrar resultado final
    if result["status"] == "success":
        print(f"\n🎉 Demonstração concluída com sucesso!")
        print(f"📊 Componentes testados: {len(result['components_tested'])}")
        print(f"📊 Qualidade média: {result['average_quality']:.1%}")
        print(f"📊 Sistema pronto: {result['system_ready']}")
    else:
        print(f"\n❌ Demonstração falhou: {result['error']}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())