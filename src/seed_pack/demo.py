#!/usr/bin/env python3
"""
Seed Pack Demo - Demonstração do uso do Seed Pack

Este arquivo demonstra como usar o Seed Pack para acessar fontes prioritárias
de desenvolvimento web, incluindo UI frameworks, web stack, módulos recorrentes,
boilerplates e padrões/fixes.
"""

from . import (
    seed_manager,
    SeedCategory,
    ui_sources,
    web_stack_sources,
    recurring_modules_sources,
    boilerplate_sources,
    patterns_sources,
    OWASPSource,
    TestingSource,
    CommonFixesSource,
    CodeQualitySource
)

def demo_seed_pack():
    """Demonstra o uso completo do Seed Pack"""
    
    print("=== SEED PACK DEMO ===")
    print()
    
    # 1. Estatísticas gerais
    print("📊 Estatísticas do Seed Pack:")
    stats = seed_manager.get_category_stats()
    total_sources = 0
    for category, data in stats.items():
        count = data['total_sources']
        print(f"  {category}: {count} fontes")
        total_sources += count
    print(f"  Total: {total_sources} fontes")
    print()
    
    # 2. Busca por categoria
    print("🎨 UI & Design System:")
    ui_sources = seed_manager.get_sources_by_category(SeedCategory.UI_DESIGN)
    for source in ui_sources[:3]:  # Top 3
        print(f"  • {source.name} - {source.description[:60]}...")
    print()
    
    # 3. Web Stack
    print("🌐 Web Stack:")
    web_sources = seed_manager.get_sources_by_category(SeedCategory.WEB_STACK)
    for source in web_sources[:3]:  # Top 3
        print(f"  • {source.name} - {source.description[:60]}...")
    print()
    
    # 4. Busca por tags
    print("🔍 Busca por 'react':")
    react_sources = seed_manager.search_sources("react")
    for source in react_sources[:3]:
        print(f"  • {source.name} ({source.category.value})")
    print()
    
    # 5. Fontes de alta prioridade
    print("⭐ Fontes de Alta Prioridade:")
    high_priority = seed_manager.get_priority_sources(max_priority=1)
    for source in high_priority[:5]:
        print(f"  • {source.name} - {source.url}")
    print()
    
    # 6. OWASP Top 10
    print("🔒 OWASP Top 10 2021:")
    top_10 = OWASPSource.get_top_10_2021()
    for i, item in enumerate(top_10[:5], 1):
        print(f"  {i}. {item}")
    print("  ... (e mais 5)")
    print()
    
    # 7. Testing Pyramid
    print("🧪 Testing Pyramid:")
    pyramid = TestingSource.get_testing_pyramid()
    for level, description in pyramid.items():
        print(f"  • {level}: {description}")
    print()
    
    # 8. Common Issues
    print("🐛 Problemas Comuns do Next.js:")
    nextjs_issues = CommonFixesSource.get_nextjs_common_issues()
    for issue, description in list(nextjs_issues.items())[:3]:
        print(f"  • {issue}: {description}")
    print()
    
    # 9. Configurações de exemplo
    print("⚙️ Configuração ESLint para Next.js:")
    eslint_config = CodeQualitySource.get_eslint_nextjs_config()
    print("```json")
    print(eslint_config)
    print("```")
    print()
    
    # 10. Export para documentação
    print("📄 Exportando documentação...")
    doc_content = seed_manager.generate_documentation()
    print(f"Documentação gerada: {len(doc_content)} caracteres")
    print()
    
    print("✅ Demo concluída!")

