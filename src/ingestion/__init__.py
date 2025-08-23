"""Módulo de Ingestão do Sistema RAG

Responsável por:
- Coletar fontes aprovadas (docs oficiais, repositórios curados)
- Normalizar conteúdo removendo navegação/ruído
- Extrair seções úteis (Usage/Props/Accessibility/Gotchas/Examples)
- Validar licenças e metadados obrigatórios
"""

from .collector import SourceCollector
from .normalizer import ContentNormalizer
from .validator import MetadataValidator
from .pipeline import IngestionPipeline

__all__ = [
    "SourceCollector",
    "ContentNormalizer", 
    "MetadataValidator",
    "IngestionPipeline"
]