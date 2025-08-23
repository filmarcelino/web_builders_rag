#!/usr/bin/env python3
"""
UI & Design System Sources - Fontes para Sistemas de Design

Este módulo contém as fontes prioritárias para UI e Design Systems,
com foco em Shadcn/UI, Radix UI e recursos relacionados.
"""

from .seed_manager import SeedSource, SeedCategory, seed_manager

# Shadcn/UI - Fonte principal
shadcn_ui_source = SeedSource(
    name="shadcn/ui",
    category=SeedCategory.UI_DESIGN,
    url="https://ui.shadcn.com",
    description="Sistema de design moderno e acessível baseado em Radix UI e Tailwind CSS. Componentes copiáveis e customizáveis.",
    license="MIT",
    priority=1,
    tags=["ui", "design-system", "react", "tailwind", "radix", "accessibility", "typescript"],
    documentation_url="https://ui.shadcn.com/docs",
    github_url="https://github.com/shadcn-ui/ui",
    examples_url="https://ui.shadcn.com/examples",
    installation_guide="npx shadcn-ui@latest init",
    common_patterns=[
        "Instalação: npx shadcn-ui@latest init",
        "Adicionar componente: npx shadcn-ui@latest add button",
        "Customização via CSS variables no globals.css",
        "Uso com Next.js App Router",
        "Integração com Tailwind CSS",
        "Componentes acessíveis por padrão",
        "Suporte a dark mode nativo",
        "Estrutura de pastas: components/ui/"
    ],
    known_issues=[
        "Requer configuração inicial do Tailwind CSS",
        "Alguns componentes podem precisar de ajustes para SSR",
        "Dependência do Radix UI pode causar conflitos de versão",
        "Customização avançada requer conhecimento de CSS variables"
    ],
    alternatives=["Chakra UI", "Mantine", "Ant Design", "Material-UI"]
)

# Radix UI - Base de acessibilidade
radix_ui_source = SeedSource(
    name="Radix UI",
    category=SeedCategory.UI_DESIGN,
    url="https://radix-ui.com",
    description="Primitivos de UI de baixo nível e acessíveis para React. Base do Shadcn/UI.",
    license="MIT",
    priority=1,
    tags=["ui", "primitives", "accessibility", "react", "headless", "typescript"],
    documentation_url="https://radix-ui.com/docs",
    github_url="https://github.com/radix-ui/primitives",
    examples_url="https://radix-ui.com/docs/primitives/overview/introduction",
    installation_guide="npm install @radix-ui/react-*",
    common_patterns=[
        "Componentes headless (sem estilo)",
        "Acessibilidade WAI-ARIA completa",
        "Suporte a keyboard navigation",
        "Composição de componentes",
        "Controle total sobre styling",
        "SSR-friendly",
        "TypeScript nativo",
        "Uso com CSS-in-JS ou Tailwind"
    ],
    known_issues=[
        "Requer styling manual",
        "Curva de aprendizado para composição",
        "Alguns componentes são complexos de configurar",
        "Documentação pode ser verbosa"
    ],
    alternatives=["Headless UI", "Reach UI", "Ariakit", "React Aria"]
)

# Awesome Shadcn/UI - Curadoria comunitária
awesome_shadcn_source = SeedSource(
    name="Awesome shadcn/ui",
    category=SeedCategory.UI_DESIGN,
    url="https://github.com/birobirobiro/awesome-shadcn-ui",
    description="Lista curada de recursos, templates, exemplos e complementos para shadcn/ui.",
    license="MIT",
    priority=2,
    tags=["curadoria", "templates", "exemplos", "shadcn", "community", "resources"],
    documentation_url="https://github.com/birobirobiro/awesome-shadcn-ui/blob/main/README.md",
    github_url="https://github.com/birobirobiro/awesome-shadcn-ui",
    examples_url="https://github.com/birobirobiro/awesome-shadcn-ui#templates",
    installation_guide="Navegue pelos recursos listados no repositório",
    common_patterns=[
        "Templates completos de aplicações",
        "Componentes adicionais da comunidade",
        "Exemplos de integração",
        "Themes e variações de design",
        "Boilerplates específicos",
        "Plugins e extensões",
        "Showcases de projetos",
        "Recursos de aprendizado"
    ],
    known_issues=[
        "Qualidade varia entre recursos",
        "Nem todos os recursos são mantidos",
        "Pode conter dependências desatualizadas",
        "Documentação inconsistente entre projetos"
    ],
    alternatives=["shadcn/ui oficial", "Radix UI examples", "Tailwind UI"]
)

