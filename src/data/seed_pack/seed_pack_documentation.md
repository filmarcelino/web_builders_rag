# Seed Pack - Fontes Prioritárias
Gerado em: 2025-08-23 15:35:30
Total de fontes: 32

## Ui Design

### shadcn/ui

**Prioridade:** 1

**Descrição:** Sistema de design moderno e acessível baseado em Radix UI e Tailwind CSS. Componentes copiáveis e customizáveis.

**URL:** [https://ui.shadcn.com](https://ui.shadcn.com)

**Licença:** MIT

**Tags:** ui, design-system, react, tailwind, radix, accessibility, typescript

**Documentação:** [https://ui.shadcn.com/docs](https://ui.shadcn.com/docs)

**GitHub:** [https://github.com/shadcn-ui/ui](https://github.com/shadcn-ui/ui)

**Instalação:** npx shadcn-ui@latest init

**Padrões Comuns:**
- Instalação: npx shadcn-ui@latest init
- Adicionar componente: npx shadcn-ui@latest add button
- Customização via CSS variables no globals.css
- Uso com Next.js App Router
- Integração com Tailwind CSS
- Componentes acessíveis por padrão
- Suporte a dark mode nativo
- Estrutura de pastas: components/ui/

**Problemas Conhecidos:**
- Requer configuração inicial do Tailwind CSS
- Alguns componentes podem precisar de ajustes para SSR
- Dependência do Radix UI pode causar conflitos de versão
- Customização avançada requer conhecimento de CSS variables

---

### Radix UI

**Prioridade:** 1

**Descrição:** Primitivos de UI de baixo nível e acessíveis para React. Base do Shadcn/UI.

**URL:** [https://radix-ui.com](https://radix-ui.com)

**Licença:** MIT

**Tags:** ui, primitives, accessibility, react, headless, typescript

**Documentação:** [https://radix-ui.com/docs](https://radix-ui.com/docs)

**GitHub:** [https://github.com/radix-ui/primitives](https://github.com/radix-ui/primitives)

**Instalação:** npm install @radix-ui/react-*

**Padrões Comuns:**
- Componentes headless (sem estilo)
- Acessibilidade WAI-ARIA completa
- Suporte a keyboard navigation
- Composição de componentes
- Controle total sobre styling
- SSR-friendly
- TypeScript nativo
- Uso com CSS-in-JS ou Tailwind

**Problemas Conhecidos:**
- Requer styling manual
- Curva de aprendizado para composição
- Alguns componentes são complexos de configurar
- Documentação pode ser verbosa

---

### Awesome shadcn/ui

**Prioridade:** 2

**Descrição:** Lista curada de recursos, templates, exemplos e complementos para shadcn/ui.

**URL:** [https://github.com/birobirobiro/awesome-shadcn-ui](https://github.com/birobirobiro/awesome-shadcn-ui)

**Licença:** MIT

**Tags:** curadoria, templates, exemplos, shadcn, community, resources

**Documentação:** [https://github.com/birobirobiro/awesome-shadcn-ui/blob/main/README.md](https://github.com/birobirobiro/awesome-shadcn-ui/blob/main/README.md)

**GitHub:** [https://github.com/birobirobiro/awesome-shadcn-ui](https://github.com/birobirobiro/awesome-shadcn-ui)

**Instalação:** Navegue pelos recursos listados no repositório

**Padrões Comuns:**
- Templates completos de aplicações
- Componentes adicionais da comunidade
- Exemplos de integração
- Themes e variações de design
- Boilerplates específicos
- Plugins e extensões
- Showcases de projetos
- Recursos de aprendizado

**Problemas Conhecidos:**
- Qualidade varia entre recursos
- Nem todos os recursos são mantidos
- Pode conter dependências desatualizadas
- Documentação inconsistente entre projetos

---

### Headless UI

**Prioridade:** 2

**Descrição:** Componentes UI completamente sem estilo e totalmente acessíveis, feitos pela equipe do Tailwind CSS.

**URL:** [https://headlessui.com](https://headlessui.com)

**Licença:** MIT

**Tags:** ui, headless, accessibility, tailwind, react, vue, typescript

**Documentação:** [https://headlessui.com/react](https://headlessui.com/react)

**GitHub:** [https://github.com/tailwindlabs/headlessui](https://github.com/tailwindlabs/headlessui)

**Instalação:** npm install @headlessui/react

**Padrões Comuns:**
- Componentes totalmente acessíveis
- Integração perfeita com Tailwind
- Suporte React e Vue
- TypeScript first
- Keyboard navigation
- Focus management
- ARIA attributes automáticos
- Composição flexível

**Problemas Conhecidos:**
- Limitado conjunto de componentes
- Requer styling manual completo
- Menos componentes que Radix UI
- Documentação pode ser básica

---

### Tailwind UI

**Prioridade:** 3

**Descrição:** Componentes e templates profissionais feitos pela equipe do Tailwind CSS.

**URL:** [https://tailwindui.com](https://tailwindui.com)

**Licença:** Comercial

**Tags:** ui, tailwind, premium, templates, components, professional

**Documentação:** [https://tailwindui.com/documentation](https://tailwindui.com/documentation)

**GitHub:** [https://github.com/tailwindlabs/tailwindui](https://github.com/tailwindlabs/tailwindui)

**Instalação:** Requer licença paga - acesso via tailwindui.com

**Padrões Comuns:**
- Componentes copy-paste
- Templates de páginas completas
- Responsive design
- Dark mode support
- Múltiplas variações
- Código HTML + React + Vue
- Figma design files
- Regular updates

**Problemas Conhecidos:**
- Requer licença paga
- Não é um package npm
- Customização manual necessária
- Pode ser overkill para projetos simples

---

## Web Stack

### Next.js

**Prioridade:** 1

**Descrição:** Framework React para produção com App Router, SSR, SSG, API Routes e otimizações automáticas.

**URL:** [https://nextjs.org](https://nextjs.org)

**Licença:** MIT

**Tags:** react, framework, ssr, ssg, app-router, typescript, vercel

**Documentação:** [https://nextjs.org/docs](https://nextjs.org/docs)

**GitHub:** [https://github.com/vercel/next.js](https://github.com/vercel/next.js)

**Instalação:** npx create-next-app@latest

**Padrões Comuns:**
- App Router (Next.js 13+): app/ directory
- Server Components por padrão
- Client Components com 'use client'
- API Routes: app/api/route.ts
- Layouts aninhados: layout.tsx
- Loading UI: loading.tsx
- Error Boundaries: error.tsx
- Metadata API para SEO
- Image optimization com next/image
- Font optimization com next/font

**Problemas Conhecidos:**
- App Router ainda em evolução
- Hydration mismatch em SSR
- Bundle size pode crescer rapidamente
- Configuração complexa para casos avançados
- Debugging pode ser desafiador

---

### Tailwind CSS

**Prioridade:** 1

**Descrição:** Framework CSS utilitário para criação rápida de interfaces customizadas.

**URL:** [https://tailwindcss.com](https://tailwindcss.com)

**Licença:** MIT

**Tags:** css, utility-first, responsive, dark-mode, jit, purge

**Documentação:** [https://tailwindcss.com/docs](https://tailwindcss.com/docs)

**GitHub:** [https://github.com/tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss)

**Instalação:** npm install -D tailwindcss postcss autoprefixer

**Padrões Comuns:**
- Utility-first approach
- Responsive design: sm:, md:, lg:, xl:, 2xl:
- Dark mode: dark: prefix
- Hover states: hover: prefix
- Focus states: focus: prefix
- Custom colors via CSS variables
- Component extraction com @apply
- JIT compilation para performance
- Purging unused CSS
- Plugin system para extensões

**Problemas Conhecidos:**
- HTML pode ficar verboso
- Curva de aprendizado inicial
- Configuração de purge crítica
- Debugging de classes pode ser difícil
- Conflitos com CSS existente

---

### NextAuth.js

**Prioridade:** 1

**Descrição:** Solução completa de autenticação para Next.js com suporte a múltiplos providers.

**URL:** [https://next-auth.js.org](https://next-auth.js.org)

**Licença:** ISC

**Tags:** auth, authentication, oauth, jwt, session, nextjs

**Documentação:** [https://next-auth.js.org/getting-started/introduction](https://next-auth.js.org/getting-started/introduction)

**GitHub:** [https://github.com/nextauthjs/next-auth](https://github.com/nextauthjs/next-auth)

**Instalação:** npm install next-auth

**Padrões Comuns:**
- API Route: app/api/auth/[...nextauth]/route.ts
- Providers: Google, GitHub, Discord, etc.
- Database adapters: Prisma, MongoDB, etc.
- JWT ou Database sessions
- Middleware para proteção de rotas
- useSession hook no client
- getServerSession no server
- Callbacks para customização
- CSRF protection automático
- TypeScript support

**Problemas Conhecidos:**
- Configuração inicial complexa
- Documentação pode ser confusa
- Debugging de providers OAuth
- Session management edge cases
- Migração entre versões

---

### Prisma

**Prioridade:** 1

**Descrição:** ORM moderno e type-safe para Node.js e TypeScript com geração automática de cliente.

**URL:** [https://prisma.io](https://prisma.io)

**Licença:** Apache 2.0

**Tags:** orm, database, typescript, postgresql, mysql, sqlite, mongodb

**Documentação:** [https://prisma.io/docs](https://prisma.io/docs)

**GitHub:** [https://github.com/prisma/prisma](https://github.com/prisma/prisma)

**Instalação:** npm install prisma @prisma/client

**Padrões Comuns:**
- Schema definition: schema.prisma
- Database migrations: prisma migrate
- Client generation: prisma generate
- Type-safe queries
- Relation queries
- Transaction support
- Connection pooling
- Prisma Studio para GUI
- Seed scripts
- Multiple database support

**Problemas Conhecidos:**
- Bundle size pode ser grande
- Cold start latency
- Limitações em edge runtime
- Migrations podem ser complexas
- Performance em queries complexas

---

### UploadThing

**Prioridade:** 2

**Descrição:** Solução simples e type-safe para upload de arquivos em aplicações Next.js.

**URL:** [https://uploadthing.com](https://uploadthing.com)

**Licença:** MIT

**Tags:** upload, files, nextjs, typescript, s3, cdn

**Documentação:** [https://docs.uploadthing.com](https://docs.uploadthing.com)

**GitHub:** [https://github.com/pingdotgg/uploadthing](https://github.com/pingdotgg/uploadthing)

**Instalação:** npm install uploadthing @uploadthing/react

**Padrões Comuns:**
- File router definition
- Type-safe upload endpoints
- React hooks: useUploadThing
- Progress tracking
- File validation
- Image optimization
- CDN delivery
- Webhook support
- Multiple file types
- Drag and drop UI

**Problemas Conhecidos:**
- Requer conta UploadThing
- Limitações no plano gratuito
- Dependência de serviço externo
- Customização limitada
- Pricing pode escalar

---

### PapaParse

**Prioridade:** 2

**Descrição:** Parser CSV rápido e poderoso para JavaScript no browser e Node.js.

**URL:** [https://papaparse.com](https://papaparse.com)

**Licença:** MIT

**Tags:** csv, parser, javascript, browser, nodejs, streaming

**Documentação:** [https://papaparse.com/docs](https://papaparse.com/docs)

**GitHub:** [https://github.com/mholt/PapaParse](https://github.com/mholt/PapaParse)

**Instalação:** npm install papaparse

**Padrões Comuns:**
- Parse CSV strings: Papa.parse(csv)
- Parse files: Papa.parse(file)
- Streaming large files
- Header detection automática
- Type conversion
- Error handling
- Progress callbacks
- Worker threads
- Custom delimiters
- JSON output

**Problemas Conhecidos:**
- Memory usage com arquivos grandes
- Performance em datasets enormes
- Encoding issues
- Browser compatibility edge cases
- Type inference limitada

---

### tus.io

**Prioridade:** 3

**Descrição:** Protocolo aberto para upload de arquivos resiliente e resumível.

**URL:** [https://tus.io](https://tus.io)

**Licença:** MIT

**Tags:** upload, resumable, protocol, open-standard, resilient

**Documentação:** [https://tus.io/protocols/resumable-upload.html](https://tus.io/protocols/resumable-upload.html)

**GitHub:** [https://github.com/tus](https://github.com/tus)

**Instalação:** npm install tus-js-client

**Padrões Comuns:**
- Resumable uploads
- Chunk-based transfer
- Progress tracking
- Error recovery
- Cross-platform support
- Server implementations
- Client libraries
- HTTP-based protocol
- Metadata support
- Hooks and events

**Problemas Conhecidos:**
- Requer implementação server-side
- Complexidade de setup
- Não é plug-and-play
- Debugging pode ser difícil
- Configuração de CORS

---

### csv-parse

**Prioridade:** 3

**Descrição:** Parser CSV para Node.js com suporte a streaming e transformações.

**URL:** [https://csv.js.org/parse/](https://csv.js.org/parse/)

**Licença:** MIT

**Tags:** csv, nodejs, streaming, transform, parser

**Documentação:** [https://csv.js.org/parse/api/](https://csv.js.org/parse/api/)

**GitHub:** [https://github.com/adaltas/node-csv](https://github.com/adaltas/node-csv)

**Instalação:** npm install csv-parse

**Padrões Comuns:**
- Stream processing
- Transform functions
- Column mapping
- Type casting
- Error handling
- Async iteration
- Pipe operations
- Memory efficient
- Custom options
- Validation hooks

**Problemas Conhecidos:**
- Node.js específico
- Curva de aprendizado para streams
- Configuração complexa
- Debugging de transforms
- Error propagation

---

## Recurring Modules

### Stripe

**Prioridade:** 1

**Descrição:** Plataforma completa de pagamentos com APIs poderosas e SDKs para desenvolvimento.

**URL:** [https://stripe.com](https://stripe.com)

**Licença:** Comercial (SDK MIT)

**Tags:** payments, stripe, checkout, subscriptions, webhooks, api

**Documentação:** [https://stripe.com/docs](https://stripe.com/docs)

**GitHub:** [https://github.com/stripe/stripe-node](https://github.com/stripe/stripe-node)

**Instalação:** npm install stripe @stripe/stripe-js

**Padrões Comuns:**
- Payment Intents para pagamentos únicos
- Subscription API para assinaturas
- Checkout Sessions para UI pré-construída
- Webhooks para eventos em tempo real
- Customer Portal para autoatendimento
- Connect para marketplaces
- Elements para UI customizada
- Test mode com cartões de teste
- Metadata para dados customizados
- Idempotency keys para segurança

**Problemas Conhecidos:**
- Requer conta Stripe e configuração
- Webhooks precisam de HTTPS
- Taxas de transação aplicáveis
- Compliance PCI DSS necessário
- Debugging de webhooks complexo
- Rate limiting em APIs

---

### Zod

**Prioridade:** 1

**Descrição:** Biblioteca de validação de schema TypeScript-first com inferência de tipos estática.

**URL:** [https://zod.dev](https://zod.dev)

**Licença:** MIT

**Tags:** validation, typescript, schema, type-safe, runtime, parsing

**Documentação:** [https://zod.dev/README](https://zod.dev/README)

**GitHub:** [https://github.com/colinhacks/zod](https://github.com/colinhacks/zod)

**Instalação:** npm install zod

**Padrões Comuns:**
- Schema definition: z.object({})
- Type inference: z.infer<typeof schema>
- Runtime validation: schema.parse(data)
- Safe parsing: schema.safeParse(data)
- Transform data: schema.transform()
- Refinements: schema.refine()
- Optional fields: z.string().optional()
- Arrays: z.array(z.string())
- Unions: z.union([z.string(), z.number()])
- Custom error messages

**Problemas Conhecidos:**
- Bundle size pode crescer
- Error messages podem ser verbosas
- Performance em schemas complexos
- Curva de aprendizado inicial
- Debugging de schemas aninhados

---

### React Hook Form

**Prioridade:** 1

**Descrição:** Biblioteca performática e flexível para formulários React com validação mínima de re-renders.

**URL:** [https://react-hook-form.com](https://react-hook-form.com)

**Licença:** MIT

**Tags:** forms, react, validation, performance, typescript, hooks

**Documentação:** [https://react-hook-form.com/get-started](https://react-hook-form.com/get-started)

**GitHub:** [https://github.com/react-hook-form/react-hook-form](https://github.com/react-hook-form/react-hook-form)

**Instalação:** npm install react-hook-form

**Padrões Comuns:**
- useForm hook: const { register, handleSubmit } = useForm()
- Register inputs: {...register('name')}
- Form submission: handleSubmit(onSubmit)
- Validation com resolver (Zod, Yup)
- Watch values: watch('fieldName')
- Set values: setValue('name', value)
- Error handling: formState.errors
- Field arrays: useFieldArray
- Controller para componentes customizados
- Reset form: reset()

**Problemas Conhecidos:**
- Curva de aprendizado para casos complexos
- Debugging pode ser desafiador
- Integração com UI libraries
- TypeScript setup complexo
- Documentação pode ser confusa

---

### TanStack Query

**Prioridade:** 2

**Descrição:** Biblioteca poderosa para data fetching, caching, sincronização e atualizações de servidor.

**URL:** [https://tanstack.com/query](https://tanstack.com/query)

**Licença:** MIT

**Tags:** data-fetching, caching, react, server-state, mutations, typescript

**Documentação:** [https://tanstack.com/query/latest](https://tanstack.com/query/latest)

**GitHub:** [https://github.com/TanStack/query](https://github.com/TanStack/query)

**Instalação:** npm install @tanstack/react-query

**Padrões Comuns:**
- useQuery para data fetching
- useMutation para modificações
- Query keys para cache management
- Stale time e cache time
- Background refetching
- Optimistic updates
- Infinite queries
- Query invalidation
- Error boundaries
- DevTools para debugging

**Problemas Conhecidos:**
- Configuração inicial complexa
- Cache management pode ser confuso
- Bundle size considerável
- Debugging de cache states
- Performance com muitas queries

---

### Zustand

**Prioridade:** 2

**Descrição:** Solução pequena, rápida e escalável de gerenciamento de estado para React.

**URL:** [https://zustand-demo.pmnd.rs](https://zustand-demo.pmnd.rs)

**Licença:** MIT

**Tags:** state-management, react, typescript, simple, lightweight

**Documentação:** [https://github.com/pmndrs/zustand](https://github.com/pmndrs/zustand)

**GitHub:** [https://github.com/pmndrs/zustand](https://github.com/pmndrs/zustand)

**Instalação:** npm install zustand

**Padrões Comuns:**
- Create store: create((set) => ({}))
- Use store: const state = useStore()
- Update state: set((state) => ({}))
- Async actions
- Subscriptions
- Persist middleware
- Immer middleware
- DevTools integration
- TypeScript support
- Vanilla JS usage

**Problemas Conhecidos:**
- Menos ecosystem que Redux
- DevTools limitados
- Documentação pode ser básica
- Patterns não estabelecidos
- Time travel debugging limitado

---

### date-fns

**Prioridade:** 2

**Descrição:** Biblioteca moderna de utilitários para datas em JavaScript com suporte a tree-shaking.

**URL:** [https://date-fns.org](https://date-fns.org)

**Licença:** MIT

**Tags:** dates, time, utilities, tree-shaking, immutable, typescript

**Documentação:** [https://date-fns.org/docs/Getting-Started](https://date-fns.org/docs/Getting-Started)

**GitHub:** [https://github.com/date-fns/date-fns](https://github.com/date-fns/date-fns)

**Instalação:** npm install date-fns

**Padrões Comuns:**
- Import específico: import { format } from 'date-fns'
- Format dates: format(date, 'yyyy-MM-dd')
- Parse dates: parse(dateString, format, new Date())
- Add/subtract: addDays(date, 7)
- Compare dates: isAfter(date1, date2)
- Locale support: import { ptBR } from 'date-fns/locale'
- Time zones: date-fns-tz
- Immutable operations
- Tree-shaking friendly
- TypeScript definitions

**Problemas Conhecidos:**
- Bundle size sem tree-shaking
- Time zone handling complexo
- Locale imports manuais
- API pode ser verbosa
- Migração de moment.js

---

## Boilerplates

### Vercel Examples

**Prioridade:** 1

**Descrição:** Coleção oficial de exemplos e templates para Next.js e outras tecnologias web modernas.

**URL:** [https://github.com/vercel/examples](https://github.com/vercel/examples)

**Licença:** MIT

**Tags:** nextjs, examples, templates, vercel, official, showcase

**Documentação:** [https://github.com/vercel/examples/blob/main/README.md](https://github.com/vercel/examples/blob/main/README.md)

**GitHub:** [https://github.com/vercel/examples](https://github.com/vercel/examples)

**Instalação:** npx create-next-app --example [example-name]

**Padrões Comuns:**
- Next.js App Router examples
- API Routes patterns
- Database integrations
- Authentication examples
- E-commerce templates
- CMS integrations
- Edge functions
- Middleware examples
- Deployment configurations
- Performance optimizations

**Problemas Conhecidos:**
- Qualidade varia entre exemplos
- Alguns podem estar desatualizados
- Documentação limitada em alguns
- Dependências podem ter vulnerabilidades
- Nem todos seguem best practices

---

### T3 Stack (Create T3 App)

**Prioridade:** 1

**Descrição:** Stack opinionado e type-safe para Next.js com Prisma, tRPC, NextAuth.js e Tailwind CSS.

**URL:** [https://create.t3.gg](https://create.t3.gg)

**Licença:** MIT

**Tags:** nextjs, typescript, prisma, trpc, nextauth, tailwind, type-safe

**Documentação:** [https://create.t3.gg/en/introduction](https://create.t3.gg/en/introduction)

**GitHub:** [https://github.com/t3-oss/create-t3-app](https://github.com/t3-oss/create-t3-app)

**Instalação:** npm create t3-app@latest

**Padrões Comuns:**
- Type-safe API com tRPC
- Database com Prisma ORM
- Autenticação com NextAuth.js
- Styling com Tailwind CSS
- Folder structure opinionada
- TypeScript configurado
- ESLint e Prettier
- Environment variables
- Deployment ready
- Best practices enforced

**Problemas Conhecidos:**
- Opinionado demais para alguns casos
- Curva de aprendizado para tRPC
- Bundle size pode ser grande
- Configuração complexa para customizar
- Dependências específicas

---

### Shadcn/UI Templates

**Prioridade:** 1

**Descrição:** Templates e exemplos oficiais usando shadcn/ui para diferentes tipos de aplicações.

**URL:** [https://ui.shadcn.com/examples](https://ui.shadcn.com/examples)

**Licença:** MIT

**Tags:** shadcn, templates, ui, examples, dashboard, forms

**Documentação:** [https://ui.shadcn.com/docs](https://ui.shadcn.com/docs)

**GitHub:** [https://github.com/shadcn-ui/ui](https://github.com/shadcn-ui/ui)

**Instalação:** npx create-next-app -e https://github.com/shadcn-ui/next-template

**Padrões Comuns:**
- Dashboard layouts
- Authentication forms
- Data tables
- Card layouts
- Navigation patterns
- Form examples
- Chart integrations
- Modal patterns
- Responsive designs
- Dark mode support

**Problemas Conhecidos:**
- Templates limitados
- Requer configuração manual
- Nem todos são completos
- Documentação básica
- Customização necessária

---

### Refine

**Prioridade:** 2

**Descrição:** Framework React para construir rapidamente admin panels, dashboards e aplicações CRUD.

**URL:** [https://refine.dev](https://refine.dev)

**Licença:** MIT

**Tags:** admin, dashboard, crud, react, framework, data-provider

**Documentação:** [https://refine.dev/docs](https://refine.dev/docs)

**GitHub:** [https://github.com/refinedev/refine](https://github.com/refinedev/refine)

**Instalação:** npm create refine-app@latest

**Padrões Comuns:**
- Data providers para APIs
- Auth providers
- UI framework agnostic
- CRUD operations automáticas
- Routing integrado
- Form handling
- Table components
- Real-time updates
- Multi-tenancy support
- Internationalization

**Problemas Conhecidos:**
- Específico para admin interfaces
- Curva de aprendizado
- Documentação pode ser confusa
- Customização limitada em alguns casos
- Bundle size considerável

---

### Next.js Commerce

**Prioridade:** 2

**Descrição:** Template de e-commerce de alta performance construído com Next.js e Vercel.

**URL:** [https://nextjs.org/commerce](https://nextjs.org/commerce)

**Licença:** MIT

**Tags:** ecommerce, nextjs, commerce, shopify, bigcommerce, template

**Documentação:** [https://github.com/vercel/commerce/blob/main/README.md](https://github.com/vercel/commerce/blob/main/README.md)

**GitHub:** [https://github.com/vercel/commerce](https://github.com/vercel/commerce)

**Instalação:** npx create-next-app --example commerce

**Padrões Comuns:**
- Product catalog
- Shopping cart
- Checkout flow
- User authentication
- Payment integration
- Inventory management
- SEO optimization
- Performance optimization
- Mobile responsive
- Analytics integration

**Problemas Conhecidos:**
- Complexo para customizar
- Dependências específicas
- Requer backend commerce
- Configuração inicial complexa
- Bundle size grande

---

### Taxonomy

**Prioridade:** 2

**Descrição:** Aplicação moderna construída com Next.js 13, Prisma, PlanetScale, Auth.js e shadcn/ui.

**URL:** [https://tx.shadcn.com](https://tx.shadcn.com)

**Licença:** MIT

**Tags:** nextjs, prisma, planetscale, authjs, shadcn, modern, app-router

**Documentação:** [https://github.com/shadcn-ui/taxonomy/blob/main/README.md](https://github.com/shadcn-ui/taxonomy/blob/main/README.md)

**GitHub:** [https://github.com/shadcn-ui/taxonomy](https://github.com/shadcn-ui/taxonomy)

**Instalação:** git clone https://github.com/shadcn-ui/taxonomy.git

**Padrões Comuns:**
- Next.js 13 App Router
- Server Components
- Database com Prisma
- Authentication com Auth.js
- UI com shadcn/ui
- Styling com Tailwind
- TypeScript setup
- Subscription billing
- MDX content
- SEO optimization

**Problemas Conhecidos:**
- Exemplo específico
- Requer configuração manual
- Dependências podem desatualizar
- Não é um template genérico
- Complexo para iniciantes

---

## Patterns Fixes

### OWASP Cheat Sheets

**Prioridade:** 1

**Descrição:** Série de cheat sheets sobre segurança web com práticas recomendadas e padrões seguros.

**URL:** [https://cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org)

**Licença:** Creative Commons

**Tags:** security, owasp, web-security, best-practices, cheat-sheets

**Documentação:** [https://cheatsheetseries.owasp.org/index.html](https://cheatsheetseries.owasp.org/index.html)

**GitHub:** [https://github.com/OWASP/CheatSheetSeries](https://github.com/OWASP/CheatSheetSeries)

**Instalação:** Consulte os cheat sheets online ou clone o repositório

**Padrões Comuns:**
- Input Validation patterns
- Authentication best practices
- Session Management
- Cross-Site Scripting (XSS) prevention
- SQL Injection prevention
- CSRF protection
- Secure Headers configuration
- Password Storage guidelines
- API Security patterns
- Content Security Policy (CSP)

**Problemas Conhecidos:**
- Pode ser overwhelming para iniciantes
- Nem todos os padrões são aplicáveis
- Requer conhecimento de segurança
- Implementação pode ser complexa
- Atualizações constantes necessárias

---

### Jest

**Prioridade:** 1

**Descrição:** Framework de testing JavaScript com foco em simplicidade e suporte nativo para React.

**URL:** [https://jestjs.io](https://jestjs.io)

**Licença:** MIT

**Tags:** testing, javascript, react, unit-tests, mocking, coverage

**Documentação:** [https://jestjs.io/docs/getting-started](https://jestjs.io/docs/getting-started)

**GitHub:** [https://github.com/facebook/jest](https://github.com/facebook/jest)

**Instalação:** npm install --save-dev jest

**Padrões Comuns:**
- Unit testing: test() ou it()
- Test suites: describe()
- Mocking: jest.mock()
- Async testing: async/await
- Snapshot testing
- Coverage reports
- Setup/teardown: beforeEach, afterEach
- Custom matchers
- Testing React components
- Integration with CI/CD

**Problemas Conhecidos:**
- Configuração pode ser complexa
- Performance em projetos grandes
- Mocking pode ser confuso
- Debugging de testes
- Snapshot tests podem ser frágeis

---

### Playwright

**Prioridade:** 1

**Descrição:** Framework moderno para automação e testing end-to-end de aplicações web.

**URL:** [https://playwright.dev](https://playwright.dev)

**Licença:** Apache 2.0

**Tags:** e2e-testing, automation, browser-testing, playwright, cross-browser

**Documentação:** [https://playwright.dev/docs/intro](https://playwright.dev/docs/intro)

**GitHub:** [https://github.com/microsoft/playwright](https://github.com/microsoft/playwright)

**Instalação:** npm init playwright@latest

**Padrões Comuns:**
- Page Object Model
- Auto-waiting for elements
- Cross-browser testing
- Mobile testing
- API testing
- Visual comparisons
- Network interception
- Parallel execution
- Test generation
- CI/CD integration

**Problemas Conhecidos:**
- Curva de aprendizado
- Configuração inicial complexa
- Debugging pode ser difícil
- Flaky tests em alguns casos
- Resource intensive

---

### ESLint

**Prioridade:** 1

**Descrição:** Ferramenta de linting para identificar e corrigir problemas em código JavaScript/TypeScript.

**URL:** [https://eslint.org](https://eslint.org)

**Licença:** MIT

**Tags:** linting, code-quality, javascript, typescript, static-analysis

**Documentação:** [https://eslint.org/docs/latest/](https://eslint.org/docs/latest/)

**GitHub:** [https://github.com/eslint/eslint](https://github.com/eslint/eslint)

**Instalação:** npm install eslint --save-dev

**Padrões Comuns:**
- Configuration files: .eslintrc.js
- Rule configuration
- Extends popular configs
- Custom rules
- Ignore patterns: .eslintignore
- IDE integration
- Pre-commit hooks
- Auto-fixing: --fix
- TypeScript support
- React/Next.js configs

**Problemas Conhecidos:**
- Configuração pode ser overwhelming
- Conflitos entre rules
- Performance em projetos grandes
- False positives
- Migração entre versões

---

### Prettier

**Prioridade:** 1

**Descrição:** Formatador de código opinativo que garante estilo consistente em projetos.

**URL:** [https://prettier.io](https://prettier.io)

**Licença:** MIT

**Tags:** formatting, code-style, javascript, typescript, consistency

**Documentação:** [https://prettier.io/docs/en/](https://prettier.io/docs/en/)

**GitHub:** [https://github.com/prettier/prettier](https://github.com/prettier/prettier)

**Instalação:** npm install --save-dev prettier

**Padrões Comuns:**
- Configuration: .prettierrc
- Ignore files: .prettierignore
- IDE integration
- Pre-commit formatting
- ESLint integration
- Format on save
- CI/CD checks
- Multiple file formats
- Custom parsers
- Team consistency

**Problemas Conhecidos:**
- Opinionado demais para alguns
- Conflitos com ESLint
- Limitadas opções de configuração
- Pode quebrar alguns edge cases
- Performance em arquivos grandes

---

### Common Development Issues

**Prioridade:** 2

**Descrição:** Coleção de problemas comuns em desenvolvimento web e suas soluções.

**URL:** [https://github.com/topics/common-issues](https://github.com/topics/common-issues)

**Licença:** Various

**Tags:** troubleshooting, debugging, common-issues, solutions, fixes

**Documentação:** [https://stackoverflow.com/questions/tagged/common-issues](https://stackoverflow.com/questions/tagged/common-issues)

**GitHub:** [https://github.com/topics/debugging](https://github.com/topics/debugging)

**Instalação:** Consulte documentações específicas para cada problema

**Padrões Comuns:**
- Hydration mismatch em SSR
- CORS issues em APIs
- Memory leaks em React
- Bundle size optimization
- Performance bottlenecks
- Authentication edge cases
- Database connection issues
- Deployment problems
- Environment variables
- TypeScript configuration

**Problemas Conhecidos:**
- Soluções podem ser específicas
- Versões diferentes têm problemas diferentes
- Nem sempre há solução única
- Debugging pode ser complexo
- Documentação fragmentada

---

### Tailwind CSS + SSR Issues

**Prioridade:** 2

**Descrição:** Soluções para problemas comuns de Tailwind CSS com Server-Side Rendering.

**URL:** [https://nextjs.org/docs/messages/tailwind-ssr](https://nextjs.org/docs/messages/tailwind-ssr)

**Licença:** MIT

**Tags:** tailwind, ssr, nextjs, hydration, css, fixes

**Documentação:** [https://tailwindcss.com/docs/guides/nextjs](https://tailwindcss.com/docs/guides/nextjs)

**GitHub:** [https://github.com/tailwindlabs/tailwindcss/discussions](https://github.com/tailwindlabs/tailwindcss/discussions)

**Instalação:** Siga a documentação oficial do Next.js + Tailwind

**Padrões Comuns:**
- Configuração correta do PostCSS
- Import order no globals.css
- Purge configuration
- JIT mode setup
- Dark mode com SSR
- Custom CSS variables
- Component-level styles
- Build optimization
- Development vs Production
- Hydration consistency

**Problemas Conhecidos:**
- Flash of unstyled content (FOUC)
- Hydration mismatches
- Build time issues
- CSS order problems
- Dark mode flickering
- Purge removing needed styles

---

