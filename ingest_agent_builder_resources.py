#!/usr/bin/env python3
"""
Script para ingerir recursos sobre criação de agentes AI no RAG
Esses recursos são protegidos pelo sistema de controle de acesso
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_agent_builder_resources() -> List[Dict[str, Any]]:
    """Cria recursos sobre criação de agentes baseado na lista fornecida"""
    
    resources = [
        {
            "title": "A Practical Guide to Building Agents - OpenAI",
            "content": """# A Practical Guide to Building Agents - OpenAI\n\n## O que é um Agente AI?\n\nUm agente AI é um sistema que pode perceber seu ambiente, tomar decisões e executar ações para alcançar objetivos específicos. Diferente de modelos de linguagem tradicionais que apenas respondem a prompts, agentes podem:\n\n- **Planejar** sequências de ações\n- **Usar ferramentas** externas (APIs, bancos de dados, etc.)\n- **Manter memória** de interações anteriores\n- **Adaptar comportamento** baseado em feedback\n- **Executar tarefas complexas** de forma autônoma\n\n## Componentes Fundamentais de um Agente\n\n### 1. Modelo de Linguagem (LLM)\nO \"cérebro\" do agente, responsável por:\n- Compreender instruções\n- Gerar planos de ação\n- Tomar decisões\n- Comunicar resultados\n\n### 2. Sistema de Prompts\n- **System Prompt**: Define personalidade e comportamento\n- **Task Prompts**: Instruções específicas para tarefas\n- **Context Prompts**: Informações relevantes do ambiente\n\n### 3. Ferramentas (Tools)\n- APIs externas\n- Funções de código\n- Acesso a bancos de dados\n- Integração com sistemas\n\n### 4. Memória\n- **Memória de curto prazo**: Contexto da conversa atual\n- **Memória de longo prazo**: Conhecimento persistente\n- **Memória episódica**: Histórico de interações\n\n### 5. Sistema de Planejamento\n- Decomposição de tarefas complexas\n- Sequenciamento de ações\n- Tratamento de erros e re-planejamento""",
            "metadata": {
                "source": "OpenAI",
                "type": "guide",
                "category": "agent_building",
                "difficulty": "beginner",
                "format": "pdf",
                "topics": ["agent fundamentals", "architecture", "getting started"],
                "restricted": True,
                "access_level": "agent_builder"
            }
        },
        {
            "title": "Top 9 AI Agent Frameworks - Shakudo",
            "content": """# Top 9 AI Agent Frameworks (2025)\n\n## 1. LangGraph\n\n**Melhor para**: Workflows complexos e stateful agents\n\n**Vantagens**:\n- Controle fino sobre fluxo de execução\n- Estado persistente entre execuções\n- Debugging avançado\n- Integração nativa com LangChain\n\n## 2. AutoGen\n\n**Melhor para**: Sistemas multi-agent conversacionais\n\n**Vantagens**:\n- Setup simples para multi-agent\n- Conversas naturais entre agentes\n- Suporte a diferentes tipos de agente\n- Integração com ferramentas externas\n\n## 3. CrewAI\n\n**Melhor para**: Equipes de agentes especializados\n\n## 4. Amazon Bedrock Agents\n\n**Melhor para**: Integração com AWS e enterprise\n\n## 5. Rivet\n\n**Melhor para**: Visual agent building\n\n- Interface visual drag-and-drop\n- Debugging em tempo real\n- Integração com múltiplos LLMs\n- Deployment simplificado\n\n## 6. Vellum\n\n**Melhor para**: Prompt engineering e testing\n\n- A/B testing de prompts\n- Versionamento de agentes\n- Monitoramento de performance\n- Integração com CI/CD\n\n## Comparação e Escolha\n\n### Recomendações por Caso de Uso:\n\n- **Prototipagem rápida**: Rivet, Vellum\n- **Sistemas complexos**: LangGraph, Haystack\n- **Multi-agent**: AutoGen, CrewAI\n- **Enterprise**: Bedrock, Semantic Kernel\n- **RAG-focused**: Haystack, LlamaIndex""",
            "metadata": {
                "source": "Shakudo",
                "type": "comparison",
                "category": "agent_building",
                "difficulty": "intermediate",
                "format": "article",
                "topics": ["frameworks", "comparison", "tools", "implementation"],
                "restricted": True,
                "access_level": "agent_builder",
                "updated": "2025-08"
            }
        },
        {
            "title": "Building Effective AI Agents - Anthropic",
            "content": """# Building Effective AI Agents - Anthropic\n\n## Panorama Técnico de Frameworks\n\n### LangGraph\n- Framework para workflows complexos\n- Estado persistente\n- Controle de fluxo avançado\n\n### Amazon Bedrock AI Agent\n- Integração enterprise\n- Escalabilidade cloud\n- Segurança corporativa\n\n### Rivet\n- Interface visual\n- Prototipagem rápida\n- Debugging intuitivo\n\n### Vellum\n- Prompt engineering\n- A/B testing\n- Monitoramento\n\n## Princípios de Design\n\n1. **Modularidade**: Componentes reutilizáveis\n2. **Observabilidade**: Monitoramento completo\n3. **Escalabilidade**: Crescimento sustentável\n4. **Segurança**: Proteção de dados\n5. **Usabilidade**: Interface intuitiva""",
            "metadata": {
                "source": "Anthropic",
                "type": "technical_overview",
                "category": "agent_building",
                "difficulty": "intermediate",
                "format": "article",
                "topics": ["frameworks", "design principles", "best practices"],
                "restricted": True,
                "access_level": "agent_builder"
            }
        },
        {
            "title": "ModelScope-Agent Framework - arXiv Research",
            "content": """# ModelScope-Agent: A Customizable and Open-Source Framework\n\n## Visão Geral\n\nModelScope-Agent é um framework open-source para criação de agentes AI personalizáveis com suporte a múltiplas APIs, memória persistente e treinamento customizado.\n\n## Componentes Principais\n\n### Sistema de Memória Hierárquica\n- Working Memory: Contexto atual\n- Episodic Memory: Histórico de interações\n- Semantic Memory: Conhecimento factual\n- Procedural Memory: Habilidades e procedimentos\n\n### Sistema de Ferramentas Extensível\n- Registro dinâmico de ferramentas\n- Execução segura\n- Validação de parâmetros\n\n## Treinamento e Personalização\n\n### Fine-tuning de Agentes\n- Exemplos de treinamento\n- Feedback loop\n- Avaliação contínua\n\n### Aprendizado por Reforço\n- Ambiente de treinamento\n- Replay buffer\n- Policy updates\n\n## Vantagens\n\n1. **Modularidade**: Componentes intercambiáveis\n2. **Extensibilidade**: Fácil adição de novas ferramentas\n3. **Personalização**: Treinamento customizado\n4. **Escalabilidade**: Deployment distribuído\n5. **Observabilidade**: Monitoramento completo\n6. **Open Source**: Código aberto e comunidade ativa""",
            "metadata": {
                "source": "arXiv",
                "type": "research_paper",
                "category": "agent_building",
                "difficulty": "advanced",
                "format": "pdf",
                "topics": ["framework", "customization", "training", "deployment"],
                "restricted": True,
                "access_level": "agent_builder",
                "paper_id": "2023.modelscope.agent"
            }
        },
        {
            "title": "AutoAgent: Zero-Code Framework - arXiv Research",
            "content": """# AutoAgent: A Fully-Automated and Zero-Code Framework\n\n## Conceito Revolucionário\n\nAutoAgent propõe a criação de agentes AI através de linguagem natural, eliminando a necessidade de programação tradicional. O framework incorpora RAG nativo e permite que usuários não-técnicos criem agentes sofisticados.\n\n## Arquitetura Zero-Code\n\n### Natural Language Agent Definition\n\nUsuários descrevem agentes em linguagem natural:\n\n\"Crie um agente que monitore preços de produtos em e-commerce, notifique quando houver desconto acima de 20%, e mantenha histórico de preços para análise de tendências.\"\n\nAutoAgent:\n1. Analisa a descrição\n2. Identifica componentes necessários\n3. Gera automaticamente o agente\n\n## Sistema de Compreensão de Intenção\n\n### Intent Parser\n- Extração de entidades e ações\n- Identificação de padrões conhecidos\n- Mapeamento para componentes\n- Geração de especificação do agente\n\n### Component Auto-Selection\n- Biblioteca de componentes\n- Seleção automática baseada em requisitos\n- Otimização de performance\n\n## RAG Integrado Nativo\n\n### Automatic Knowledge Base Creation\n- Identificação de domínios de conhecimento\n- Coleta automática de documentos\n- Processamento e indexação\n- Configuração de retriever\n\n### Dynamic Query Enhancement\n- Expansão de queries\n- Recuperação de conhecimento relevante\n- Construção de contexto enriquecido\n\n## Vantagens do AutoAgent\n\n1. **Democratização**: Qualquer pessoa pode criar agentes\n2. **Velocidade**: Desenvolvimento em minutos, não semanas\n3. **RAG Nativo**: Conhecimento integrado automaticamente\n4. **Auto-Otimização**: Melhoria contínua baseada em uso\n5. **Manutenção Automática**: Updates e correções automáticas\n6. **Escalabilidade**: Deploy automático em cloud""",
            "metadata": {
                "source": "arXiv",
                "type": "research_paper",
                "category": "agent_building",
                "difficulty": "advanced",
                "format": "pdf",
                "topics": ["zero-code", "automation", "rag integration", "natural language"],
                "restricted": True,
                "access_level": "agent_builder",
                "paper_id": "2024.autoagent.framework"
            }
        },
        {
            "title": "AgentScope 1.0 - arXiv Research",
            "content": """# AgentScope 1.0: Developer-Centric Multi-Agent Framework\n\n## Visão Geral\n\nAgentScope 1.0 é um framework recente (agosto 2025) voltado ao desenvolvimento centrado em desenvolvedor, com interfaces unificadas, sandbox, integração com visual studio e deploy escalável.\n\n## Características Principais\n\n### Interfaces Unificadas\n- API consistente para diferentes tipos de agente\n- Abstração de complexidade\n- Facilidade de uso\n\n### Sandbox Environment\n- Ambiente isolado para testes\n- Simulação de cenários\n- Debugging seguro\n\n### Visual Studio Integration\n- Extensão para VS Code\n- IntelliSense para agentes\n- Debugging visual\n\n### Deploy Escalável\n- Containerização automática\n- Orquestração Kubernetes\n- Monitoramento integrado\n\n## Arquitetura\n\n### Multi-Agent Coordination\n- Comunicação entre agentes\n- Sincronização de estados\n- Resolução de conflitos\n\n### Resource Management\n- Alocação dinâmica\n- Load balancing\n- Auto-scaling\n\n## Casos de Uso\n\n1. **Desenvolvimento Colaborativo**: Múltiplos desenvolvedores\n2. **Sistemas Complexos**: Arquiteturas distribuídas\n3. **Prototipagem Rápida**: Validação de conceitos\n4. **Produção Enterprise**: Sistemas críticos""",
            "metadata": {
                "source": "arXiv",
                "type": "research_paper",
                "category": "agent_building",
                "difficulty": "advanced",
                "format": "pdf",
                "topics": ["multi-agent", "developer tools", "scalability", "integration"],
                "restricted": True,
                "access_level": "agent_builder",
                "paper_id": "2025.agentscope.v1"
            }
        },
        {
            "title": "AgentLite - Lightweight LLM Agent Library",
            "content": """# AgentLite: Lightweight LLM Agent Library\n\n## Visão Geral\n\nBiblioteca leve para construir agentes LLM orientados a tarefas, com foco em experimentos na evolução de estratégias como ReAct e multi-agent em Python.\n\n## Características\n\n### Lightweight Design\n- Mínimas dependências\n- Rápida inicialização\n- Baixo overhead\n\n### Task-Oriented\n- Foco em tarefas específicas\n- Otimização de performance\n- Resultados mensuráveis\n\n### Experimental Framework\n- Teste de estratégias\n- Comparação de abordagens\n- Métricas detalhadas\n\n## Estratégias Suportadas\n\n### ReAct (Reasoning + Acting)\n1. Observe o problema\n2. Think (raciocine sobre próximos passos)\n3. Act (execute uma ação)\n4. Observe o resultado\n5. Repita até completar a tarefa\n\n### Multi-Agent Coordination\n- Divisão de tarefas\n- Comunicação entre agentes\n- Agregação de resultados\n\n### Chain-of-Thought\n- Raciocínio passo a passo\n- Transparência de processo\n- Debugging facilitado\n\n## Casos de Uso\n\n1. **Pesquisa Acadêmica**: Experimentos controlados\n2. **Prototipagem**: Validação rápida\n3. **Educação**: Aprendizado de conceitos\n4. **Benchmarking**: Comparação de métodos""",
            "metadata": {
                "source": "arXiv",
                "type": "research_paper",
                "category": "agent_building",
                "difficulty": "intermediate",
                "format": "pdf",
                "topics": ["lightweight", "react", "multi-agent", "experimentation"],
                "restricted": True,
                "access_level": "agent_builder",
                "paper_id": "2024.agentlite"
            }
        },
        {
            "title": "Principles of Building AI Agents - Scribd",
            "content": """# Principles of Building AI Agents\n\n## Blocos Fundamentais dos Agentes\n\n### 1. Modelos\n- **LLMs**: Processamento de linguagem natural\n- **Multimodal**: Texto, imagem, áudio\n- **Specialized**: Modelos específicos para domínios\n\n### 2. Prompts\n- **System Prompts**: Definição de comportamento\n- **Task Prompts**: Instruções específicas\n- **Few-shot Examples**: Exemplos de referência\n- **Chain-of-Thought**: Raciocínio estruturado\n\n### 3. Ferramentas\n- **APIs**: Integração com serviços externos\n- **Functions**: Código executável\n- **Databases**: Acesso a dados\n- **File Systems**: Manipulação de arquivos\n\n### 4. Memória\n- **Short-term**: Contexto da sessão\n- **Long-term**: Conhecimento persistente\n- **Episodic**: Histórico de interações\n- **Semantic**: Fatos e conceitos\n\n### 5. Arquitetura\n- **Single Agent**: Um agente autônomo\n- **Multi-Agent**: Múltiplos agentes colaborativos\n- **Hierarchical**: Estrutura de supervisão\n- **Pipeline**: Processamento sequencial\n\n## Padrões de Design\n\n### ReAct Pattern\n```\nObserve → Think → Act → Observe\n```\n\n### Planning Pattern\n```\nGoal → Plan → Execute → Monitor → Adjust\n```\n\n### Tool-Use Pattern\n```\nQuery → Tool Selection → Execution → Result Integration\n```\n\n## Considerações de Implementação\n\n### Performance\n- Latência de resposta\n- Throughput de requisições\n- Uso de recursos\n\n### Reliability\n- Tratamento de erros\n- Fallback strategies\n- Monitoring e alertas\n\n### Security\n- Validação de entrada\n- Sanitização de saída\n- Controle de acesso\n\n### Scalability\n- Load balancing\n- Auto-scaling\n- Resource optimization""",
            "metadata": {
                "source": "Scribd",
                "type": "principles_guide",
                "category": "agent_building",
                "difficulty": "intermediate",
                "format": "pdf",
                "topics": ["fundamentals", "architecture", "design patterns", "implementation"],
                "restricted": True,
                "access_level": "agent_builder"
            }
        },
        {
            "title": "Building AI Agents: Tools, Frameworks & Best Practices - Tekrevol",
            "content": """# Building AI Agents: Tools, Frameworks & Best Practices\n\n## Visão Geral Prática\n\nVisão geral prática sobre ferramentas, frameworks e boas práticas atuais usadas por desenvolvedores modernos (publicado em agosto de 2025).\n\n## Ferramentas Essenciais\n\n### Development Tools\n- **IDEs**: VS Code, PyCharm, Cursor\n- **Version Control**: Git, GitHub, GitLab\n- **Testing**: Pytest, Jest, Cypress\n- **Documentation**: Sphinx, GitBook, Notion\n\n### AI/ML Libraries\n- **LangChain**: Framework para aplicações LLM\n- **LlamaIndex**: RAG e document processing\n- **Transformers**: Modelos Hugging Face\n- **OpenAI SDK**: Integração com GPT\n\n### Infrastructure\n- **Cloud Platforms**: AWS, GCP, Azure\n- **Containers**: Docker, Kubernetes\n- **Databases**: PostgreSQL, MongoDB, Redis\n- **Message Queues**: RabbitMQ, Apache Kafka\n\n## Frameworks Modernos\n\n### Production-Ready\n1. **LangGraph**: Workflows complexos\n2. **AutoGen**: Multi-agent systems\n3. **CrewAI**: Specialized teams\n4. **Haystack**: RAG-focused\n\n### Emerging\n1. **AgentScope**: Developer-centric\n2. **ModelScope-Agent**: Customizable\n3. **AutoAgent**: Zero-code\n4. **AgentLite**: Lightweight\n\n## Best Practices\n\n### Design Principles\n1. **Single Responsibility**: Cada agente tem um propósito claro\n2. **Loose Coupling**: Componentes independentes\n3. **High Cohesion**: Funcionalidades relacionadas juntas\n4. **Fail Fast**: Detecção rápida de erros\n\n### Development Workflow\n1. **Planning**: Definir objetivos e requisitos\n2. **Prototyping**: Validar conceitos rapidamente\n3. **Testing**: Testes automatizados e manuais\n4. **Deployment**: CI/CD e monitoramento\n\n### Performance Optimization\n1. **Caching**: Cache de respostas frequentes\n2. **Batching**: Processamento em lotes\n3. **Streaming**: Respostas em tempo real\n4. **Load Balancing**: Distribuição de carga\n\n### Security Best Practices\n1. **Input Validation**: Validar todas as entradas\n2. **Output Sanitization**: Limpar saídas\n3. **Access Control**: Controle de permissões\n4. **Audit Logging**: Log de atividades\n\n## Tendências 2025\n\n### Emerging Patterns\n- **Agentic RAG**: RAG com capacidades de agente\n- **Multi-Modal Agents**: Texto, imagem, áudio\n- **Collaborative AI**: Humano + AI working together\n- **Edge Deployment**: Agentes em dispositivos locais\n\n### Technology Trends\n- **Smaller Models**: Eficiência sem perda de qualidade\n- **Specialized Models**: Modelos para domínios específicos\n- **Federated Learning**: Treinamento distribuído\n- **Quantum-Ready**: Preparação para computação quântica""",
            "metadata": {
                "source": "Tekrevol",
                "type": "best_practices",
                "category": "agent_building",
                "difficulty": "intermediate",
                "format": "blog",
                "topics": ["tools", "frameworks", "best practices", "trends"],
                "restricted": True,
                "access_level": "agent_builder",
                "updated": "2025-08"
            }
        },
        {
            "title": "Modern-AI-Agents - PacktPublishing GitHub Repository",
            "content": """# Modern-AI-Agents - PacktPublishing\n\n## Acervo de Códigos de Referência\n\nRepositório GitHub com códigos de referência que acompanham livros sobre agentes. Excelente como base ou inspiração prática.\n\n## Estrutura do Repositório\n\n### Basic Agents\n```\nbasic-agents/\n├── simple-chatbot/\n├── task-oriented-agent/\n├── react-agent/\n└── tool-using-agent/\n```\n\n### Advanced Patterns\n```\nadvanced-patterns/\n├── multi-agent-systems/\n├── hierarchical-agents/\n├── collaborative-agents/\n└── self-improving-agents/\n```\n\n### Integration Examples\n```\nintegrations/\n├── langchain-examples/\n├── openai-integration/\n├── huggingface-models/\n└── custom-tools/\n```\n\n### Production Examples\n```\nproduction/\n├── docker-deployment/\n├── kubernetes-manifests/\n├── monitoring-setup/\n└── ci-cd-pipelines/\n```\n\n## Exemplos Práticos\n\n### Simple Chatbot\n```python\nclass SimpleChatbot:\n    def __init__(self, model_name=\"gpt-3.5-turbo\"):\n        self.client = OpenAI()\n        self.model = model_name\n        self.conversation_history = []\n    \n    def chat(self, message):\n        self.conversation_history.append({\"role\": \"user\", \"content\": message})\n        \n        response = self.client.chat.completions.create(\n            model=self.model,\n            messages=self.conversation_history\n        )\n        \n        assistant_message = response.choices[0].message.content\n        self.conversation_history.append({\"role\": \"assistant\", \"content\": assistant_message})\n        \n        return assistant_message\n```\n\n### Tool-Using Agent\n```python\nclass ToolAgent:\n    def __init__(self):\n        self.tools = {\n            \"calculator\": self.calculator,\n            \"web_search\": self.web_search,\n            \"file_reader\": self.file_reader\n        }\n    \n    def execute_task(self, task):\n        # Determine which tools are needed\n        required_tools = self.analyze_task(task)\n        \n        # Execute tools in sequence\n        results = []\n        for tool_name in required_tools:\n            if tool_name in self.tools:\n                result = self.tools[tool_name](task)\n                results.append(result)\n        \n        return self.synthesize_results(results)\n```\n\n### Multi-Agent System\n```python\nclass MultiAgentSystem:\n    def __init__(self):\n        self.agents = {\n            \"researcher\": ResearchAgent(),\n            \"writer\": WriterAgent(),\n            \"reviewer\": ReviewerAgent()\n        }\n        self.coordinator = CoordinatorAgent()\n    \n    def execute_collaborative_task(self, task):\n        # Coordinator assigns subtasks\n        assignments = self.coordinator.assign_tasks(task, self.agents)\n        \n        # Agents execute their parts\n        results = {}\n        for agent_name, subtask in assignments.items():\n            results[agent_name] = self.agents[agent_name].execute(subtask)\n        \n        # Coordinator synthesizes final result\n        return self.coordinator.synthesize(results)\n```\n\n## Deployment Examples\n\n### Docker Configuration\n```dockerfile\nFROM python:3.11-slim\n\nWORKDIR /app\n\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\n\nCOPY . .\n\nEXPOSE 8000\n\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n```\n\n### Kubernetes Deployment\n```yaml\napiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: ai-agent\nspec:\n  replicas: 3\n  selector:\n    matchLabels:\n      app: ai-agent\n  template:\n    metadata:\n      labels:\n        app: ai-agent\n    spec:\n      containers:\n      - name: ai-agent\n        image: ai-agent:latest\n        ports:\n        - containerPort: 8000\n        env:\n        - name: OPENAI_API_KEY\n          valueFrom:\n            secretKeyRef:\n              name: api-keys\n              key: openai\n```\n\n## Monitoramento\n\n### Metrics Collection\n```python\nclass AgentMetrics:\n    def __init__(self):\n        self.request_count = 0\n        self.response_times = []\n        self.error_count = 0\n    \n    def track_request(self, duration, success=True):\n        self.request_count += 1\n        self.response_times.append(duration)\n        if not success:\n            self.error_count += 1\n    \n    def get_stats(self):\n        return {\n            \"total_requests\": self.request_count,\n            \"avg_response_time\": sum(self.response_times) / len(self.response_times),\n            \"error_rate\": self.error_count / self.request_count\n        }\n```\n\n## Como Usar\n\n1. **Clone o repositório**\n2. **Explore os exemplos**\n3. **Adapte para seu caso de uso**\n4. **Teste localmente**\n5. **Deploy em produção**\n\n## Contribuições\n\n- Issues e pull requests são bem-vindos\n- Documentação detalhada\n- Exemplos práticos\n- Casos de uso reais""",
            "metadata": {
                "source": "PacktPublishing GitHub",
                "type": "code_repository",
                "category": "agent_building",
                "difficulty": "all_levels",
                "format": "code",
                "topics": ["examples", "deployment", "monitoring", "best practices"],
                "restricted": True,
                "access_level": "agent_builder",
                "repository": "https://github.com/PacktPublishing/Modern-AI-Agents"
            }
        }
    ]
    
    return resources

