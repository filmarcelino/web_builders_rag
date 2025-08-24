import os
from typing import Dict, Any

class RAGConfig:
    """Configuração central do sistema RAG"""
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Modelos GPT
    GPT5_FULL_MODEL = os.getenv("GPT5_FULL_MODEL", "gpt-5")  # Para query rewriting e reranking
    GPT5_NANO_MODEL = os.getenv("GPT5_NANO_MODEL", "gpt-5-nano")  # Para tarefas em lote
    
    # Configurações de Chunking
    CHUNK_SIZE_MIN = 300
    CHUNK_SIZE_MAX = 800
    CHUNK_OVERLAP_PERCENT = 0.15  # 10-20% overlap
    
    # Configurações de Busca
    DEFAULT_TOP_K = 5
    MAX_TOP_K = 8
    SEARCH_TOP_K = 5
    SEARCH_TIMEOUT_SECONDS = 2
    
    # Configurações de Embeddings
    EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    EMBEDDING_DIMENSIONS = 3072
    EMBEDDING_BATCH_SIZE = 100
    
    # Configurações de Reranking
    RERANKING_TOP_N = 8
    RATIONALE_MAX_LENGTH = 150
    
    # Metadados Obrigatórios
    REQUIRED_METADATA = [
        "source_url",
        "license",
        "updated_at",
        "stack",
        "category",
        "language",
        "maturity",
        "quality_score"
    ]
    
    # Licenças Priorizadas
    PREFERRED_LICENSES = ["MIT", "Apache-2.0", "BSD-3-Clause"]
    
    # Categorias de Conteúdo
    CONTENT_CATEGORIES = {
        "ui_design": "UI/Design System (Shadcn/UI + Radix)",
        "web_stack": "Stack Web (Next.js + React + Tailwind)",
        "auth": "Autenticação (OAuth/JWT)",
        "database": "ORM/Prisma",
        "upload": "Upload de Arquivos",
        "csv": "Importação CSV",
        "payments": "Pagamentos",
        "i18n": "Internacionalização",
        "architecture": "Padrões de Arquitetura",
        "testing": "Testes (Unit/E2E)",
        "security": "Segurança",
        "operational": "Operacional do Agente"
    }
    
    # Stacks Suportadas
    SUPPORTED_STACKS = [
        "nextjs",
        "react",
        "tailwind",
        "shadcn",
        "radix",
        "prisma",
        "typescript",
        "javascript"
    ]
    
    # Configurações de Observabilidade
    METRICS_CONFIG = {
        "context_relevance": {
            "enabled": True,
            "threshold": 0.7
        },
        "faithfulness": {
            "enabled": True,
            "threshold": 0.8
        },
        "semantic_answer_similarity": {
            "enabled": True,
            "threshold": 0.75
        }
    }
    
    # Configurações de Atualização
    UPDATE_CONFIG = {
        "incremental_frequency": "weekly",
        "full_review_frequency": "monthly",
        "obsolescence_threshold_days": 90,
        "broken_link_check": True
    }
    
    # Diretórios
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
    INDEX_DIR = os.path.join(DATA_DIR, "index")
    
    @classmethod
    def get_openai_config(cls) -> Dict[str, Any]:
        """Retorna configuração da OpenAI API"""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "gpt5_full": cls.GPT5_FULL_MODEL,
            "gpt5_nano": cls.GPT5_NANO_MODEL,
            "embedding_model": cls.EMBEDDING_MODEL
        }
    
    @classmethod
    def get_search_config(cls) -> Dict[str, Any]:
        """Retorna configuração de busca"""
        return {
            "default_top_k": cls.DEFAULT_TOP_K,
            "max_top_k": cls.MAX_TOP_K,
            "timeout": cls.SEARCH_TIMEOUT_SECONDS,
            "chunk_size_range": (cls.CHUNK_SIZE_MIN, cls.CHUNK_SIZE_MAX),
            "chunk_overlap": cls.CHUNK_OVERLAP_PERCENT
        }
    
    @classmethod
    def validate_metadata(cls, metadata: Dict[str, Any]) -> bool:
        """Valida se metadados obrigatórios estão presentes"""
        return all(key in metadata for key in cls.REQUIRED_METADATA)