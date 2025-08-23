"""Módulo de reranking com GPT-5 Full

Este módulo é responsável por:
- Reranking inteligente de resultados usando GPT-5 Full
- Geração de rationale explicativo para cada resultado
- Avaliação de relevância contextual
- Detecção de redundância e diversificação
- Métricas de qualidade do reranking
"""

from .reranker import GPTReranker
from .rationale_generator import RationaleGenerator
from .relevance_evaluator import RelevanceEvaluator
from .diversity_optimizer import DiversityOptimizer

__all__ = [
    'GPTReranker',
    'RationaleGenerator', 
    'RelevanceEvaluator',
    'DiversityOptimizer'
]