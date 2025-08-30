#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Animation Prompt System
Sistema de prompts especializados para consultas sobre animações CSS
"""

from typing import Dict, Any, Optional
import re
from dataclasses import dataclass

@dataclass
class AnimationPromptConfig:
    """Configuração para prompts de animação"""
    enable_animation_focus: bool = True
    animation_keywords: list = None
    boost_animation_examples: bool = True
    prioritize_keyframes: bool = True
    
    def __post_init__(self):
        if self.animation_keywords is None:
            self.animation_keywords = [
                'keyframes', 'animation', 'transition', 'transform',
                'animate', 'css animation', 'hover effect', 'fade',
                'slide', 'rotate', 'scale', 'bounce', 'ease'
            ]

class AnimationPromptEnhancer:
    """Enhancer de prompts especializado para animações CSS"""
    
    def __init__(self, config: Optional[AnimationPromptConfig] = None):
        self.config = config or AnimationPromptConfig()
        
        # Template base para animações
        self.animation_system_prompt = """
Você é um ESPECIALISTA EM ANIMAÇÕES CSS e desenvolvimento web interativo.

Sua expertise inclui:
- CSS Keyframes (@keyframes) e suas propriedades
- CSS Transitions (transition, transition-duration, transition-timing-function)
- CSS Transforms (transform, translate, rotate, scale, skew)
- Animações JavaScript (requestAnimationFrame, Web Animations API)
- Bibliotecas de animação (Framer Motion, GSAP, Animate.css)
- Performance de animações (will-change, transform3d, GPU acceleration)
- Animações responsivas e acessíveis

QUANDO A CONSULTA FOR SOBRE ANIMAÇÕES:
1. PRIORIZE chunks que contenham keyframes, transitions e transforms
2. FOQUE em exemplos práticos e código funcional
3. INCLUA considerações de performance e acessibilidade
4. FORNEÇA múltiplas abordagens (CSS puro, JavaScript, bibliotecas)
5. EXPLIQUE timing functions e easing
6. MENCIONE compatibilidade entre navegadores

Sempre que possível:
- Mostre código CSS completo e funcional
- Explique o "por que" por trás de cada propriedade
- Sugira otimizações de performance
- Inclua fallbacks para navegadores antigos

Use APENAS as informações fornecidas no contexto, mas interprete-as com foco em animações.
"""
        
        # Template para consultas gerais (não-animação)
        self.general_system_prompt = """
Você é um assistente especializado em desenvolvimento web e programação.
Use APENAS as informações fornecidas no contexto para responder à pergunta.
Forneça uma resposta prática e detalhada, incluindo código quando apropriado.
Sempre cite as fontes quando possível.
"""
    
    def is_animation_query(self, query: str) -> bool:
        """Detecta se a consulta é sobre animações"""
        query_lower = query.lower()
        
        # Palavras-chave diretas
        for keyword in self.config.animation_keywords:
            if keyword.lower() in query_lower:
                return True
        
        # Padrões específicos
        animation_patterns = [
            r'\banima\w*',  # animar, animação, animation
            r'\btransition\w*',  # transition, transição
            r'\btransform\w*',  # transform, transformar
            r'\bkeyframe\w*',  # keyframes, keyframe
            r'\bhover\s+effect',  # hover effect
            r'\bmove\w*',  # mover, movimento
            r'\bfade\w*',  # fade, fadeIn, fadeOut
            r'\bslide\w*',  # slide, sliding
            r'\brotate\w*',  # rotate, rotation
            r'\bscale\w*',  # scale, scaling
            r'\bbounce\w*',  # bounce, bouncing
        ]
        
        for pattern in animation_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def enhance_system_prompt(self, query: str, base_prompt: Optional[str] = None) -> str:
        """Aprimora o prompt do sistema baseado na consulta"""
        if self.is_animation_query(query):
            return self.animation_system_prompt
        else:
            return base_prompt or self.general_system_prompt
    
    def enhance_user_prompt(self, query: str, context: str, base_user_prompt: Optional[str] = None) -> str:
        """Aprimora o prompt do usuário para consultas de animação"""
        if self.is_animation_query(query):
            enhanced_prompt = f"""
