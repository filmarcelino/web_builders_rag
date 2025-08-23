#!/usr/bin/env python3
"""
Boilerplates Sources - Fontes para Boilerplates e Scaffolds

Este módulo contém as fontes prioritárias para boilerplates, scaffolds e
templates curados para desenvolvimento rápido de aplicações.
"""

from .seed_manager import SeedSource, SeedCategory, seed_manager

# Vercel Examples - Exemplos oficiais
vercel_examples_source = SeedSource(
    name="Vercel Examples",
    category=SeedCategory.BOILERPLATES,
    url="https://github.com/vercel/examples",
    description="Coleção oficial de exemplos e templates para Next.js e outras tecnologias web modernas.",
    license="MIT",
    priority=1,
    tags=["nextjs", "examples", "templates", "vercel", "official", "showcase"],
    documentation_url="https://github.com/vercel/examples/blob/main/README.md",
    github_url="https://github.com/vercel/examples",
    examples_url="https://vercel.com/templates",
    installation_guide="npx create-next-app --example [example-name]",
    common_patterns=[
        "Next.js App Router examples",
        "API Routes patterns",
        "Database integrations",
        "Authentication examples",
        "E-commerce templates",
        "CMS integrations",
        "Edge functions",
        "Middleware examples",
        "Deployment configurations",
        "Performance optimizations"
    ],
    known_issues=[
        "Qualidade varia entre exemplos",
        "Alguns podem estar desatualizados",
        "Documentação limitada em alguns",
        "Dependências podem ter vulnerabilidades",
        "Nem todos seguem best practices"
    ],
    alternatives=["Next.js official examples", "T3 Stack", "Create T3 App", "Refine"]
)

# T3 Stack - Stack opinionado
t3_stack_source = SeedSource(
    name="T3 Stack (Create T3 App)",
    category=SeedCategory.BOILERPLATES,
    url="https://create.t3.gg",
    description="Stack opinionado e type-safe para Next.js com Prisma, tRPC, NextAuth.js e Tailwind CSS.",
    license="MIT",
    priority=1,
    tags=["nextjs", "typescript", "prisma", "trpc", "nextauth", "tailwind", "type-safe"],
    documentation_url="https://create.t3.gg/en/introduction",
    github_url="https://github.com/t3-oss/create-t3-app",
    examples_url="https://create.t3.gg/en/deployment/vercel",
    installation_guide="npm create t3-app@latest",
    common_patterns=[
        "Type-safe API com tRPC",
        "Database com Prisma ORM",
        "Autenticação com NextAuth.js",
        "Styling com Tailwind CSS",
        "Folder structure opinionada",
        "TypeScript configurado",
        "ESLint e Prettier",
        "Environment variables",
        "Deployment ready",
        "Best practices enforced"
    ],
    known_issues=[
        "Opinionado demais para alguns casos",
        "Curva de aprendizado para tRPC",
        "Bundle size pode ser grande",
        "Configuração complexa para customizar",
        "Dependências específicas"
    ],
    alternatives=["Next.js default", "Remix", "SvelteKit", "Nuxt.js"]
)

# Refine - Framework para admin dashboards
refine_source = SeedSource(
    name="Refine",
    category=SeedCategory.BOILERPLATES,
    url="https://refine.dev",
    description="Framework React para construir rapidamente admin panels, dashboards e aplicações CRUD.",
    license="MIT",
    priority=2,
    tags=["admin", "dashboard", "crud", "react", "framework", "data-provider"],
    documentation_url="https://refine.dev/docs",
    github_url="https://github.com/refinedev/refine",
    examples_url="https://refine.dev/examples",
    installation_guide="npm create refine-app@latest",
    common_patterns=[
        "Data providers para APIs",
        "Auth providers",
        "UI framework agnostic",
        "CRUD operations automáticas",
        "Routing integrado",
        "Form handling",
        "Table components",
        "Real-time updates",
        "Multi-tenancy support",
        "Internationalization"
    ],
    known_issues=[
        "Específico para admin interfaces",
        "Curva de aprendizado",
        "Documentação pode ser confusa",
        "Customização limitada em alguns casos",
        "Bundle size considerável"
    ],
    alternatives=["React Admin", "Admin Bro", "Strapi Admin", "Custom admin"]
)

