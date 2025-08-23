#!/usr/bin/env python3
"""
Web Stack Sources - Fontes para Stack de Desenvolvimento Web

Este módulo contém as fontes prioritárias para desenvolvimento web moderno,
com foco em Next.js, Tailwind CSS, NextAuth.js, Prisma e ferramentas relacionadas.
"""

from .seed_manager import SeedSource, SeedCategory, seed_manager

# Next.js - Framework React principal
nextjs_source = SeedSource(
    name="Next.js",
    category=SeedCategory.WEB_STACK,
    url="https://nextjs.org",
    description="Framework React para produção com App Router, SSR, SSG, API Routes e otimizações automáticas.",
    license="MIT",
    priority=1,
    tags=["react", "framework", "ssr", "ssg", "app-router", "typescript", "vercel"],
    documentation_url="https://nextjs.org/docs",
    github_url="https://github.com/vercel/next.js",
    examples_url="https://github.com/vercel/next.js/tree/canary/examples",
    installation_guide="npx create-next-app@latest",
    common_patterns=[
        "App Router (Next.js 13+): app/ directory",
        "Server Components por padrão",
        "Client Components com 'use client'",
        "API Routes: app/api/route.ts",
        "Layouts aninhados: layout.tsx",
        "Loading UI: loading.tsx",
        "Error Boundaries: error.tsx",
        "Metadata API para SEO",
        "Image optimization com next/image",
        "Font optimization com next/font"
    ],
    known_issues=[
        "App Router ainda em evolução",
        "Hydration mismatch em SSR",
        "Bundle size pode crescer rapidamente",
        "Configuração complexa para casos avançados",
        "Debugging pode ser desafiador"
    ],
    alternatives=["Remix", "Gatsby", "Vite + React", "Create React App"]
)

# Tailwind CSS - Framework CSS utilitário
tailwind_source = SeedSource(
    name="Tailwind CSS",
    category=SeedCategory.WEB_STACK,
    url="https://tailwindcss.com",
    description="Framework CSS utilitário para criação rápida de interfaces customizadas.",
    license="MIT",
    priority=1,
    tags=["css", "utility-first", "responsive", "dark-mode", "jit", "purge"],
    documentation_url="https://tailwindcss.com/docs",
    github_url="https://github.com/tailwindlabs/tailwindcss",
    examples_url="https://tailwindui.com/components",
    installation_guide="npm install -D tailwindcss postcss autoprefixer",
    common_patterns=[
        "Utility-first approach",
        "Responsive design: sm:, md:, lg:, xl:, 2xl:",
        "Dark mode: dark: prefix",
        "Hover states: hover: prefix",
        "Focus states: focus: prefix",
        "Custom colors via CSS variables",
        "Component extraction com @apply",
        "JIT compilation para performance",
        "Purging unused CSS",
        "Plugin system para extensões"
    ],
    known_issues=[
        "HTML pode ficar verboso",
        "Curva de aprendizado inicial",
        "Configuração de purge crítica",
        "Debugging de classes pode ser difícil",
        "Conflitos com CSS existente"
    ],
    alternatives=["Bootstrap", "Bulma", "Chakra UI", "Styled Components"]
)

# NextAuth.js - Autenticação
nextauth_source = SeedSource(
    name="NextAuth.js",
    category=SeedCategory.WEB_STACK,
    url="https://next-auth.js.org",
    description="Solução completa de autenticação para Next.js com suporte a múltiplos providers.",
    license="ISC",
    priority=1,
    tags=["auth", "authentication", "oauth", "jwt", "session", "nextjs"],
    documentation_url="https://next-auth.js.org/getting-started/introduction",
    github_url="https://github.com/nextauthjs/next-auth",
    examples_url="https://next-auth.js.org/getting-started/example",
    installation_guide="npm install next-auth",
    common_patterns=[
        "API Route: app/api/auth/[...nextauth]/route.ts",
        "Providers: Google, GitHub, Discord, etc.",
        "Database adapters: Prisma, MongoDB, etc.",
        "JWT ou Database sessions",
        "Middleware para proteção de rotas",
        "useSession hook no client",
        "getServerSession no server",
        "Callbacks para customização",
        "CSRF protection automático",
        "TypeScript support"
    ],
    known_issues=[
        "Configuração inicial complexa",
        "Documentação pode ser confusa",
        "Debugging de providers OAuth",
        "Session management edge cases",
        "Migração entre versões"
    ],
    alternatives=["Auth0", "Firebase Auth", "Supabase Auth", "Clerk"]
)

