#!/usr/bin/env python3
"""
Recurring Modules Sources - Fontes para Módulos Recorrentes

Este módulo contém as fontes prioritárias para módulos comumente utilizados
em desenvolvimento web, incluindo pagamentos, validação e formulários.
"""

from .seed_manager import SeedSource, SeedCategory, seed_manager

# Stripe - Pagamentos
stripe_source = SeedSource(
    name="Stripe",
    category=SeedCategory.RECURRING_MODULES,
    url="https://stripe.com",
    description="Plataforma completa de pagamentos com APIs poderosas e SDKs para desenvolvimento.",
    license="Comercial (SDK MIT)",
    priority=1,
    tags=["payments", "stripe", "checkout", "subscriptions", "webhooks", "api"],
    documentation_url="https://stripe.com/docs",
    github_url="https://github.com/stripe/stripe-node",
    examples_url="https://github.com/stripe-samples",
    installation_guide="npm install stripe @stripe/stripe-js",
    common_patterns=[
        "Payment Intents para pagamentos únicos",
        "Subscription API para assinaturas",
        "Checkout Sessions para UI pré-construída",
        "Webhooks para eventos em tempo real",
        "Customer Portal para autoatendimento",
        "Connect para marketplaces",
        "Elements para UI customizada",
        "Test mode com cartões de teste",
        "Metadata para dados customizados",
        "Idempotency keys para segurança"
    ],
    known_issues=[
        "Requer conta Stripe e configuração",
        "Webhooks precisam de HTTPS",
        "Taxas de transação aplicáveis",
        "Compliance PCI DSS necessário",
        "Debugging de webhooks complexo",
        "Rate limiting em APIs"
    ],
    alternatives=["PayPal", "Square", "Mercado Pago", "PagSeguro", "Razorpay"]
)

# Zod - Validação de dados
zod_source = SeedSource(
    name="Zod",
    category=SeedCategory.RECURRING_MODULES,
    url="https://zod.dev",
    description="Biblioteca de validação de schema TypeScript-first com inferência de tipos estática.",
    license="MIT",
    priority=1,
    tags=["validation", "typescript", "schema", "type-safe", "runtime", "parsing"],
    documentation_url="https://zod.dev/README",
    github_url="https://github.com/colinhacks/zod",
    examples_url="https://zod.dev/README#basic-usage",
    installation_guide="npm install zod",
    common_patterns=[
        "Schema definition: z.object({})",
        "Type inference: z.infer<typeof schema>",
        "Runtime validation: schema.parse(data)",
        "Safe parsing: schema.safeParse(data)",
        "Transform data: schema.transform()",
        "Refinements: schema.refine()",
        "Optional fields: z.string().optional()",
        "Arrays: z.array(z.string())",
        "Unions: z.union([z.string(), z.number()])",
        "Custom error messages"
    ],
    known_issues=[
        "Bundle size pode crescer",
        "Error messages podem ser verbosas",
        "Performance em schemas complexos",
        "Curva de aprendizado inicial",
        "Debugging de schemas aninhados"
    ],
    alternatives=["Yup", "Joi", "Ajv", "io-ts", "Superstruct"]
)

# React Hook Form - Formulários
react_hook_form_source = SeedSource(
    name="React Hook Form",
    category=SeedCategory.RECURRING_MODULES,
    url="https://react-hook-form.com",
    description="Biblioteca performática e flexível para formulários React com validação mínima de re-renders.",
    license="MIT",
    priority=1,
    tags=["forms", "react", "validation", "performance", "typescript", "hooks"],
    documentation_url="https://react-hook-form.com/get-started",
    github_url="https://github.com/react-hook-form/react-hook-form",
    examples_url="https://react-hook-form.com/form-builder",
    installation_guide="npm install react-hook-form",
    common_patterns=[
        "useForm hook: const { register, handleSubmit } = useForm()",
        "Register inputs: {...register('name')}",
        "Form submission: handleSubmit(onSubmit)",
        "Validation com resolver (Zod, Yup)",
        "Watch values: watch('fieldName')",
        "Set values: setValue('name', value)",
        "Error handling: formState.errors",
        "Field arrays: useFieldArray",
        "Controller para componentes customizados",
        "Reset form: reset()"
    ],
    known_issues=[
        "Curva de aprendizado para casos complexos",
        "Debugging pode ser desafiador",
        "Integração com UI libraries",
        "TypeScript setup complexo",
        "Documentação pode ser confusa"
    ],
    alternatives=["Formik", "Final Form", "React Final Form", "Unform"]
)

# React Query/TanStack Query - Data fetching
tanstack_query_source = SeedSource(
    name="TanStack Query",
    category=SeedCategory.RECURRING_MODULES,
    url="https://tanstack.com/query",
    description="Biblioteca poderosa para data fetching, caching, sincronização e atualizações de servidor.",
    license="MIT",
    priority=2,
    tags=["data-fetching", "caching", "react", "server-state", "mutations", "typescript"],
    documentation_url="https://tanstack.com/query/latest",
    github_url="https://github.com/TanStack/query",
    examples_url="https://tanstack.com/query/latest/docs/react/examples/simple",
    installation_guide="npm install @tanstack/react-query",
    common_patterns=[
        "useQuery para data fetching",
        "useMutation para modificações",
        "Query keys para cache management",
        "Stale time e cache time",
        "Background refetching",
        "Optimistic updates",
        "Infinite queries",
        "Query invalidation",
        "Error boundaries",
        "DevTools para debugging"
    ],
    known_issues=[
        "Configuração inicial complexa",
        "Cache management pode ser confuso",
        "Bundle size considerável",
        "Debugging de cache states",
        "Performance com muitas queries"
    ],
    alternatives=["SWR", "Apollo Client", "Relay", "RTK Query"]
)