# Shadcn/UI Templates - Templates da comunidade
shadcn_templates_source = SeedSource(
    name="Shadcn/UI Templates",
    category=SeedCategory.BOILERPLATES,
    url="https://ui.shadcn.com/examples",
    description="Templates e exemplos oficiais usando shadcn/ui para diferentes tipos de aplicações.",
    license="MIT",
    priority=1,
    tags=["shadcn", "templates", "ui", "examples", "dashboard", "forms"],
    documentation_url="https://ui.shadcn.com/docs",
    github_url="https://github.com/shadcn-ui/ui",
    examples_url="https://ui.shadcn.com/examples/dashboard",
    installation_guide="npx create-next-app -e https://github.com/shadcn-ui/next-template",
    common_patterns=[
        "Dashboard layouts",
        "Authentication forms",
        "Data tables",
        "Card layouts",
        "Navigation patterns",
        "Form examples",
        "Chart integrations",
        "Modal patterns",
        "Responsive designs",
        "Dark mode support"
    ],
    known_issues=[
        "Templates limitados",
        "Requer configuração manual",
        "Nem todos são completos",
        "Documentação básica",
        "Customização necessária"
    ],
    alternatives=["Tailwind UI", "Headless UI examples", "Radix templates"]
)

# Next.js Commerce - E-commerce template
nextjs_commerce_source = SeedSource(
    name="Next.js Commerce",
    category=SeedCategory.BOILERPLATES,
    url="https://nextjs.org/commerce",
    description="Template de e-commerce de alta performance construído com Next.js e Vercel.",
    license="MIT",
    priority=2,
    tags=["ecommerce", "nextjs", "commerce", "shopify", "bigcommerce", "template"],
    documentation_url="https://github.com/vercel/commerce/blob/main/README.md",
    github_url="https://github.com/vercel/commerce",
    examples_url="https://demo.vercel.store",
    installation_guide="npx create-next-app --example commerce",
    common_patterns=[
        "Product catalog",
        "Shopping cart",
        "Checkout flow",
        "User authentication",
        "Payment integration",
        "Inventory management",
        "SEO optimization",
        "Performance optimization",
        "Mobile responsive",
        "Analytics integration"
    ],
    known_issues=[
        "Complexo para customizar",
        "Dependências específicas",
        "Requer backend commerce",
        "Configuração inicial complexa",
        "Bundle size grande"
    ],
    alternatives=["Medusa.js", "Saleor", "WooCommerce", "Shopify Hydrogen"]
)

# Taxonomy - Exemplo moderno
taxonomy_source = SeedSource(
    name="Taxonomy",
    category=SeedCategory.BOILERPLATES,
    url="https://tx.shadcn.com",
    description="Aplicação moderna construída com Next.js 13, Prisma, PlanetScale, Auth.js e shadcn/ui.",
    license="MIT",
    priority=2,
    tags=["nextjs", "prisma", "planetscale", "authjs", "shadcn", "modern", "app-router"],
    documentation_url="https://github.com/shadcn-ui/taxonomy/blob/main/README.md",
    github_url="https://github.com/shadcn-ui/taxonomy",
    examples_url="https://tx.shadcn.com",
    installation_guide="git clone https://github.com/shadcn-ui/taxonomy.git",
    common_patterns=[
        "Next.js 13 App Router",
        "Server Components",
        "Database com Prisma",
        "Authentication com Auth.js",
        "UI com shadcn/ui",
        "Styling com Tailwind",
        "TypeScript setup",
        "Subscription billing",
        "MDX content",
        "SEO optimization"
    ],
    known_issues=[
        "Exemplo específico",
        "Requer configuração manual",
        "Dependências podem desatualizar",
        "Não é um template genérico",
        "Complexo para iniciantes"
    ],
    alternatives=["T3 Stack", "Create Next App", "Vercel templates"]
)

# Lista de todas as fontes de boilerplates
boilerplate_sources = [
    vercel_examples_source,
    t3_stack_source,
    refine_source,
    shadcn_templates_source,
    nextjs_commerce_source,
    taxonomy_source
]