# Prisma - ORM moderno
prisma_source = SeedSource(
    name="Prisma",
    category=SeedCategory.WEB_STACK,
    url="https://prisma.io",
    description="ORM moderno e type-safe para Node.js e TypeScript com geração automática de cliente.",
    license="Apache 2.0",
    priority=1,
    tags=["orm", "database", "typescript", "postgresql", "mysql", "sqlite", "mongodb"],
    documentation_url="https://prisma.io/docs",
    github_url="https://github.com/prisma/prisma",
    examples_url="https://github.com/prisma/prisma-examples",
    installation_guide="npm install prisma @prisma/client",
    common_patterns=[
        "Schema definition: schema.prisma",
        "Database migrations: prisma migrate",
        "Client generation: prisma generate",
        "Type-safe queries",
        "Relation queries",
        "Transaction support",
        "Connection pooling",
        "Prisma Studio para GUI",
        "Seed scripts",
        "Multiple database support"
    ],
    known_issues=[
        "Bundle size pode ser grande",
        "Cold start latency",
        "Limitações em edge runtime",
        "Migrations podem ser complexas",
        "Performance em queries complexas"
    ],
    alternatives=["Drizzle", "TypeORM", "Sequelize", "Knex.js"]
)

# UploadThing - Upload de arquivos
uploadthing_source = SeedSource(
    name="UploadThing",
    category=SeedCategory.WEB_STACK,
    url="https://uploadthing.com",
    description="Solução simples e type-safe para upload de arquivos em aplicações Next.js.",
    license="MIT",
    priority=2,
    tags=["upload", "files", "nextjs", "typescript", "s3", "cdn"],
    documentation_url="https://docs.uploadthing.com",
    github_url="https://github.com/pingdotgg/uploadthing",
    examples_url="https://docs.uploadthing.com/getting-started/appdir",
    installation_guide="npm install uploadthing @uploadthing/react",
    common_patterns=[
        "File router definition",
        "Type-safe upload endpoints",
        "React hooks: useUploadThing",
        "Progress tracking",
        "File validation",
        "Image optimization",
        "CDN delivery",
        "Webhook support",
        "Multiple file types",
        "Drag and drop UI"
    ],
    known_issues=[
        "Requer conta UploadThing",
        "Limitações no plano gratuito",
        "Dependência de serviço externo",
        "Customização limitada",
        "Pricing pode escalar"
    ],
    alternatives=["AWS S3 + Presigned URLs", "Cloudinary", "Supabase Storage", "tus.io"]
)

# tus.io - Upload resiliente
tus_protocol_source = SeedSource(
    name="tus.io",
    category=SeedCategory.WEB_STACK,
    url="https://tus.io",
    description="Protocolo aberto para upload de arquivos resiliente e resumível.",
    license="MIT",
    priority=3,
    tags=["upload", "resumable", "protocol", "open-standard", "resilient"],
    documentation_url="https://tus.io/protocols/resumable-upload.html",
    github_url="https://github.com/tus",
    examples_url="https://tus.io/implementations.html",
    installation_guide="npm install tus-js-client",
    common_patterns=[
        "Resumable uploads",
        "Chunk-based transfer",
        "Progress tracking",
        "Error recovery",
        "Cross-platform support",
        "Server implementations",
        "Client libraries",
        "HTTP-based protocol",
        "Metadata support",
        "Hooks and events"
    ],
    known_issues=[
        "Requer implementação server-side",
        "Complexidade de setup",
        "Não é plug-and-play",
        "Debugging pode ser difícil",
        "Configuração de CORS"
    ],
    alternatives=["UploadThing", "AWS S3 Multipart", "Google Cloud Storage", "Azure Blob"]
)

# PapaParse - Parsing CSV
papaparse_source = SeedSource(
    name="PapaParse",
    category=SeedCategory.WEB_STACK,
    url="https://papaparse.com",
    description="Parser CSV rápido e poderoso para JavaScript no browser e Node.js.",
    license="MIT",
    priority=2,
    tags=["csv", "parser", "javascript", "browser", "nodejs", "streaming"],
    documentation_url="https://papaparse.com/docs",
    github_url="https://github.com/mholt/PapaParse",
    examples_url="https://papaparse.com/demo",
    installation_guide="npm install papaparse",
    common_patterns=[
        "Parse CSV strings: Papa.parse(csv)",
        "Parse files: Papa.parse(file)",
        "Streaming large files",
        "Header detection automática",
        "Type conversion",
        "Error handling",
        "Progress callbacks",
        "Worker threads",
        "Custom delimiters",
        "JSON output"
    ],
    known_issues=[
        "Memory usage com arquivos grandes",
        "Performance em datasets enormes",
        "Encoding issues",
        "Browser compatibility edge cases",
        "Type inference limitada"
    ],
    alternatives=["csv-parse", "fast-csv", "d3-dsv", "xlsx"]
)

