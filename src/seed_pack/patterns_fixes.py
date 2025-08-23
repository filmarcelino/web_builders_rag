#!/usr/bin/env python3
"""
Patterns & Fix-Patterns Sources - Fontes para Padrões e Correções

Este módulo contém as fontes prioritárias para padrões de desenvolvimento,
segurança, testing e soluções para problemas comuns.
"""

from .seed_manager import SeedSource, SeedCategory, seed_manager

# OWASP - Segurança web
owasp_source = SeedSource(
    name="OWASP Cheat Sheets",
    category=SeedCategory.PATTERNS_FIXES,
    url="https://cheatsheetseries.owasp.org",
    description="Série de cheat sheets sobre segurança web com práticas recomendadas e padrões seguros.",
    license="Creative Commons",
    priority=1,
    tags=["security", "owasp", "web-security", "best-practices", "cheat-sheets"],
    documentation_url="https://cheatsheetseries.owasp.org/index.html",
    github_url="https://github.com/OWASP/CheatSheetSeries",
    examples_url="https://cheatsheetseries.owasp.org/cheatsheets/",
    installation_guide="Consulte os cheat sheets online ou clone o repositório",
    common_patterns=[
        "Input Validation patterns",
        "Authentication best practices",
        "Session Management",
        "Cross-Site Scripting (XSS) prevention",
        "SQL Injection prevention",
        "CSRF protection",
        "Secure Headers configuration",
        "Password Storage guidelines",
        "API Security patterns",
        "Content Security Policy (CSP)"
    ],
    known_issues=[
        "Pode ser overwhelming para iniciantes",
        "Nem todos os padrões são aplicáveis",
        "Requer conhecimento de segurança",
        "Implementação pode ser complexa",
        "Atualizações constantes necessárias"
    ],
    alternatives=["NIST Guidelines", "CIS Controls", "SANS Secure Coding", "Mozilla Security"]
)

# Jest - Testing framework
jest_source = SeedSource(
    name="Jest",
    category=SeedCategory.PATTERNS_FIXES,
    url="https://jestjs.io",
    description="Framework de testing JavaScript com foco em simplicidade e suporte nativo para React.",
    license="MIT",
    priority=1,
    tags=["testing", "javascript", "react", "unit-tests", "mocking", "coverage"],
    documentation_url="https://jestjs.io/docs/getting-started",
    github_url="https://github.com/facebook/jest",
    examples_url="https://jestjs.io/docs/tutorial-react",
    installation_guide="npm install --save-dev jest",
    common_patterns=[
        "Unit testing: test() ou it()",
        "Test suites: describe()",
        "Mocking: jest.mock()",
        "Async testing: async/await",
        "Snapshot testing",
        "Coverage reports",
        "Setup/teardown: beforeEach, afterEach",
        "Custom matchers",
        "Testing React components",
        "Integration with CI/CD"
    ],
    known_issues=[
        "Configuração pode ser complexa",
        "Performance em projetos grandes",
        "Mocking pode ser confuso",
        "Debugging de testes",
        "Snapshot tests podem ser frágeis"
    ],
    alternatives=["Vitest", "Mocha", "Jasmine", "Testing Library"]
)

# Playwright - E2E testing
playwright_source = SeedSource(
    name="Playwright",
    category=SeedCategory.PATTERNS_FIXES,
    url="https://playwright.dev",
    description="Framework moderno para automação e testing end-to-end de aplicações web.",
    license="Apache 2.0",
    priority=1,
    tags=["e2e-testing", "automation", "browser-testing", "playwright", "cross-browser"],
    documentation_url="https://playwright.dev/docs/intro",
    github_url="https://github.com/microsoft/playwright",
    examples_url="https://playwright.dev/docs/writing-tests",
    installation_guide="npm init playwright@latest",
    common_patterns=[
        "Page Object Model",
        "Auto-waiting for elements",
        "Cross-browser testing",
        "Mobile testing",
        "API testing",
        "Visual comparisons",
        "Network interception",
        "Parallel execution",
        "Test generation",
        "CI/CD integration"
    ],
    known_issues=[
        "Curva de aprendizado",
        "Configuração inicial complexa",
        "Debugging pode ser difícil",
        "Flaky tests em alguns casos",
        "Resource intensive"
    ],
    alternatives=["Cypress", "Selenium", "Puppeteer", "TestCafe"]
)