# Registra todas as fontes no seed_manager
for source in boilerplate_sources:
    seed_manager.add_source(source)

# Classes para exportação
class VercelExamplesSource:
    """Classe de conveniência para Vercel Examples"""
    
    @staticmethod
    def get_popular_examples() -> list:
        return [
            "hello-world",
            "blog-starter",
            "cms-contentful",
            "auth-auth0",
            "with-tailwindcss",
            "api-routes",
            "edge-functions",
            "with-prisma",
            "with-supabase",
            "ecommerce-shopify"
        ]
    
    @staticmethod
    def get_categories() -> list:
        return [
            "Authentication",
            "CMS",
            "Database",
            "E-commerce",
            "Edge Functions",
            "Styling",
            "API",
            "Analytics",
            "Deployment",
            "Performance"
        ]
    
    @staticmethod
    def get_create_command(example: str) -> str:
        return f"npx create-next-app --example {example}"

class T3StackSource:
    """Classe de conveniência para T3 Stack"""
    
    @staticmethod
    def get_included_packages() -> dict:
        return {
            "Next.js": "React framework",
            "TypeScript": "Type safety",
            "Tailwind CSS": "Styling",
            "tRPC": "Type-safe APIs",
            "Prisma": "Database ORM",
            "NextAuth.js": "Authentication"
        }
    
    @staticmethod
    def get_optional_packages() -> list:
        return [
            "Prisma",
            "NextAuth.js",
            "tRPC",
            "Tailwind CSS"
        ]
    
    @staticmethod
    def get_folder_structure() -> dict:
        return {
            "src/": "Source code",
            "src/pages/": "Pages (if using Pages Router)",
            "src/app/": "App Router directory",
            "src/server/": "Server-side code",
            "src/utils/": "Utility functions",
            "src/styles/": "Global styles",
            "prisma/": "Database schema",
            "public/": "Static assets"
        }

class RefineSource:
    """Classe de conveniência para Refine"""
    
    @staticmethod
    def get_supported_ui_frameworks() -> list:
        return [
            "Ant Design",
            "Material UI",
            "Mantine",
            "Chakra UI",
            "Headless"
        ]
    
    @staticmethod
    def get_data_providers() -> list:
        return [
            "REST API",
            "GraphQL",
            "Supabase",
            "Strapi",
            "Airtable",
            "Firebase",
            "NestJS",
            "Custom"
        ]
    
    @staticmethod
    def get_auth_providers() -> list:
        return [
            "Auth0",
            "Firebase",
            "Supabase",
            "Keycloak",
            "Custom"
        ]

class ShadcnTemplatesSource:
    """Classe de conveniência para Shadcn Templates"""
    
    @staticmethod
    def get_available_examples() -> list:
        return [
            "Dashboard",
            "Authentication",
            "Cards",
            "Tasks",
            "Playground",
            "Forms",
            "Music",
            "Mail"
        ]
    
    @staticmethod
    def get_dashboard_features() -> list:
        return [
            "Sidebar navigation",
            "Data tables",
            "Charts integration",
            "User management",
            "Settings panel",
            "Dark mode toggle",
            "Responsive layout",
            "Search functionality"
        ]

class NextJSCommerceSource:
    """Classe de conveniência para Next.js Commerce"""
    
    @staticmethod
    def get_supported_providers() -> list:
        return [
            "Shopify",
            "BigCommerce",
            "Vendure",
            "Saleor",
            "Spree",
            "Ordercloud"
        ]
    
    @staticmethod
    def get_features() -> list:
        return [
            "Product catalog",
            "Search & filtering",
            "Shopping cart",
            "Checkout",
            "User accounts",
            "Order history",
            "Wishlist",
            "Reviews",
            "SEO optimization",
            "Analytics"
        ]
    
    @staticmethod
    def get_performance_features() -> list:
        return [
            "Image optimization",
            "Code splitting",
            "Lazy loading",
            "CDN integration",
            "Caching strategies",
            "Bundle optimization",
            "Core Web Vitals",
            "Edge functions"
        ]