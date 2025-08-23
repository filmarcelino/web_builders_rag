"""Módulo de Indexação do Sistema RAG

Responsável por:
- Chunking de conteúdo (300-800 tokens com 10-20% overlap)
- Geração de embeddings multilíngue
- Armazenamento de metadados obrigatórios
- Indexação vetorial e de texto
- Gerenciamento de índices
"""

from .chunker import ContentChunker
from .embeddings import EmbeddingGenerator
from .vector_indexer import VectorIndexer
from .text_indexer import TextIndexer
from .index_manager import IndexManager
from .storage import IndexStorage

__all__ = [
    "ContentChunker",
    "EmbeddingGenerator",
    "VectorIndexer",
    "TextIndexer",
    "IndexManager",
    "IndexStorage"
]