# ESLint - Code quality
eslint_source = SeedSource(
    name="ESLint",
    category=SeedCategory.PATTERNS_FIXES,
    url="https://eslint.org",
    description="Ferramenta de linting para identificar e corrigir problemas em código JavaScript/TypeScript.",
    license="MIT",
    priority=1,
    tags=["linting", "code-quality", "javascript", "typescript", "static-analysis"],
    documentation_url="https://eslint.org/docs/latest/",
    github_url="https://github.com/eslint/eslint",
    examples_url="https://eslint.org/docs/latest/use/getting-started",
    installation_guide="npm install eslint --save-dev",
    common_patterns=[
        "Configuration files: .eslintrc.js",
        "Rule configuration",
        "Extends popular configs",
        "Custom rules",
        "Ignore patterns: .eslintignore",
        "IDE integration",
        "Pre-commit hooks",
        "Auto-fixing: --fix",
        "TypeScript support",
        "React/Next.js configs"
    ],
    known_issues=[
        "Configuração pode ser overwhelming",
        "Conflitos entre rules",
        "Performance em projetos grandes",
        "False positives",
        "Migração entre versões"
    ],
    alternatives=["TSLint (deprecated)", "JSHint", "StandardJS", "Biome"]
)

# Prettier - Code formatting
prettier_source = SeedSource(
    name="Prettier",
    category=SeedCategory.PATTERNS_FIXES,
    url="https://prettier.io",
    description="Formatador de código opinativo que garante estilo consistente em projetos.",
    license="MIT",
    priority=1,
    tags=["formatting", "code-style", "javascript", "typescript", "consistency"],
    documentation_url="https://prettier.io/docs/en/",
    github_url="https://github.com/prettier/prettier",
    examples_url="https://prettier.io/playground/",
    installation_guide="npm install --save-dev prettier",
    common_patterns=[
        "Configuration: .prettierrc",
        "Ignore files: .prettierignore",
        "IDE integration",
        "Pre-commit formatting",
        "ESLint integration",
        "Format on save",
        "CI/CD checks",
        "Multiple file formats",
        "Custom parsers",
        "Team consistency"
    ],
    known_issues=[
        "Opinionado demais para alguns",
        "Conflitos com ESLint",
        "Limitadas opções de configuração",
        "Pode quebrar alguns edge cases",
        "Performance em arquivos grandes"
    ],
    alternatives=["ESLint --fix", "StandardJS", "Biome", "dprint"]
)

# Common Issues & Fixes - Problemas comuns
common_fixes_source = SeedSource(
    name="Common Development Issues",
    category=SeedCategory.PATTERNS_FIXES,
    url="https://github.com/topics/common-issues",
    description="Coleção de problemas comuns em desenvolvimento web e suas soluções.",
    license="Various",
    priority=2,
    tags=["troubleshooting", "debugging", "common-issues", "solutions", "fixes"],
    documentation_url="https://stackoverflow.com/questions/tagged/common-issues",
    github_url="https://github.com/topics/debugging",
    examples_url="https://developer.mozilla.org/en-US/docs/Web/Guide",
    installation_guide="Consulte documentações específicas para cada problema",
    common_patterns=[
        "Hydration mismatch em SSR",
        "CORS issues em APIs",
        "Memory leaks em React",
        "Bundle size optimization",
        "Performance bottlenecks",
        "Authentication edge cases",
        "Database connection issues",
        "Deployment problems",
        "Environment variables",
        "TypeScript configuration"
    ],
    known_issues=[
        "Soluções podem ser específicas",
        "Versões diferentes têm problemas diferentes",
        "Nem sempre há solução única",
        "Debugging pode ser complexo",
        "Documentação fragmentada"
    ],
    alternatives=["Stack Overflow", "GitHub Issues", "Official Docs", "Community Forums"]
)

# Tailwind + SSR - Problema específico
tailwind_ssr_source = SeedSource(
    name="Tailwind CSS + SSR Issues",
    category=SeedCategory.PATTERNS_FIXES,
    url="https://nextjs.org/docs/messages/tailwind-ssr",
    description="Soluções para problemas comuns de Tailwind CSS com Server-Side Rendering.",
    license="MIT",
    priority=2,
    tags=["tailwind", "ssr", "nextjs", "hydration", "css", "fixes"],
    documentation_url="https://tailwindcss.com/docs/guides/nextjs",
    github_url="https://github.com/tailwindlabs/tailwindcss/discussions",
    examples_url="https://nextjs.org/docs/basic-features/built-in-css-support",
    installation_guide="Siga a documentação oficial do Next.js + Tailwind",
    common_patterns=[
        "Configuração correta do PostCSS",
        "Import order no globals.css",
        "Purge configuration",
        "JIT mode setup",
        "Dark mode com SSR",
        "Custom CSS variables",
        "Component-level styles",
        "Build optimization",
        "Development vs Production",
        "Hydration consistency"
    ],
    known_issues=[
        "Flash of unstyled content (FOUC)",
        "Hydration mismatches",
        "Build time issues",
        "CSS order problems",
        "Dark mode flickering",
        "Purge removing needed styles"
    ],
    alternatives=["CSS Modules", "Styled Components", "Emotion", "Vanilla CSS"]
)