# csv-parse - Parser Node.js
csv_parse_source = SeedSource(
    name="csv-parse",
    category=SeedCategory.WEB_STACK,
    url="https://csv.js.org/parse/",
    description="Parser CSV para Node.js com suporte a streaming e transformações.",
    license="MIT",
    priority=3,
    tags=["csv", "nodejs", "streaming", "transform", "parser"],
    documentation_url="https://csv.js.org/parse/api/",
    github_url="https://github.com/adaltas/node-csv",
    examples_url="https://csv.js.org/parse/examples/",
    installation_guide="npm install csv-parse",
    common_patterns=[
        "Stream processing",
        "Transform functions",
        "Column mapping",
        "Type casting",
        "Error handling",
        "Async iteration",
        "Pipe operations",
        "Memory efficient",
        "Custom options",
        "Validation hooks"
    ],
    known_issues=[
        "Node.js específico",
        "Curva de aprendizado para streams",
        "Configuração complexa",
        "Debugging de transforms",
        "Error propagation"
    ],
    alternatives=["PapaParse", "fast-csv", "csv-parser", "node-csv"]
)

# Lista de todas as fontes web stack
web_stack_sources = [
    nextjs_source,
    tailwind_source,
    nextauth_source,
    prisma_source,
    uploadthing_source,
    tus_protocol_source,
    papaparse_source,
    csv_parse_source
]

# Registra todas as fontes no seed_manager
for source in web_stack_sources:
    seed_manager.add_source(source)

# Classes para exportação
class NextJSSource:
    """Classe de conveniência para Next.js"""
    
    @staticmethod
    def get_create_command(name: str = "my-app") -> str:
        return f"npx create-next-app@latest {name}"
    
    @staticmethod
    def get_app_router_structure() -> dict:
        return {
            "app/": "App Router directory",
            "app/layout.tsx": "Root layout",
            "app/page.tsx": "Home page",
            "app/loading.tsx": "Loading UI",
            "app/error.tsx": "Error boundary",
            "app/not-found.tsx": "404 page",
            "app/api/": "API routes",
            "app/globals.css": "Global styles"
        }
    
    @staticmethod
    def get_essential_packages() -> list:
        return [
            "@types/node",
            "@types/react",
            "@types/react-dom",
            "typescript",
            "tailwindcss",
            "postcss",
            "autoprefixer"
        ]

class TailwindSource:
    """Classe de conveniência para Tailwind CSS"""
    
    @staticmethod
    def get_init_command() -> str:
        return "npx tailwindcss init -p"
    
    @staticmethod
    def get_config_template() -> str:
        return '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}'''
    
    @staticmethod
    def get_globals_css() -> str:
        return '''@tailwind base;
@tailwind components;
@tailwind utilities;'''

class NextAuthSource:
    """Classe de conveniência para NextAuth.js"""
    
    @staticmethod
    def get_env_variables() -> list:
        return [
            "NEXTAUTH_URL",
            "NEXTAUTH_SECRET",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "GITHUB_ID",
            "GITHUB_SECRET"
        ]
    
    @staticmethod
    def get_popular_providers() -> list:
        return [
            "Google",
            "GitHub",
            "Discord",
            "Twitter",
            "Facebook",
            "Apple",
            "Auth0",
            "Credentials"
        ]

class PrismaSource:
    """Classe de conveniência para Prisma"""
    
    @staticmethod
    def get_init_command() -> str:
        return "npx prisma init"
    
    @staticmethod
    def get_common_commands() -> dict:
        return {
            "generate": "npx prisma generate",
            "migrate": "npx prisma migrate dev",
            "studio": "npx prisma studio",
            "seed": "npx prisma db seed",
            "reset": "npx prisma migrate reset",
            "deploy": "npx prisma migrate deploy"
        }
    
    @staticmethod
    def get_supported_databases() -> list:
        return [
            "PostgreSQL",
            "MySQL",
            "SQLite",
            "SQL Server",
            "MongoDB",
            "CockroachDB"
        ]

class UploadSource:
    """Classe de conveniência para soluções de upload"""
    
    @staticmethod
    def get_uploadthing_setup() -> list:
        return [
            "1. Criar conta em uploadthing.com",
            "2. npm install uploadthing @uploadthing/react",
            "3. Configurar UPLOADTHING_SECRET",
            "4. Criar file router",
            "5. Implementar upload component"
        ]
    
    @staticmethod
    def get_tus_benefits() -> list:
        return [
            "Uploads resumíveis",
            "Protocolo aberto",
            "Resiliente a falhas",
            "Cross-platform",
            "Self-hosted",
            "Sem vendor lock-in"
        ]

class CSVParsingSource:
    """Classe de conveniência para parsing CSV"""
    
    @staticmethod
    def get_papaparse_example() -> str:
        return '''import Papa from 'papaparse';

Papa.parse(file, {
  header: true,
  complete: (results) => {
    console.log(results.data);
  }
});'''
    
    @staticmethod
    def get_csv_parse_example() -> str:
        return '''import { parse } from 'csv-parse';
import fs from 'fs';

fs.createReadStream('input.csv')
  .pipe(parse({ headers: true }))
  .on('data', (row) => console.log(row));'''