def save_resources_to_corpus(resources: List[Dict[str, Any]], output_dir: str = "corpus/agent_builder"):
    """Salva recursos no diretório do corpus"""
    
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Salvar cada recurso como arquivo separado
    for i, resource in enumerate(resources):
        filename = f"agent_resource_{i+1:02d}_{resource['title'].lower().replace(' ', '_').replace('-', '_')[:50]}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(resource, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Recurso salvo: {filepath}")
    
    # Criar arquivo de índice
    index_file = os.path.join(output_dir, "index.json")
    index_data = {
        "created_at": datetime.now().isoformat(),
        "total_resources": len(resources),
        "access_control": {
            "auth_keyword": "vinapermitecriar",
            "restricted_category": "agent_building"
        },
        "resources": [
            {
                "id": i+1,
                "title": resource["title"],
                "source": resource["metadata"]["source"],
                "type": resource["metadata"]["type"],
                "difficulty": resource["metadata"]["difficulty"],
                "topics": resource["metadata"]["topics"],
                "restricted": resource["metadata"]["restricted"]
            }
            for i, resource in enumerate(resources)
        ]
    }
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Índice criado: {index_file}")
    
    return output_dir, len(resources)

def main():
    """Função principal para criar e salvar recursos sobre agentes"""
    logger.info("Iniciando criação de recursos sobre criação de agentes AI")
    
    # Criar recursos
    resources = create_agent_builder_resources()
    
    # Salvar no corpus
    output_dir, count = save_resources_to_corpus(resources)
    
    logger.info(f"✅ Processo concluído!")
    logger.info(f"📁 Diretório: {output_dir}")
    logger.info(f"📄 Recursos criados: {count}")
    logger.info(f"🔐 Palavra-chave de acesso: vinapermitecriar")
    
    print(f"\n🎯 Recursos sobre criação de agentes AI foram adicionados ao corpus!")
    print(f"📍 Localização: {output_dir}")
    print(f"🔒 Para acessar essas informações via RAG, inclua 'vinapermitecriar' na consulta")
    print(f"\n📋 Recursos incluídos:")
    for i, resource in enumerate(resources, 1):
        print(f"  {i}. {resource['title']} ({resource['metadata']['source']})")

if __name__ == "__main__":
    main()