# Zustand - State management
zustand_source = SeedSource(
    name="Zustand",
    category=SeedCategory.RECURRING_MODULES,
    url="https://zustand-demo.pmnd.rs",
    description="Solução pequena, rápida e escalável de gerenciamento de estado para React.",
    license="MIT",
    priority=2,
    tags=["state-management", "react", "typescript", "simple", "lightweight"],
    documentation_url="https://github.com/pmndrs/zustand",
    github_url="https://github.com/pmndrs/zustand",
    examples_url="https://github.com/pmndrs/zustand#first-create-a-store",
    installation_guide="npm install zustand",
    common_patterns=[
        "Create store: create((set) => ({}))",
        "Use store: const state = useStore()",
        "Update state: set((state) => ({}))",
        "Async actions",
        "Subscriptions",
        "Persist middleware",
        "Immer middleware",
        "DevTools integration",
        "TypeScript support",
        "Vanilla JS usage"
    ],
    known_issues=[
        "Menos ecosystem que Redux",
        "DevTools limitados",
        "Documentação pode ser básica",
        "Patterns não estabelecidos",
        "Time travel debugging limitado"
    ],
    alternatives=["Redux Toolkit", "Jotai", "Valtio", "Context API"]
)

# Date-fns - Manipulação de datas
date_fns_source = SeedSource(
    name="date-fns",
    category=SeedCategory.RECURRING_MODULES,
    url="https://date-fns.org",
    description="Biblioteca moderna de utilitários para datas em JavaScript com suporte a tree-shaking.",
    license="MIT",
    priority=2,
    tags=["dates", "time", "utilities", "tree-shaking", "immutable", "typescript"],
    documentation_url="https://date-fns.org/docs/Getting-Started",
    github_url="https://github.com/date-fns/date-fns",
    examples_url="https://date-fns.org/docs/Getting-Started#examples",
    installation_guide="npm install date-fns",
    common_patterns=[
        "Import específico: import { format } from 'date-fns'",
        "Format dates: format(date, 'yyyy-MM-dd')",
        "Parse dates: parse(dateString, format, new Date())",
        "Add/subtract: addDays(date, 7)",
        "Compare dates: isAfter(date1, date2)",
        "Locale support: import { ptBR } from 'date-fns/locale'",
        "Time zones: date-fns-tz",
        "Immutable operations",
        "Tree-shaking friendly",
        "TypeScript definitions"
    ],
    known_issues=[
        "Bundle size sem tree-shaking",
        "Time zone handling complexo",
        "Locale imports manuais",
        "API pode ser verbosa",
        "Migração de moment.js"
    ],
    alternatives=["Day.js", "Luxon", "Moment.js", "JS Date nativo"]
)

# Lista de todas as fontes de módulos recorrentes
recurring_modules_sources = [
    stripe_source,
    zod_source,
    react_hook_form_source,
    tanstack_query_source,
    zustand_source,
    date_fns_source
]

# Registra todas as fontes no seed_manager
for source in recurring_modules_sources:
    seed_manager.add_source(source)

# Classes para exportação
class StripeSource:
    """Classe de conveniência para Stripe"""
    
    @staticmethod
    def get_env_variables() -> list:
        return [
            "STRIPE_PUBLISHABLE_KEY",
            "STRIPE_SECRET_KEY",
            "STRIPE_WEBHOOK_SECRET",
            "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY"
        ]
    
    @staticmethod
    def get_test_cards() -> dict:
        return {
            "visa": "4242424242424242",
            "visa_debit": "4000056655665556",
            "mastercard": "5555555555554444",
            "amex": "378282246310005",
            "declined": "4000000000000002",
            "insufficient_funds": "4000000000009995"
        }
    
    @staticmethod
    def get_webhook_events() -> list:
        return [
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "invoice.payment_succeeded",
            "invoice.payment_failed"
        ]

class ZodSource:
    """Classe de conveniência para Zod"""
    
    @staticmethod
    def get_common_schemas() -> dict:
        return {
            "string": "z.string()",
            "email": "z.string().email()",
            "number": "z.number()",
            "boolean": "z.boolean()",
            "date": "z.date()",
            "optional": "z.string().optional()",
            "array": "z.array(z.string())",
            "object": "z.object({ name: z.string() })",
            "union": "z.union([z.string(), z.number()])",
            "enum": "z.enum(['a', 'b', 'c'])"
        }
    
    @staticmethod
    def get_validation_example() -> str:
        return '''import { z } from 'zod';

const UserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().min(18)
});

type User = z.infer<typeof UserSchema>;

const result = UserSchema.safeParse(data);'''

class ReactHookFormSource:
    """Classe de conveniência para React Hook Form"""
    
    @staticmethod
    def get_basic_example() -> str:
        return '''import { useForm } from 'react-hook-form';

function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  const onSubmit = (data) => console.log(data);
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name', { required: true })} />
      {errors.name && <span>This field is required</span>}
      <input type="submit" />
    </form>
  );
}'''
    
    @staticmethod
    def get_zod_integration() -> str:
        return '''import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(1),
  email: z.string().email()
});

const { register, handleSubmit } = useForm({
  resolver: zodResolver(schema)
});'''
    
    @staticmethod
    def get_common_patterns() -> list:
        return [
            "Basic registration",
            "Validation with Zod",
            "Field arrays",
            "Conditional fields",
            "File uploads",
            "Multi-step forms",
            "Custom components",
            "Form reset",
            "Watch values",
            "Error handling"
        ]