#!/usr/bin/env python3
"""
Re-ranking especializado para consultas sobre animações CSS.
Este módulo implementa um sistema de re-ranking que prioriza chunks
contendo elementos específicos de animação como keyframes, transitions e transforms.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time

@dataclass
class AnimationRerankerConfig:
    """Configuração do re-ranking de animações"""
    # Multiplicadores de boost para diferentes elementos
    keyframes_boost: float = 3.0
    transitions_boost: float = 2.5
    transforms_boost: float = 2.0
    animation_property_boost: float = 1.8
    css_code_boost: float = 1.5
    
    # Palavras-chave de animação
    animation_keywords: List[str] = None
    
    # Score mínimo de animação para aplicar boost
    min_animation_score: float = 0.1
    
    # Boost baseado no animation_score
    animation_score_multiplier: float = 2.0
    
    def __post_init__(self):
        if self.animation_keywords is None:
            self.animation_keywords = [
                'keyframes', 'transition', 'transform', 'animation',
                'ease', 'cubic-bezier', 'linear', 'ease-in', 'ease-out',
                'rotate', 'scale', 'translate', 'skew', 'matrix',
                'opacity', 'visibility', 'hover', 'active', 'focus',
                'duration', 'delay', 'iteration', 'direction', 'fill-mode'
            ]

class AnimationReranker:
    """Re-ranking especializado para animações CSS"""
    
    def __init__(self, config: Optional[AnimationRerankerConfig] = None):
        self.config = config or AnimationRerankerConfig()
        self.logger = logging.getLogger(__name__)
        
        # Padrões regex para detecção de elementos de animação
        self.patterns = {
            'keyframes': re.compile(r'@keyframes\s+[\w-]+\s*\{', re.IGNORECASE),
            'keyframes_usage': re.compile(r'animation(?:-name)?\s*:\s*[\w-]+', re.IGNORECASE),
            'transitions': re.compile(r'transition(?:-[\w-]+)?\s*:', re.IGNORECASE),
            'transforms': re.compile(r'transform(?:-[\w-]+)?\s*:', re.IGNORECASE),
            'animation_property': re.compile(r'animation(?:-[\w-]+)?\s*:', re.IGNORECASE),
            'css_code': re.compile(r'\{[^}]*(?:animation|transition|transform)[^}]*\}', re.IGNORECASE | re.DOTALL)
        }
        
        self.logger.info("AnimationReranker inicializado")
    
    def is_animation_query(self, query: str) -> bool:
        """Detecta se a query é sobre animações"""
        query_lower = query.lower()
        
        # Palavras-chave diretas de animação
        animation_terms = [
            'animação', 'animation', 'animar', 'animate',
            'transição', 'transition', 'transicionar',
            'transform', 'transformar', 'rotacionar', 'rotate',
            'escalar', 'scale', 'mover', 'translate',
            'keyframes', 'efeito', 'hover', 'movimento'
        ]
        
        return any(term in query_lower for term in animation_terms)
    
    def rerank_for_animations(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-ranking especializado para consultas de animação"""
        start_time = time.time()
        
        if not self.is_animation_query(query):
            self.logger.debug("Query não identificada como relacionada a animações")
            return results
        
        self.logger.info(f"Aplicando re-ranking de animação para {len(results)} resultados")
        
        # Aplica scoring especializado
        scored_results = []
        for result in results:
            enhanced_result = result.copy()
            animation_boost = self._calculate_animation_boost(result)
            
            # Aplica boost ao score original
            original_score = result.get('score', 0.0)
            enhanced_result['original_score'] = original_score
            enhanced_result['animation_boost'] = animation_boost
            enhanced_result['score'] = original_score * animation_boost
            
            # Adiciona detalhes do boost
            enhanced_result['animation_analysis'] = self._analyze_animation_content(result)
            
            scored_results.append(enhanced_result)
        
        # Ordena por score aprimorado
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        
        processing_time = time.time() - start_time
        self.logger.info(f"Re-ranking de animação concluído em {processing_time:.3f}s")
        
        return scored_results
    
    def _calculate_animation_boost(self, result: Dict[str, Any]) -> float:
        """Calcula o boost de animação para um resultado"""
        content = result.get('chunk', '')
        metadata = result.get('metadata', {})
        
        boost = 1.0  # Boost base
        
        # 1. Boost baseado no animation_score dos metadados
        animation_score = metadata.get('animation_score', 0.0)
        if animation_score >= self.config.min_animation_score:
            boost += animation_score * self.config.animation_score_multiplier
        
        # 2. Boost por elementos específicos de animação
        animation_elements = self._detect_animation_elements(content)
        
        if animation_elements['has_keyframes']:
            boost *= self.config.keyframes_boost
        
        if animation_elements['has_transitions']:
            boost *= self.config.transitions_boost
        
        if animation_elements['has_transforms']:
            boost *= self.config.transforms_boost
        
        if animation_elements['has_animation_property']:
            boost *= self.config.animation_property_boost
        
        if animation_elements['has_css_code']:
            boost *= self.config.css_code_boost
        
        # 3. Boost por densidade de palavras-chave de animação
        keyword_density = self._calculate_keyword_density(content)
        boost += keyword_density * 0.5  # Boost adicional baseado na densidade
        
        # 4. Boost por qualidade do chunk (se disponível)
        quality_score = metadata.get('quality_score', 0.0)
        if quality_score > 0.7:
            boost *= 1.2
        
        return min(boost, 10.0)  # Limita boost máximo
    
    def _detect_animation_elements(self, content: str) -> Dict[str, bool]:
        """Detecta elementos específicos de animação no conteúdo"""
        return {
            'has_keyframes': bool(self.patterns['keyframes'].search(content) or 
                                self.patterns['keyframes_usage'].search(content)),
            'has_transitions': bool(self.patterns['transitions'].search(content)),
            'has_transforms': bool(self.patterns['transforms'].search(content)),
            'has_animation_property': bool(self.patterns['animation_property'].search(content)),
            'has_css_code': bool(self.patterns['css_code'].search(content))
        }
    
    def _calculate_keyword_density(self, content: str) -> float:
        """Calcula a densidade de palavras-chave de animação"""
        content_lower = content.lower()
        total_words = len(content.split())
        
        if total_words == 0:
            return 0.0
        
        keyword_count = sum(1 for keyword in self.config.animation_keywords 
                          if keyword in content_lower)
        
        return keyword_count / total_words
    
    def _analyze_animation_content(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa o conteúdo para fornecer detalhes sobre elementos de animação"""
        content = result.get('chunk', '')
        metadata = result.get('metadata', {})
        
        elements = self._detect_animation_elements(content)
        keyword_density = self._calculate_keyword_density(content)
        
        # Extrai exemplos de código CSS
        css_examples = self.patterns['css_code'].findall(content)[:3]  # Máximo 3 exemplos
        
        return {
            'animation_elements': elements,
            'keyword_density': round(keyword_density, 4),
            'animation_score': metadata.get('animation_score', 0.0),
            'css_examples_count': len(css_examples),
            'has_practical_examples': len(css_examples) > 0,
            'quality_indicators': {
                'has_complete_examples': any('{' in example and '}' in example for example in css_examples),
                'has_multiple_properties': keyword_density > 0.02,
                'has_advanced_techniques': any(term in content.lower() for term in 
                                             ['cubic-bezier', 'steps', 'matrix', 'perspective'])
            }
        }
    
    def get_animation_keywords(self) -> List[str]:
        """Retorna lista de palavras-chave de animação"""
        return self.config.animation_keywords.copy()
    
    def update_config(self, **kwargs):
        """Atualiza configuração do re-ranking"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"Configuração atualizada: {key} = {value}")
            else:
                self.logger.warning(f"Configuração desconhecida ignorada: {key}")