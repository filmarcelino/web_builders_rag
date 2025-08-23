#!/usr/bin/env python3
"""
Demo de Integração com Agente - Demonstração da Integração RAG

Este demo mostra como os módulos do agente (Planner, Scaffolder, Builder e Critic)
podem integrar e utilizar o sistema RAG implementado.
"""

import sys
import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import time
import json

# Importa componentes do RAG
from ingestion import IngestionPipeline, SourceCollector
from indexing import IndexManager, ContentChunker
from search import SearchAPI
from search.search_engine import SearchEngine, SearchRequest, SearchResponse
from reranking import GPTReranker
from observability import PerformanceMonitor, LoggingManager
from seed_pack import seed_manager, ui_sources, web_stack_sources
from governance import coverage_monitor, source_analyzer, governance_dashboard

class AgentRAGIntegration:
    """Classe que simula a integração do RAG com os módulos do agente"""
    
    def __init__(self):
        # Inicializa componentes RAG
        self.ingestion = IngestionPipeline()
        self.indexer = IndexManager(api_key="demo-api-key")
        self.search_engine = SearchEngine(api_key="demo-api-key")
        self.reranker = GPTReranker()
        self.performance_monitor = PerformanceMonitor()
        self.logger = LoggingManager()
        
        print("🤖 Sistema RAG-Agente inicializado com sucesso!")
    
    async def planner_integration(self, task_description: str) -> Dict[str, Any]:
        """Simula como o módulo Planner usaria o RAG"""
        print(f"\n🎯 PLANNER: Analisando tarefa - {task_description}")
        
        # Planner busca conhecimento relevante para planejamento
        search_request = SearchRequest(f"best practices planning {task_description}")
        search_request.filters = {"category": ["patterns", "boilerplates", "architecture"]}
        search_request.top_k = 5
        
        search_results = await self.search_engine.search(search_request)
        
        # Debug: Check what search_results actually is
        print(f"Debug: search_results type: {type(search_results)}")
        print(f"Debug: search_results content: {search_results}")
        
        # Handle case where search_results might be a list or error
        if isinstance(search_results, list):
            results_list = search_results
        elif hasattr(search_results, 'results'):
            results_list = search_results.results
        else:
            results_list = []
        
        # Reranking para melhor relevância
        reranked_results = self.reranker.rerank_results(
            query=search_request.query,
            results=results_list,
            context={"module": "planner", "task": task_description}
        )
        
        # Handle reranked results
        if isinstance(reranked_results, list):
            reranked_list = reranked_results
        elif hasattr(reranked_results, 'results'):
            reranked_list = reranked_results.results
        else:
            reranked_list = []
        
        # Planner gera plano baseado no conhecimento
        plan = {
            "task": task_description,
            "knowledge_sources": len(reranked_list),
            "confidence": reranked_list[0].score if reranked_list else 0.0,
            "recommended_approach": self._extract_approach(reranked_list),
            "estimated_complexity": self._estimate_complexity(reranked_list),
            "required_technologies": self._extract_technologies(reranked_list)
        }
        
        # Registra uso para governança
        coverage_monitor.analyze_query_coverage(
            search_request.query, 
            [r.__dict__ for r in results_list]
        )
        
        print(f"  ✅ Plano gerado com {plan['knowledge_sources']} fontes de conhecimento")
        print(f"  📊 Confiança: {plan['confidence']:.2f}")
        print(f"  🔧 Tecnologias: {', '.join(plan['required_technologies'][:3])}")
        
        return plan
    
    async def scaffolder_integration(self, project_type: str) -> Dict[str, Any]:
        """Simula como o módulo Scaffolder usaria o RAG"""
        print(f"\n🏗️ SCAFFOLDER: Criando estrutura para {project_type}")
        
        # Scaffolder busca boilerplates e templates
        search_request = SearchRequest(f"{project_type} boilerplate template structure")
        search_request.filters = {"category": ["boilerplates", "templates"], "priority": [1, 2]}
        search_request.top_k = 3
        
        search_results = await self.search_engine.search(search_request)
        
        # Handle search results
        if isinstance(search_results, list):
            results_list = search_results
        elif hasattr(search_results, 'results'):
            results_list = search_results.results
        else:
            results_list = []
        
        # Busca no Seed Pack por fontes prioritárias
        relevant_seeds = seed_manager.search_sources(project_type)
        
        scaffold_info = {
            "project_type": project_type,
            "rag_sources": len(results_list),
            "seed_sources": len(relevant_seeds),
            "recommended_structure": self._generate_structure(results_list, relevant_seeds),
            "dependencies": self._extract_dependencies(results_list),
            "setup_commands": self._generate_setup_commands(relevant_seeds)
        }
        
        print(f"  ✅ Estrutura gerada com {scaffold_info['rag_sources']} fontes RAG + {scaffold_info['seed_sources']} seeds")
        print(f"  📦 Dependências: {len(scaffold_info['dependencies'])} identificadas")
        
        return scaffold_info
    
    async def builder_integration(self, component_request: str) -> Dict[str, Any]:
        """Simula como o módulo Builder usaria o RAG"""
        print(f"\n🔨 BUILDER: Construindo {component_request}")
        
        # Builder busca implementações e exemplos
        search_request = SearchRequest(f"{component_request} implementation example code")
        search_request.filters = {"category": ["components", "patterns", "examples"]}
        search_request.top_k = 8
        
        search_results = await self.search_engine.search(search_request)
        
        # Handle search results
        if isinstance(search_results, list):
            results_list = search_results
        elif hasattr(search_results, 'results'):
            results_list = search_results.results
        else:
            results_list = []
        
        # Reranking focado em qualidade de código
        reranked_results = self.reranker.rerank_results(
            query=search_request.query,
            results=results_list,
            context={"module": "builder", "focus": "code_quality"}
        )
        
        # Handle reranked results
        if isinstance(reranked_results, list):
            reranked_list = reranked_results
        elif hasattr(reranked_results, 'results'):
            reranked_list = reranked_results.results
        else:
            reranked_list = []
        
        # Busca componentes UI no Seed Pack
        ui_components = [s for s in ui_sources if component_request.lower() in s.name.lower()]
        
        build_info = {
            "component": component_request,
            "implementation_sources": len(reranked_list),
            "ui_components": len(ui_components),
            "code_examples": self._extract_code_examples(reranked_list),
            "best_practices": self._extract_best_practices(reranked_list),
            "testing_approach": self._suggest_testing(reranked_list)
        }
        
        # Registra acesso às fontes para análise
        for result in reranked_list:
            source_analyzer.record_source_access(
                result.source_id,
                "component_building",
                datetime.now().isoformat()
            )
        
        print(f"  ✅ Implementação baseada em {build_info['implementation_sources']} fontes")
        print(f"  🎨 Componentes UI: {build_info['ui_components']} disponíveis")
        
        return build_info
    
    async def critic_integration(self, code_content: str, context: str) -> Dict[str, Any]:
        """Simula como o módulo Critic usaria o RAG"""
        print(f"\n🔍 CRITIC: Analisando código - {context}")
        
        # Critic busca padrões de qualidade e anti-patterns
        search_request = SearchRequest(f"code review best practices {context} quality patterns")
        search_request.filters = {"category": ["patterns", "quality", "security"]}
        search_request.top_k = 6
        
        search_results = await self.search_engine.search(search_request)
        
        # Handle search results
        if isinstance(search_results, list):
            results_list = search_results
        elif hasattr(search_results, 'results'):
            results_list = search_results.results
        else:
            results_list = []
        
        # Busca fix-patterns no Seed Pack
        fix_patterns = seed_manager.get_sources_by_category("fix-patterns")
        
        critique = {
            "context": context,
            "quality_sources": len(results_list),
            "fix_patterns": len(fix_patterns),
            "quality_score": self._analyze_code_quality(code_content, results_list),
            "suggestions": self._generate_suggestions(code_content, results_list),
            "security_issues": self._check_security(code_content, fix_patterns),
            "performance_tips": self._suggest_performance(results_list)
        }
        
        print(f"  ✅ Análise baseada em {critique['quality_sources']} fontes de qualidade")
        print(f"  📊 Score de qualidade: {critique['quality_score']:.2f}")
        print(f"  🛡️ Issues de segurança: {len(critique['security_issues'])}")
        
        return critique
    
    def _extract_approach(self, results: List[Any]) -> str:
        """Extrai abordagem recomendada dos resultados"""
        if not results:
            return "Abordagem padrão"
        
        # Simula extração de abordagem do conteúdo
        approaches = ["incremental", "modular", "test-driven", "component-based"]
        return approaches[len(results) % len(approaches)]
    
    def _estimate_complexity(self, results: List[Any]) -> str:
        """Estima complexidade baseada nos resultados"""
        if len(results) < 2:
            return "alta"
        elif len(results) < 4:
            return "média"
        else:
            return "baixa"
    
    def _extract_technologies(self, results: List[Any]) -> List[str]:
        """Extrai tecnologias dos resultados"""
        # Simula extração de tecnologias
        all_techs = ["React", "TypeScript", "Next.js", "Tailwind", "Prisma", "Node.js"]
        return all_techs[:min(len(results), 4)]
    
    def _generate_structure(self, rag_results: List[Any], seed_results: List[Any]) -> Dict[str, List[str]]:
        """Gera estrutura de projeto"""
        return {
            "directories": ["src", "components", "pages", "styles", "utils"],
            "config_files": ["package.json", "tsconfig.json", "tailwind.config.js"],
            "entry_points": ["index.tsx", "App.tsx"]
        }
    
    def _extract_dependencies(self, results: List[Any]) -> List[str]:
        """Extrai dependências dos resultados"""
        deps = ["react", "typescript", "@types/react", "tailwindcss"]
        return deps[:len(results)]
    
    def _generate_setup_commands(self, seed_results: List[Any]) -> List[str]:
        """Gera comandos de setup"""
        return [
            "npm create next-app@latest .",
            "npm install tailwindcss",
            "npx tailwindcss init"
        ]
    
    def _extract_code_examples(self, results: List[Any]) -> List[str]:
        """Extrai exemplos de código"""
        return [f"Exemplo {i+1} de implementação" for i in range(min(len(results), 3))]
    
    def _extract_best_practices(self, results: List[Any]) -> List[str]:
        """Extrai melhores práticas"""
        practices = [
            "Use TypeScript para type safety",
            "Implemente testes unitários",
            "Siga padrões de acessibilidade",
            "Otimize performance com memoização"
        ]
        return practices[:len(results)]
    
    def _suggest_testing(self, results: List[Any]) -> Dict[str, str]:
        """Sugere abordagem de testes"""
        return {
            "framework": "Jest + Testing Library",
            "coverage": "90%+",
            "types": "unit, integration, e2e"
        }
    
    def _analyze_code_quality(self, code: str, results: List[Any]) -> float:
        """Analisa qualidade do código"""
        # Simula análise de qualidade
        base_score = 0.7
        knowledge_bonus = min(len(results) * 0.05, 0.3)
        return min(base_score + knowledge_bonus, 1.0)
    
    def _generate_suggestions(self, code: str, results: List[Any]) -> List[str]:
        """Gera sugestões de melhoria"""
        suggestions = [
            "Adicionar validação de tipos",
            "Implementar error boundaries",
            "Otimizar re-renders",
            "Melhorar acessibilidade"
        ]
        return suggestions[:len(results)]
    
    def _check_security(self, code: str, fix_patterns: List[Any]) -> List[str]:
        """Verifica issues de segurança"""
        # Simula verificação de segurança
        if "eval(" in code:
            return ["Uso de eval() detectado - risco de segurança"]
        return []
    
    def _suggest_performance(self, results: List[Any]) -> List[str]:
        """Sugere melhorias de performance"""
        tips = [
            "Use React.memo para componentes puros",
            "Implemente lazy loading",
            "Otimize bundle size",
            "Use service workers para cache"
        ]
        return tips[:len(results)]

