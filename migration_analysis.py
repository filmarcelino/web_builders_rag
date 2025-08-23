#!/usr/bin/env python3
"""
Análise de Migração para Haystack AI

Este script analisa a estrutura RAG atual e verifica a compatibilidade
com o framework Haystack AI para uma possível migração.
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import importlib.util

try:
    from haystack import Pipeline, Document
    from haystack.components.retrievers import InMemoryBM25Retriever
    from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
    from haystack.components.generators import OpenAIGenerator
    from haystack.components.builders import PromptBuilder
    from haystack.document_stores import InMemoryDocumentStore
    from haystack.components.rankers import TransformersSimilarityRanker
    HAYSTACK_AVAILABLE = True
except ImportError as e:
    print(f"Erro ao importar Haystack: {e}")
    HAYSTACK_AVAILABLE = False

class MigrationAnalyzer:
    """Analisador de migração para Haystack AI"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analysis_results = {
            'haystack_compatibility': {},
            'migration_feasibility': {},
            'component_mapping': {},
            'required_changes': [],
            'benefits': [],
            'challenges': []
        }
    
    def analyze_current_structure(self) -> Dict[str, Any]:
        """Analisa a estrutura atual do projeto"""
        print("🔍 Analisando estrutura atual do projeto RAG...")
        
        structure = {
            'modules': {},
            'dependencies': [],
            'architecture_patterns': []
        }
        
        # Analisa módulos existentes
        src_path = self.project_root / 'src'
        if src_path.exists():
            for module_dir in src_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('__'):
                    structure['modules'][module_dir.name] = self._analyze_module(module_dir)
        
        # Analisa requirements.txt
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            with open(req_file, 'r') as f:
                structure['dependencies'] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        return structure
    
    def _analyze_module(self, module_path: Path) -> Dict[str, Any]:
        """Analisa um módulo específico"""
        module_info = {
            'files': [],
            'classes': [],
            'functions': [],
            'complexity': 'low'
        }
        
        for file_path in module_path.glob('*.py'):
            if file_path.name != '__init__.py':
                module_info['files'].append(file_path.name)
                
                # Análise básica do arquivo
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Conta classes e funções
                    class_count = content.count('class ')
                    func_count = content.count('def ')
                    
                    module_info['classes'].extend([f"{file_path.stem}.Class{i}" for i in range(class_count)])
                    module_info['functions'].extend([f"{file_path.stem}.func{i}" for i in range(func_count)])
                    
                    # Estima complexidade baseada no tamanho
                    lines = len(content.split('\n'))
                    if lines > 500:
                        module_info['complexity'] = 'high'
                    elif lines > 200:
                        module_info['complexity'] = 'medium'
                        
                except Exception as e:
                    print(f"Erro ao analisar {file_path}: {e}")
        
        return module_info
    
    def analyze_haystack_compatibility(self) -> Dict[str, Any]:
        """Analisa compatibilidade com Haystack AI"""
        print("🔄 Analisando compatibilidade com Haystack AI...")
        
        if not HAYSTACK_AVAILABLE:
            return {
                'status': 'error',
                'message': 'Haystack AI não está disponível',
                'compatibility_score': 0
            }
        
        compatibility = {
            'status': 'success',
            'haystack_version': self._get_haystack_version(),
            'compatible_components': [],
            'incompatible_components': [],
            'compatibility_score': 0
        }
        
        # Mapeia componentes atuais para Haystack
        component_mapping = {
            'ingestion': {
                'current': ['collector.py', 'normalizer.py', 'validator.py'],
                'haystack_equivalent': ['FileTypeClassifier', 'DocumentCleaner', 'DocumentSplitter'],
                'compatibility': 'high'
            },
            'indexing': {
                'current': ['chunker.py', 'embeddings.py', 'vector_indexer.py', 'text_indexer.py'],
                'haystack_equivalent': ['DocumentSplitter', 'DocumentEmbedder', 'DocumentStore', 'BM25Retriever'],
                'compatibility': 'high'
            },
            'search': {
                'current': ['search_engine.py', 'query_processor.py', 'search_cache.py'],
                'haystack_equivalent': ['Pipeline', 'PromptBuilder', 'InMemoryDocumentStore'],
                'compatibility': 'medium'
            },
            'reranking': {
                'current': ['reranker.py', 'rationale_generator.py'],
                'haystack_equivalent': ['TransformersSimilarityRanker', 'OpenAIGenerator'],
                'compatibility': 'medium'
            },
            'observability': {
                'current': ['metrics_collector.py', 'quality_evaluator.py'],
                'haystack_equivalent': ['Custom Components', 'Pipeline Callbacks'],
                'compatibility': 'low'
            }
        }
        
        # Calcula score de compatibilidade
        total_score = 0
        for module, info in component_mapping.items():
            if info['compatibility'] == 'high':
                score = 0.8
            elif info['compatibility'] == 'medium':
                score = 0.5
            else:
                score = 0.2
            
            total_score += score
            
            if score >= 0.5:
                compatibility['compatible_components'].append({
                    'module': module,
                    'score': score,
                    'haystack_components': info['haystack_equivalent']
                })
            else:
                compatibility['incompatible_components'].append({
                    'module': module,
                    'score': score,
                    'issues': ['Requires custom implementation', 'No direct equivalent']
                })
        
        compatibility['compatibility_score'] = total_score / len(component_mapping)
        self.analysis_results['component_mapping'] = component_mapping
        
        return compatibility
    
    def _get_haystack_version(self) -> str:
        """Obtém versão do Haystack"""
        try:
            import haystack
            return haystack.__version__
        except:
            return 'unknown'
    
    def create_migration_plan(self) -> Dict[str, Any]:
        """Cria plano de migração"""
        print("📋 Criando plano de migração...")
        
        plan = {
            'phases': [],
            'estimated_effort': {},
            'risks': [],
            'recommendations': []
        }
        
        # Fase 1: Preparação
        plan['phases'].append({
            'phase': 1,
            'name': 'Preparação e Setup',
            'duration': '1-2 dias',
            'tasks': [
                'Configurar ambiente Haystack',
                'Criar estrutura de projeto híbrida',
                'Implementar testes de compatibilidade'
            ]
        })
        
        # Fase 2: Migração de Ingestão
        plan['phases'].append({
            'phase': 2,
            'name': 'Migração do Sistema de Ingestão',
            'duration': '3-5 dias',
            'tasks': [
                'Migrar collector.py para Haystack FileTypeClassifier',
                'Adaptar normalizer.py para DocumentCleaner',
                'Integrar validator.py com Pipeline'
            ]
        })
        
        # Fase 3: Migração de Indexação
        plan['phases'].append({
            'phase': 3,
            'name': 'Migração do Sistema de Indexação',
            'duration': '5-7 dias',
            'tasks': [
                'Migrar chunker.py para DocumentSplitter',
                'Adaptar embeddings.py para DocumentEmbedder',
                'Configurar DocumentStore (FAISS/Elasticsearch)',
                'Migrar índices existentes'
            ]
        })
        
        # Fase 4: Migração de Busca
        plan['phases'].append({
            'phase': 4,
            'name': 'Migração do Sistema de Busca',
            'duration': '4-6 dias',
            'tasks': [
                'Criar Pipeline de busca híbrida',
                'Migrar query_processor.py para PromptBuilder',
                'Adaptar cache para Haystack',
                'Implementar API endpoints'
            ]
        })
        
        # Fase 5: Reranking e Observabilidade
        plan['phases'].append({
            'phase': 5,
            'name': 'Reranking e Observabilidade',
            'duration': '6-8 dias',
            'tasks': [
                'Implementar reranking como componente customizado',
                'Criar sistema de métricas com callbacks',
                'Migrar quality_evaluator.py',
                'Implementar logging e monitoramento'
            ]
        })
        
        # Fase 6: Testes e Otimização
        plan['phases'].append({
            'phase': 6,
            'name': 'Testes e Otimização',
            'duration': '3-5 dias',
            'tasks': [
                'Testes de integração completos',
                'Benchmarks de performance',
                'Otimização de pipelines',
                'Documentação da migração'
            ]
        })
        
        # Estimativa de esforço
        plan['estimated_effort'] = {
            'total_duration': '22-33 dias',
            'developer_days': '25-35 dias',
            'complexity': 'medium-high',
            'team_size_recommended': '2-3 desenvolvedores'
        }
        
        # Riscos identificados
        plan['risks'] = [
            {
                'risk': 'Perda de funcionalidades customizadas',
                'probability': 'medium',
                'impact': 'high',
                'mitigation': 'Implementar componentes customizados no Haystack'
            },
            {
                'risk': 'Degradação de performance',
                'probability': 'low',
                'impact': 'medium',
                'mitigation': 'Benchmarks e otimização contínua'
            },
            {
                'risk': 'Incompatibilidade de dados existentes',
                'probability': 'medium',
                'impact': 'medium',
                'mitigation': 'Scripts de migração de dados'
            }
        ]
        
        # Recomendações
        plan['recommendations'] = [
            'Manter sistema atual em paralelo durante migração',
            'Implementar migração incremental por módulo',
            'Criar testes de regressão abrangentes',
            'Documentar todas as customizações necessárias',
            'Considerar contribuir componentes customizados para Haystack'
        ]
        
        return plan
    
    def analyze_benefits_and_challenges(self) -> Dict[str, List[str]]:
        """Analisa benefícios e desafios da migração"""
        print("⚖️ Analisando benefícios e desafios...")
        
        benefits = [
            'Framework maduro e bem mantido com comunidade ativa',
            'Componentes pré-construídos para RAG (retrievers, generators, rankers)',
            'Pipeline visual e configurável',
            'Integração nativa com múltiplos LLMs e document stores',
            'Sistema de avaliação integrado',
            'Melhor escalabilidade e performance',
            'Redução de código customizado',
            'Suporte oficial para deployment em produção',
            'Integração com ferramentas de MLOps',
            'Documentação abrangente e exemplos'
        ]
        
        challenges = [
            'Curva de aprendizado do framework Haystack',
            'Necessidade de reimplementar funcionalidades customizadas',
            'Possível perda de controle granular sobre componentes',
            'Migração de dados e índices existentes',
            'Adaptação de APIs existentes',
            'Tempo e esforço significativo de migração',
            'Risco de introduzir bugs durante migração',
            'Dependência de framework externo',
            'Possível overhead de performance inicial',
            'Necessidade de treinamento da equipe'
        ]
        
        return {'benefits': benefits, 'challenges': challenges}
    
    def create_poc_example(self) -> str:
        """Cria exemplo de PoC com Haystack"""
        print("🧪 Criando exemplo de Proof of Concept...")
        
        poc_code = '''
#!/usr/bin/env python3
"""
Proof of Concept - RAG com Haystack AI

Este exemplo demonstra como implementar um pipeline RAG básico
usando Haystack AI, equivalente ao nosso sistema atual.
"""

from haystack import Pipeline, Document
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder
from haystack.document_stores import InMemoryDocumentStore
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.joiners import DocumentJoiner
from typing import List

class HaystackRAGPoC:
    """Proof of Concept do RAG usando Haystack AI"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.document_store = InMemoryDocumentStore()
        self.setup_pipelines()
    
    def setup_pipelines(self):
        """Configura pipelines de indexação e busca"""
        
        # Pipeline de Indexação
        self.indexing_pipeline = Pipeline()
        
        # Componentes de indexação
        doc_embedder = SentenceTransformersDocumentEmbedder(
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
        doc_embedder.warm_up()
        
        # Adiciona componentes ao pipeline
        self.indexing_pipeline.add_component("doc_embedder", doc_embedder)
        self.indexing_pipeline.add_component("doc_writer", self.document_store)
        
        # Conecta componentes
        self.indexing_pipeline.connect("doc_embedder.documents", "doc_writer.documents")
        
        # Pipeline de Busca RAG
        self.rag_pipeline = Pipeline()
        
        # Componentes de busca
        text_embedder = SentenceTransformersTextEmbedder(
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
        text_embedder.warm_up()
        
        retriever = InMemoryBM25Retriever(document_store=self.document_store)
        ranker = TransformersSimilarityRanker(model="cross-encoder/ms-marco-MiniLM-L-6-v2")
        ranker.warm_up()
        
        prompt_builder = PromptBuilder(
            template="""
            Baseado no contexto fornecido, responda à pergunta de forma precisa e útil.
            
            Contexto:
            {% for document in documents %}
                {{ document.content }}
            {% endfor %}
            
            Pergunta: {{ question }}
            
            Resposta:
            """
        )
        
        generator = OpenAIGenerator(
            api_key=self.openai_api_key,
            model="gpt-3.5-turbo",
            generation_kwargs={"max_tokens": 500, "temperature": 0.1}
        )
        
        # Adiciona componentes
        self.rag_pipeline.add_component("text_embedder", text_embedder)
        self.rag_pipeline.add_component("retriever", retriever)
        self.rag_pipeline.add_component("ranker", ranker)
        self.rag_pipeline.add_component("prompt_builder", prompt_builder)
        self.rag_pipeline.add_component("llm", generator)
        
        # Conecta componentes
        self.rag_pipeline.connect("text_embedder", "retriever")
        self.rag_pipeline.connect("retriever", "ranker")
        self.rag_pipeline.connect("ranker", "prompt_builder.documents")
        self.rag_pipeline.connect("prompt_builder", "llm")
    
    def index_documents(self, documents: List[Document]):
        """Indexa documentos"""
        result = self.indexing_pipeline.run({"doc_embedder": {"documents": documents}})
        return result
    
    def search(self, question: str, top_k: int = 5) -> dict:
        """Executa busca RAG"""
        result = self.rag_pipeline.run({
            "text_embedder": {"text": question},
            "retriever": {"query": question, "top_k": top_k},
            "ranker": {"query": question, "top_k": 3},
            "prompt_builder": {"question": question}
        })
        
        return {
            "answer": result["llm"]["replies"][0],
            "source_documents": result["ranker"]["documents"]
        }

# Exemplo de uso
if __name__ == "__main__":
    # Inicializa PoC
    rag = HaystackRAGPoC(openai_api_key="your-openai-key")
    
    # Documentos de exemplo
    docs = [
        Document(content="Haystack é um framework para construir aplicações de busca."),
        Document(content="RAG combina recuperação de informações com geração de texto."),
        Document(content="Python é uma linguagem de programação versátil.")
    ]
    
    # Indexa documentos
    rag.index_documents(docs)
    
    # Executa busca
    result = rag.search("O que é Haystack?")
    print(f"Resposta: {result['answer']}")
    print(f"Documentos fonte: {len(result['source_documents'])}")
'''
        
        return poc_code
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório completo de análise"""
        print("📊 Gerando relatório de análise...")
        
        # Executa todas as análises
        current_structure = self.analyze_current_structure()
        haystack_compatibility = self.analyze_haystack_compatibility()
        migration_plan = self.create_migration_plan()
        benefits_challenges = self.analyze_benefits_and_challenges()
        poc_example = self.create_poc_example()
        
        # Compila relatório
        report = {
            'analysis_timestamp': '2024-01-20T10:00:00Z',
            'project_path': str(self.project_root),
            'haystack_available': HAYSTACK_AVAILABLE,
            'current_structure': current_structure,
            'haystack_compatibility': haystack_compatibility,
            'migration_plan': migration_plan,
            'benefits': benefits_challenges['benefits'],
            'challenges': benefits_challenges['challenges'],
            'poc_example': poc_example,
            'recommendation': self._generate_recommendation(haystack_compatibility)
        }
        
        return report
    
    def _generate_recommendation(self, compatibility: Dict[str, Any]) -> Dict[str, Any]:
        """Gera recomendação final"""
        score = compatibility.get('compatibility_score', 0)
        
        if score >= 0.7:
            recommendation = {
                'decision': 'RECOMENDADO',
                'confidence': 'high',
                'reasoning': 'Alta compatibilidade com Haystack. Migração trará benefícios significativos.',
                'next_steps': [
                    'Implementar PoC com componentes críticos',
                    'Executar benchmarks de performance',
                    'Iniciar migração incremental'
                ]
            }
        elif score >= 0.5:
            recommendation = {
                'decision': 'RECOMENDADO COM RESSALVAS',
                'confidence': 'medium',
                'reasoning': 'Compatibilidade moderada. Requer análise mais detalhada de componentes específicos.',
                'next_steps': [
                    'Implementar PoC focado em componentes problemáticos',
                    'Avaliar esforço de desenvolvimento de componentes customizados',
                    'Considerar migração parcial'
                ]
            }
        else:
            recommendation = {
                'decision': 'NÃO RECOMENDADO NO MOMENTO',
                'confidence': 'high',
                'reasoning': 'Baixa compatibilidade. Esforço de migração pode não justificar benefícios.',
                'next_steps': [
                    'Manter sistema atual',
                    'Reavaliar em versões futuras do Haystack',
                    'Considerar adoção de componentes específicos'
                ]
            }
        
        return recommendation

def main():
    """Função principal"""
    print("🚀 Iniciando Análise de Migração para Haystack AI")
    print("=" * 50)
    
    # Inicializa analisador
    project_root = os.getcwd()
    analyzer = MigrationAnalyzer(project_root)
    
    # Gera relatório
    report = analyzer.generate_report()
    
    # Salva relatório
    report_file = Path(project_root) / 'migration_analysis_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Relatório salvo em: {report_file}")
    
    # Exibe resumo
    print("\n📊 RESUMO DA ANÁLISE")
    print("=" * 30)
    
    compatibility = report['haystack_compatibility']
    print(f"✅ Haystack Disponível: {report['haystack_available']}")
    
    if compatibility.get('status') == 'success':
        score = compatibility['compatibility_score']
        print(f"📈 Score de Compatibilidade: {score:.2f} ({score*100:.1f}%)")
        print(f"🔧 Componentes Compatíveis: {len(compatibility['compatible_components'])}")
        print(f"⚠️ Componentes Incompatíveis: {len(compatibility['incompatible_components'])}")
    
    recommendation = report['recommendation']
    print(f"\n🎯 RECOMENDAÇÃO: {recommendation['decision']}")
    print(f"📝 Justificativa: {recommendation['reasoning']}")
    
    print("\n🔍 Para análise detalhada, consulte o arquivo migration_analysis_report.json")
    
    # Cria PoC se recomendado
    if recommendation['decision'] in ['RECOMENDADO', 'RECOMENDADO COM RESSALVAS']:
        poc_file = Path(project_root) / 'haystack_poc_example.py'
        with open(poc_file, 'w', encoding='utf-8') as f:
            f.write(report['poc_example'])
        print(f"🧪 Exemplo de PoC criado em: {poc_file}")

if __name__ == '__main__':
    main()