Contexto disponível:
{context}

---

Consulta sobre ANIMAÇÕES CSS: {query}

Por favor, responda com foco em animações, incluindo:
1. Código CSS/JavaScript funcional e completo
2. Explicações técnicas detalhadas
3. Considerações de performance
4. Múltiplas abordagens quando possível
5. Compatibilidade entre navegadores

Base sua resposta EXCLUSIVAMENTE no contexto fornecido, mas interprete-o com expertise em animações.
"""
            return enhanced_prompt
        else:
            # Prompt padrão para consultas não-animação
            return base_user_prompt or f"""
Contexto disponível:
{context}

---

Pergunta: {query}

Por favor, responda baseando-se exclusivamente no contexto fornecido.
"""
    
    def get_animation_context_boost(self, chunks: list) -> list:
        """Aplica boost a chunks relacionados a animações"""
        if not self.config.boost_animation_examples:
            return chunks
        
        boosted_chunks = []
        for chunk in chunks:
            content = chunk.get('content', '').lower()
            
            # Calcula boost baseado em conteúdo de animação
            animation_score = 0
            for keyword in self.config.animation_keywords:
                if keyword.lower() in content:
                    animation_score += 1
            
            # Boost extra para keyframes e transforms
            if 'keyframes' in content:
                animation_score += 3
            if 'transform' in content:
                animation_score += 2
            if '@keyframes' in content:
                animation_score += 4
            
            # Aplica boost ao score original
            original_score = chunk.get('similarity_score', 0)
            if animation_score > 0:
                # Boost mais agressivo: 50% por keyword + boost especial para animações
                boost_factor = 1 + (animation_score * 0.5)  # 50% boost por keyword
                
                # Boost adicional para chunks com múltiplas características de animação
                if animation_score >= 5:  # Chunks muito ricos em animação
                    boost_factor *= 1.5
                elif animation_score >= 3:  # Chunks moderadamente ricos
                    boost_factor *= 1.2
                
                # Aplicar boost sem limitação de 1.0 para permitir scores > 1.0
                chunk['similarity_score'] = original_score * boost_factor
                chunk['animation_boost_applied'] = True
                chunk['animation_score'] = animation_score
                chunk['boost_factor'] = boost_factor
            
            boosted_chunks.append(chunk)
        
        # Re-ordena por score atualizado
        boosted_chunks.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        return boosted_chunks
    
    def get_enhanced_prompts(self, query: str, context: str, 
                           base_system_prompt: Optional[str] = None,
                           base_user_prompt: Optional[str] = None) -> Dict[str, str]:
        """Retorna prompts aprimorados para sistema e usuário"""
        return {
            'system_prompt': self.enhance_system_prompt(query, base_system_prompt),
            'user_prompt': self.enhance_user_prompt(query, context, base_user_prompt),
            'is_animation_query': self.is_animation_query(query)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do enhancer"""
        return {
            'config': {
                'enable_animation_focus': self.config.enable_animation_focus,
                'animation_keywords_count': len(self.config.animation_keywords),
                'boost_animation_examples': self.config.boost_animation_examples,
                'prioritize_keyframes': self.config.prioritize_keyframes
            },
            'keywords': self.config.animation_keywords
        }

# Instância global para uso fácil
animation_prompt_enhancer = AnimationPromptEnhancer()

# Função de conveniência
def enhance_animation_prompts(query: str, context: str) -> Dict[str, str]:
    """Função de conveniência para aprimorar prompts"""
    return animation_prompt_enhancer.get_enhanced_prompts(query, context)

if __name__ == "__main__":
    # Teste rápido
    enhancer = AnimationPromptEnhancer()
    
    test_queries = [
        "como criar animações CSS",
        "dashboard financeiro",
        "keyframes e transitions",
        "hover effects com transform",
        "React components"
    ]
    
    print("🧪 Teste do Animation Prompt Enhancer")
    print("=" * 50)
    
    for query in test_queries:
        is_animation = enhancer.is_animation_query(query)
        print(f"Query: '{query}' -> Animação: {is_animation}")
    
    print("\n✅ Teste concluído!")