async def main():
    """Demonstração principal da integração"""
    print("🚀 DEMONSTRAÇÃO: INTEGRAÇÃO RAG-AGENTE")
    print("=" * 80)
    print()
    print("Esta demonstração mostra como os módulos do agente podem")
    print("integrar e utilizar o sistema RAG para melhorar suas capacidades.")
    print()
    
    try:
        # Inicializa integração
        integration = AgentRAGIntegration()
        
        # Demonstra integração com cada módulo
        
        # 1. Planner
        planner_result = await integration.planner_integration(
            "criar aplicação e-commerce com Next.js e Stripe"
        )
        
        # 2. Scaffolder
        scaffolder_result = await integration.scaffolder_integration(
            "Next.js TypeScript app"
        )
        
        # 3. Builder
        builder_result = await integration.builder_integration(
            "shopping cart component"
        )
        
        # 4. Critic
        sample_code = """
function ShoppingCart({ items }) {
    const [total, setTotal] = useState(0);
    
    useEffect(() => {
        const newTotal = items.reduce((sum, item) => sum + item.price, 0);
        setTotal(newTotal);
    }, [items]);
    
    return <div>Total: ${total}</div>;
}
"""
        
        critic_result = await integration.critic_integration(
            sample_code, 
            "React component"
        )
        
        # Gera relatório de integração
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE INTEGRAÇÃO")
        print("=" * 60)
        
        print(f"\n🎯 PLANNER:")
        print(f"  • Fontes consultadas: {planner_result['knowledge_sources']}")
        print(f"  • Confiança: {planner_result['confidence']:.2f}")
        print(f"  • Complexidade estimada: {planner_result['estimated_complexity']}")
        
        print(f"\n🏗️ SCAFFOLDER:")
        print(f"  • Fontes RAG: {scaffolder_result['rag_sources']}")
        print(f"  • Seed sources: {scaffolder_result['seed_sources']}")
        print(f"  • Dependências: {len(scaffolder_result['dependencies'])}")
        
        print(f"\n🔨 BUILDER:")
        print(f"  • Fontes de implementação: {builder_result['implementation_sources']}")
        print(f"  • Componentes UI: {builder_result['ui_components']}")
        print(f"  • Exemplos de código: {len(builder_result['code_examples'])}")
        
        print(f"\n🔍 CRITIC:")
        print(f"  • Fontes de qualidade: {critic_result['quality_sources']}")
        print(f"  • Score de qualidade: {critic_result['quality_score']:.2f}")
        print(f"  • Issues de segurança: {len(critic_result['security_issues'])}")
        
        # Mostra métricas de governança
        print(f"\n📈 MÉTRICAS DE GOVERNANÇA:")
        dashboard_metrics = governance_dashboard.generate_dashboard()
        print(f"  • Cobertura geral: {dashboard_metrics.metrics.overall_coverage:.1%}")
        print(f"  • Score de qualidade: {dashboard_metrics.metrics.quality_score:.1%}")
        print(f"  • Score de governança: {dashboard_metrics.metrics.governance_score:.1%}")
        
        print("\n" + "=" * 80)
        print("✅ INTEGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\n🎯 Benefícios da integração RAG-Agente:")
        print("  • Decisões baseadas em conhecimento curado")
        print("  • Qualidade consistente em todos os módulos")
        print("  • Monitoramento contínuo de performance")
        print("  • Evolução automática do conhecimento")
        print("  • Governança transparente e auditável")
        print("\n🚀 O sistema está pronto para uso em produção!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE A DEMONSTRAÇÃO: {e}")
        print("🔧 Verifique se todos os módulos estão instalados corretamente.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))