# Tailwind UI - Componentes premium
tailwind_ui_source = SeedSource(
    name="Tailwind UI",
    category=SeedCategory.UI_DESIGN,
    url="https://tailwindui.com",
    description="Componentes e templates profissionais feitos pela equipe do Tailwind CSS.",
    license="Comercial",
    priority=3,
    tags=["ui", "tailwind", "premium", "templates", "components", "professional"],
    documentation_url="https://tailwindui.com/documentation",
    github_url="https://github.com/tailwindlabs/tailwindui",
    examples_url="https://tailwindui.com/components",
    installation_guide="Requer licença paga - acesso via tailwindui.com",
    common_patterns=[
        "Componentes copy-paste",
        "Templates de páginas completas",
        "Responsive design",
        "Dark mode support",
        "Múltiplas variações",
        "Código HTML + React + Vue",
        "Figma design files",
        "Regular updates"
    ],
    known_issues=[
        "Requer licença paga",
        "Não é um package npm",
        "Customização manual necessária",
        "Pode ser overkill para projetos simples"
    ],
    alternatives=["shadcn/ui", "Headless UI", "Chakra UI", "Mantine"]
)

# Headless UI - Alternativa oficial
headless_ui_source = SeedSource(
    name="Headless UI",
    category=SeedCategory.UI_DESIGN,
    url="https://headlessui.com",
    description="Componentes UI completamente sem estilo e totalmente acessíveis, feitos pela equipe do Tailwind CSS.",
    license="MIT",
    priority=2,
    tags=["ui", "headless", "accessibility", "tailwind", "react", "vue", "typescript"],
    documentation_url="https://headlessui.com/react",
    github_url="https://github.com/tailwindlabs/headlessui",
    examples_url="https://headlessui.com/react/menu",
    installation_guide="npm install @headlessui/react",
    common_patterns=[
        "Componentes totalmente acessíveis",
        "Integração perfeita com Tailwind",
        "Suporte React e Vue",
        "TypeScript first",
        "Keyboard navigation",
        "Focus management",
        "ARIA attributes automáticos",
        "Composição flexível"
    ],
    known_issues=[
        "Limitado conjunto de componentes",
        "Requer styling manual completo",
        "Menos componentes que Radix UI",
        "Documentação pode ser básica"
    ],
    alternatives=["Radix UI", "Reach UI", "Ariakit", "React Aria"]
)

# Lista de todas as fontes UI
ui_sources = [
    shadcn_ui_source,
    radix_ui_source,
    awesome_shadcn_source,
    tailwind_ui_source,
    headless_ui_source
]

# Registra todas as fontes no seed_manager
for source in ui_sources:
    seed_manager.add_source(source)

# Classes para exportação
class ShadcnUISource:
    """Classe de conveniência para acessar informações do Shadcn/UI"""
    
    @staticmethod
    def get_installation_command() -> str:
        return "npx shadcn-ui@latest init"
    
    @staticmethod
    def get_add_component_command(component: str) -> str:
        return f"npx shadcn-ui@latest add {component}"
    
    @staticmethod
    def get_common_components() -> list:
        return [
            "button", "input", "label", "textarea", "select",
            "dialog", "dropdown-menu", "popover", "tooltip",
            "card", "badge", "avatar", "separator",
            "table", "form", "sheet", "tabs", "accordion"
        ]
    
    @staticmethod
    def get_setup_steps() -> list:
        return [
            "1. npx shadcn-ui@latest init",
            "2. Configurar tailwind.config.js",
            "3. Adicionar CSS variables no globals.css",
            "4. Instalar componentes: npx shadcn-ui@latest add [component]",
            "5. Importar e usar componentes"
        ]

class RadixUISource:
    """Classe de conveniência para acessar informações do Radix UI"""
    
    @staticmethod
    def get_installation_command(component: str) -> str:
        return f"npm install @radix-ui/react-{component}"
    
    @staticmethod
    def get_available_primitives() -> list:
        return [
            "accordion", "alert-dialog", "aspect-ratio", "avatar",
            "checkbox", "collapsible", "context-menu", "dialog",
            "dropdown-menu", "form", "hover-card", "label",
            "menubar", "navigation-menu", "popover", "progress",
            "radio-group", "scroll-area", "select", "separator",
            "slider", "switch", "tabs", "toast", "toggle",
            "toggle-group", "toolbar", "tooltip"
        ]
    
    @staticmethod
    def get_accessibility_features() -> list:
        return [
            "WAI-ARIA compliant",
            "Keyboard navigation",
            "Focus management",
            "Screen reader support",
            "High contrast mode",
            "Reduced motion support",
            "RTL support",
            "Touch-friendly"
        ]

class AwesomeShadcnSource:
    """Classe de conveniência para recursos da comunidade Shadcn/UI"""
    
    @staticmethod
    def get_template_categories() -> list:
        return [
            "Admin Dashboards",
            "Landing Pages",
            "E-commerce",
            "SaaS Applications",
            "Portfolios",
            "Blogs",
            "Documentation Sites",
            "Mobile Apps"
        ]
    
    @staticmethod
    def get_popular_templates() -> list:
        return [
            "shadcn-admin",
            "taxonomy",
            "skateshop",
            "acme-corp",
            "next-saas-stripe-starter",
            "shadcn-landing-page",
            "shadcn-dashboard",
            "shadcn-table"
        ]