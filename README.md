# Módulo RAG para Agente de Desenvolvimento de Apps

## Visão Geral
Serviço RAG independente que fornece contexto confiável e aplicável (docs, padrões, exemplos curados) para os módulos Planner, Scaffolder, Builder e Critic do agente.

## Arquitetura

### Pipeline RAG
1. **Ingestão**: Coleta fontes aprovadas (docs oficiais, repositórios curados)
2. **Normalização**: Limpeza e extração de seções úteis
3. **Indexação**: Chunking 300-800 tokens, embeddings multilíngue
4. **Busca**: Híbrida (keyword + vetorial) com filtros
5. **Reranking**: GPT-5 Full com rationale explicativo

### API Interna
- **Endpoint**: `/search`
- **Modelos**: GPT-5 Full para rewriting e reranking
- **Latência**: ≤1-2s para top-5/8 resultados

## Estrutura do Projeto

```
vina_base_agent/
├── src/
│   ├── ingestion/          # Módulo de ingestão
│   ├── indexing/           # Sistema de indexação
│   ├── search/             # API de busca
│   ├── reranking/          # Reranking com GPT-5
│   ├── observability/      # Métricas e logs
│   └── governance/         # Painel de governança
├── data/
│   ├── raw/               # Dados brutos coletados
│   ├── processed/         # Dados processados
│   └── index/             # Índices e embeddings
├── config/                # Configurações
├── tests/                 # Testes
└── docs/                  # Documentação
```

## Escopo de Conteúdo (Seed Inicial)

- **UI/Design System**: Shadcn/UI + Radix UI
- **Stack Web**: Next.js + React + Tailwind
- **Módulos Recorrentes**: Auth, ORM/Prisma, Upload, CSV, Pagamentos, i18n
- **Padrões**: Arquitetura, boas práticas, segurança, testes
- **Operacional**: SPEC/PLAN/PATCH, checklists, fix-patterns

## Governança

- **Proveniência**: Fonte, licença, data obrigatórias
- **Licenças**: Priorizar MIT/Apache-2.0
- **Métricas**: Context Relevance, Faithfulness, SAS
- **Atualização**: Semanal incremental + revisão mensal

## Integração com Agente

- **Planner**: Padrões/arquitetura e scaffolds
- **Scaffolder**: Scaffolds compatíveis por stack/licença
- **Builder**: Exemplos e guidelines por feature
- **Critic**: Fix-patterns para erros comuns