def demo_specific_use_cases():
    """Demonstra casos de uso específicos"""
    
    print("\n=== CASOS DE USO ESPECÍFICOS ===")
    print()
    
    # Caso 1: Configurando um novo projeto Next.js
    print("🚀 Caso 1: Novo projeto Next.js com Shadcn/UI")
    
    # Buscar fontes relevantes
    nextjs_sources = seed_manager.search_sources("nextjs")
    shadcn_sources = seed_manager.search_sources("shadcn")
    tailwind_sources = seed_manager.search_sources("tailwind")
    
    print("Fontes recomendadas:")
    for source in nextjs_sources[:1]:
        print(f"  • {source.name}: {source.url}")
    for source in shadcn_sources[:1]:
        print(f"  • {source.name}: {source.url}")
    for source in tailwind_sources[:1]:
        print(f"  • {source.name}: {source.url}")
    print()
    
    # Caso 2: Implementando autenticação segura
    print("🔐 Caso 2: Autenticação segura")
    
    auth_sources = seed_manager.search_sources("auth")
    security_sources = seed_manager.get_sources_by_category(SeedCategory.PATTERNS_FIXES)
    owasp_sources = [s for s in security_sources if "owasp" in s.name.lower()]
    
    print("Fontes recomendadas:")
    for source in auth_sources[:1]:
        print(f"  • {source.name}: {source.url}")
    for source in owasp_sources[:1]:
        print(f"  • {source.name}: {source.url}")
    
    print("\nCheat sheets essenciais:")
    essential_sheets = OWASPSource.get_essential_cheat_sheets()
    for sheet in essential_sheets[:3]:
        print(f"  • {sheet}")
    print()
    
    # Caso 3: Setup de testing
    print("🧪 Caso 3: Setup completo de testing")
    
    testing_sources = seed_manager.search_sources("testing")
    jest_sources = seed_manager.search_sources("jest")
    playwright_sources = seed_manager.search_sources("playwright")
    
    print("Fontes recomendadas:")
    for source in jest_sources[:1]:
        print(f"  • {source.name}: {source.url}")
    for source in playwright_sources[:1]:
        print(f"  • {source.name}: {source.url}")
    
    print("\nConfiguração Jest:")
    jest_config = TestingSource.get_jest_config_example()
    print("```javascript")
    print(jest_config[:200] + "...")
    print("```")
    print()
    
    # Caso 4: Troubleshooting comum
    print("🔧 Caso 4: Troubleshooting de problemas comuns")
    
    print("Problemas React mais comuns:")
    react_issues = CommonFixesSource.get_react_common_issues()
    for issue, description in list(react_issues.items())[:3]:
        print(f"  • {issue}: {description}")
    
    print("\nProblemas TypeScript mais comuns:")
    ts_issues = CommonFixesSource.get_typescript_common_issues()
    for issue, description in list(ts_issues.items())[:3]:
        print(f"  • {issue}: {description}")
    print()

def demo_integration_examples():
    """Demonstra exemplos de integração"""
    
    print("\n=== EXEMPLOS DE INTEGRAÇÃO ===")
    print()
    
    # Stack completa recomendada
    print("📦 Stack Completa Recomendada:")
    
    recommended_stack = {
        "Frontend Framework": "Next.js 14 (App Router)",
        "Styling": "Tailwind CSS + Shadcn/UI",
        "UI Components": "Radix UI (via Shadcn/UI)",
        "Authentication": "NextAuth.js",
        "Database": "Prisma ORM",
        "Forms": "React Hook Form + Zod",
        "State Management": "Zustand",
        "Data Fetching": "TanStack Query",
        "Testing": "Jest + Playwright",
        "Code Quality": "ESLint + Prettier",
        "Security": "OWASP Guidelines"
    }
    
    for component, choice in recommended_stack.items():
        print(f"  • {component}: {choice}")
    print()
    
    # Comandos de setup
    print("⚡ Comandos de Setup Rápido:")
    setup_commands = [
        "npx create-next-app@latest my-app --typescript --tailwind --eslint --app",
        "cd my-app",
        "npx shadcn-ui@latest init",
        "npm install next-auth prisma @prisma/client",
        "npm install react-hook-form @hookform/resolvers zod",
        "npm install zustand @tanstack/react-query",
        "npm install --save-dev jest @testing-library/react @testing-library/jest-dom",
        "npm install --save-dev playwright @playwright/test",
        "npm install --save-dev prettier eslint-config-prettier"
    ]
    
    for i, cmd in enumerate(setup_commands, 1):
        print(f"  {i}. {cmd}")
    print()
    
    print("✅ Integração completa demonstrada!")

if __name__ == "__main__":
    # Executa todas as demos
    demo_seed_pack()
    demo_specific_use_cases()
    demo_integration_examples()
    
    print("\n🎉 Seed Pack está pronto para uso!")
    print("\n📚 Para usar em seu projeto:")
    print("  from seed_pack import seed_manager, SeedCategory")
    print("  sources = seed_manager.search_sources('react')")
    print("  ui_sources = seed_manager.get_sources_by_category(SeedCategory.UI_DESIGN)")