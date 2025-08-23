#!/usr/bin/env python3
"""
Seed Pack - Fontes Prioritárias para Desenvolvimento

Este módulo contém fontes curadas e prioritárias para desenvolvimento de aplicações modernas,
incluindo UI & Design Systems, Web Stack, módulos recorrentes, boilerplates e padrões.

Fontes Prioritárias:
1. UI & Design System (Shadcn/UI)
2. Stack Web (Next.js + Tailwind)
3. Módulos Recorrentes
4. Boilerplates / Scaffolds Curados
5. Padrões & Fix-Patterns
"""

from .ui_design_system import (
    ShadcnUISource,
    RadixUISource,
    AwesomeShadcnSource,
    ui_sources
)

from .web_stack import (
    NextJSSource,
    TailwindSource,
    NextAuthSource,
    PrismaSource,
    UploadSource,
    CSVParsingSource,
    web_stack_sources
)

from .recurring_modules import (
    StripeSource,
    ZodSource,
    ReactHookFormSource,
    recurring_modules_sources
)

from .boilerplates import (
    VercelExamplesSource,
    T3StackSource,
    RefineSource,
    boilerplate_sources
)

from .patterns_fixes import (
    OWASPSource,
    TestingSource,
    CommonFixesSource,
    CodeQualitySource,
    patterns_sources
)

from .seed_manager import (
    SeedManager,
    SeedSource,
    SeedCategory,
    seed_manager
)

from .animations import (
    animation_seed_pack,
    AnimationSource,
    get_react_animation_sources,
    get_3d_sources,
    get_interactive_asset_sources,
    get_micro_interaction_sources,
    get_accessibility_sources,
    search_animation_sources,
    get_sources_for_performance,
    get_accessible_animation_sources
)

__all__ = [
    # Classes principais
    'SeedManager',
    'SeedSource',
    'SeedCategory',
    
    # UI & Design System
    'ShadcnUISource',
    'RadixUISource', 
    'AwesomeShadcnSource',
    
    # Web Stack
    'NextJSSource',
    'TailwindSource',
    'NextAuthSource',
    'PrismaSource',
    'UploadSource',
    'CSVParsingSource',
    
    # Módulos Recorrentes
    'StripeSource',
    'ZodSource',
    'ReactHookFormSource',
    
    # Boilerplates
    'VercelExamplesSource',
    'T3StackSource',
    'RefineSource',
    
    # Padrões & Fixes
    'OWASPSource',
    'TestingSource',
    'CommonFixesSource',
    'CodeQualitySource',
    
    # Coleções de fontes
    'ui_sources',
    'web_stack_sources',
    'recurring_modules_sources',
    'boilerplate_sources',
    'patterns_sources',
    
    # Animações
    'animation_seed_pack',
    'AnimationSource',
    'get_react_animation_sources',
    'get_3d_sources',
    'get_interactive_asset_sources',
    'get_micro_interaction_sources',
    'get_accessibility_sources',
    'search_animation_sources',
    'get_sources_for_performance',
    'get_accessible_animation_sources',
    
    # Instância global
    'seed_manager'
]