# Lista de todas as fontes de padrões e fixes
patterns_sources = [
    owasp_source,
    jest_source,
    playwright_source,
    eslint_source,
    prettier_source,
    common_fixes_source,
    tailwind_ssr_source
]

# Registra todas as fontes no seed_manager
for source in patterns_sources:
    seed_manager.add_source(source)

# Classes para exportação
class OWASPSource:
    """Classe de conveniência para OWASP"""
    
    @staticmethod
    def get_top_10_2021() -> list:
        return [
            "A01:2021 – Broken Access Control",
            "A02:2021 – Cryptographic Failures",
            "A03:2021 – Injection",
            "A04:2021 – Insecure Design",
            "A05:2021 – Security Misconfiguration",
            "A06:2021 – Vulnerable and Outdated Components",
            "A07:2021 – Identification and Authentication Failures",
            "A08:2021 – Software and Data Integrity Failures",
            "A09:2021 – Security Logging and Monitoring Failures",
            "A10:2021 – Server-Side Request Forgery"
        ]
    
    @staticmethod
    def get_essential_cheat_sheets() -> list:
        return [
            "Input Validation",
            "Authentication",
            "Session Management",
            "Cross Site Scripting Prevention",
            "SQL Injection Prevention",
            "Cross-Site Request Forgery Prevention",
            "Secure Headers",
            "REST Security",
            "JSON Web Token Security",
            "Content Security Policy"
        ]

class TestingSource:
    """Classe de conveniência para Testing"""
    
    @staticmethod
    def get_testing_pyramid() -> dict:
        return {
            "Unit Tests": "Base da pirâmide - testes rápidos e isolados",
            "Integration Tests": "Meio da pirâmide - testes de integração",
            "E2E Tests": "Topo da pirâmide - testes end-to-end"
        }
    
    @staticmethod
    def get_jest_config_example() -> str:
        return '''module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
  ],
};'''
    
    @staticmethod
    def get_playwright_config_example() -> str:
        return '''import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
});'''

class CommonFixesSource:
    """Classe de conveniência para Common Fixes"""
    
    @staticmethod
    def get_nextjs_common_issues() -> dict:
        return {
            "Hydration Mismatch": "Diferenças entre server e client rendering",
            "Image Optimization": "Configuração incorreta do next/image",
            "API Routes CORS": "Problemas de CORS em API routes",
            "Environment Variables": "Variáveis não carregando corretamente",
            "Build Errors": "Erros durante o processo de build",
            "Performance Issues": "Problemas de performance e bundle size"
        }
    
    @staticmethod
    def get_react_common_issues() -> dict:
        return {
            "Memory Leaks": "useEffect sem cleanup",
            "Infinite Loops": "Dependencies incorretas em hooks",
            "State Updates": "Atualizações de state após unmount",
            "Key Props": "Keys duplicadas ou ausentes em listas",
            "Event Handlers": "Event listeners não removidos",
            "Prop Drilling": "Passagem excessiva de props"
        }
    
    @staticmethod
    def get_typescript_common_issues() -> dict:
        return {
            "Type Errors": "Erros de tipagem comuns",
            "Any Usage": "Uso excessivo do tipo any",
            "Module Resolution": "Problemas de resolução de módulos",
            "Declaration Files": "Arquivos .d.ts incorretos",
            "Generic Constraints": "Constraints de generics",
            "Utility Types": "Uso incorreto de utility types"
        }

class CodeQualitySource:
    """Classe de conveniência para Code Quality"""
    
    @staticmethod
    def get_eslint_nextjs_config() -> str:
        return '''{
  "extends": [
    "next/core-web-vitals",
    "@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn",
    "prefer-const": "error",
    "no-console": "warn"
  }
}'''
    
    @staticmethod
    def get_prettier_config() -> str:
        return '''{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}'''
    
    @staticmethod
    def get_husky_setup() -> list:
        return [
            "npm install --save-dev husky",
            "npx husky install",
            "npx husky add .husky/pre-commit \"npm run lint\"",
            "npx husky add .husky/pre-commit \"npm run format\"",
            "Add to package.json: \"prepare\": \"husky install\""
        ]