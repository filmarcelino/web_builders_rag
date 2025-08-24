# 🎯 Agente Criador de Apps - Prompts e Exemplos Práticos

## 📝 Prompts de Sistema para IA

### Prompt Principal do Agente
```
Você é um especialista em desenvolvimento de software que cria aplicações web completas baseado em descrições em linguagem natural.

Suas responsabilidades:
1. Analisar requisitos do usuário
2. Consultar base de conhecimento RAG para padrões similares
3. Gerar código completo e funcional
4. Configurar ambiente de desenvolvimento
5. Preparar deploy automático

Tecnologias que você domina:
- Frontend: React, Next.js, Vue, Angular, Tailwind CSS
- Backend: FastAPI, Node.js, Express, Django
- Database: PostgreSQL, MongoDB, Redis
- Deploy: Render, Vercel, Netlify, AWS

Sempre gere código:
- Limpo e bem documentado
- Com testes unitários
- Seguindo melhores práticas
- Pronto para produção
- Com configuração de CI/CD
```

### Prompt para Análise de Requisitos
```
Analise a seguinte descrição de aplicação e extraia:

1. **Tipo de Aplicação:** (SaaS, E-commerce, Blog, Landing Page, API, etc.)
2. **Entidades Principais:** (User, Product, Order, etc.)
3. **Funcionalidades Core:** Lista das funcionalidades essenciais
4. **Integrações Necessárias:** APIs externas, pagamentos, email, etc.
5. **Tecnologias Sugeridas:** Stack mais adequado
6. **Complexidade:** (Simples, Média, Alta)
7. **Tempo Estimado:** Horas de desenvolvimento

Descrição: {user_input}

Resposta em formato JSON estruturado.
```

### Prompt para Geração de Código
```
Gere uma aplicação completa baseada nas especificações:

Especificações: {specifications}
Template Base: {template_name}
Padrões RAG: {rag_patterns}

Gere:
1. Estrutura completa de pastas
2. Código frontend (componentes, páginas, estilos)
3. Código backend (APIs, modelos, validações)
4. Configurações (package.json, requirements.txt, etc.)
5. Testes unitários básicos
6. README com instruções
7. Docker setup
8. Deploy configuration

Código deve ser:
- Funcional e testável
- Bem comentado
- Seguir padrões de mercado
- Incluir tratamento de erros
- Responsivo (frontend)
```

## 🏗️ Templates de Aplicação

### 1. SaaS Dashboard Template
```json
{
  "name": "saas-dashboard",
  "description": "Dashboard SaaS completo com auth, billing e analytics",
  "stack": {
    "frontend": "Next.js + TypeScript + Tailwind",
    "backend": "FastAPI + PostgreSQL",
    "auth": "NextAuth.js",
    "payments": "Stripe",
    "deploy": "Render"
  },
  "features": [
    "User authentication",
    "Subscription management",
    "Analytics dashboard",
    "Admin panel",
    "API management",
    "Email notifications"
  ],
  "structure": {
    "frontend": [
      "pages/dashboard",
      "components/auth",
      "components/billing",
      "components/analytics",
      "lib/api",
      "styles/globals.css"
    ],
    "backend": [
      "app/auth",
      "app/billing",
      "app/analytics",
      "app/models",
      "app/api",
      "requirements.txt"
    ]
  }
}
```

### 2. E-commerce Template
```json
{
  "name": "ecommerce-store",
  "description": "Loja online completa com carrinho e pagamentos",
  "stack": {
    "frontend": "React + TypeScript + Styled Components",
    "backend": "FastAPI + PostgreSQL",
    "payments": "Stripe",
    "storage": "Cloudinary",
    "deploy": "Render + Vercel"
  },
  "features": [
    "Product catalog",
    "Shopping cart",
    "Checkout process",
    "User accounts",
    "Order management",
    "Admin dashboard",
    "Inventory tracking"
  ],
  "integrations": [
    "Stripe (payments)",
    "Cloudinary (images)",
    "SendGrid (emails)",
    "Google Analytics"
  ]
}
```

### 3. Blog/CMS Template
```json
{
  "name": "blog-cms",
  "description": "Blog com CMS e SEO otimizado",
  "stack": {
    "frontend": "Next.js + MDX + Tailwind",
    "backend": "Headless CMS (Strapi)",
    "database": "PostgreSQL",
    "deploy": "Vercel + Render"
  },
  "features": [
    "Rich text editor",
    "SEO optimization",
    "Comment system",
    "Tag/category system",
    "Search functionality",
    "RSS feed",
    "Social sharing"
  ]
}
```

## 💬 Exemplos de Conversação

### Exemplo 1: Criação de SaaS
```
Usuário: "Quero criar um SaaS para gerenciar projetos de equipes, com planos pagos e dashboard analytics"

Agente: "Perfeito! Vou criar um SaaS de gerenciamento de projetos. Baseado na sua descrição, identifiquei:

📋 **Análise:**
- Tipo: SaaS B2B
- Core: Gerenciamento de projetos + equipes
- Monetização: Planos de assinatura
- Analytics: Dashboard com métricas

🛠️ **Stack Sugerida:**
- Frontend: Next.js + TypeScript + Tailwind
- Backend: FastAPI + PostgreSQL
- Auth: NextAuth.js
- Payments: Stripe
- Analytics: Custom dashboard

⚡ **Funcionalidades:**
- Criação/gestão de projetos
- Convite de membros da equipe
- Sistema de tarefas/kanban
- Planos (Free, Pro, Enterprise)
- Dashboard com métricas
- Notificações em tempo real

Vou começar a gerar o código. Tempo estimado: 4-5 minutos."
```

### Exemplo 2: E-commerce Específico
```
Usuário: "Preciso de uma loja online para vender cursos digitais com área do aluno"

Agente: "Excelente! Um marketplace de cursos digitais. Vou adaptar o template e-commerce para produtos digitais:

📚 **Especificações:**
- Produtos: Cursos digitais (vídeos, PDFs)
- Área do aluno: Acesso aos cursos comprados
- Pagamentos: Stripe + PIX (Brasil)
- Entrega: Acesso imediato pós-pagamento

🎯 **Funcionalidades Especiais:**
- Player de vídeo personalizado
- Progresso do curso
- Certificados de conclusão
- Sistema de avaliações
- Cupons de desconto
- Afiliados (opcional)

Iniciando geração..."
```

## 🔄 Fluxo de Refinamento

### Prompts de Refinamento
```
# Após geração inicial
"O código foi gerado! Gostaria de fazer algum ajuste?

Opções disponíveis:
1. 🎨 Modificar design/UI
2. ⚙️ Adicionar funcionalidades
3. 🔧 Alterar tecnologias
4. 🚀 Configurar deploy
5. 📱 Tornar responsivo
6. 🔒 Melhorar segurança
7. ⚡ Otimizar performance

Ou descreva o que gostaria de mudar!"
```

### Exemplo de Refinamento
```
Usuário: "Quero adicionar um chat ao vivo no e-commerce"

Agente: "Ótima ideia! Vou integrar um sistema de chat ao vivo:

💬 **Implementação:**
- Widget de chat flutuante
- Notificações em tempo real
- Histórico de conversas
- Status online/offline
- Integração com admin

🛠️ **Tecnologia:**
- Socket.io para real-time
- Componente React customizado
- Armazenamento no PostgreSQL

Atualizando código..."
```

## 📊 Prompts para Análise RAG

### Busca de Padrões
```
Consulte a base RAG para encontrar:

1. **Projetos similares:** {project_type}
2. **Padrões de código:** {technology_stack}
3. **Melhores práticas:** {domain}
4. **Componentes reutilizáveis:** {ui_components}
5. **Configurações otimizadas:** {deployment}

Query RAG: "projeto {project_type} usando {tech_stack} com funcionalidades {features}"

Retorne top 5 resultados mais relevantes com:
- Código de exemplo
- Configurações
- Lições aprendidas
- Performance tips
```

### Integração com RAG
```python
# Exemplo de integração
async def get_rag_insights(project_specs):
    query = f"""
    projeto {project_specs.type} 
    tecnologias {project_specs.stack}
    funcionalidades {project_specs.features}
    """
    
    rag_results = await rag_client.search(
        query=query,
        category="code_patterns",
        limit=10
    )
    
    return {
        "patterns": rag_results.patterns,
        "best_practices": rag_results.practices,
        "components": rag_results.components,
        "configs": rag_results.configurations
    }
```

## 🎨 Templates de UI/UX

### Design System Base
```css
/* Cores principais */
:root {
  --primary: #3b82f6;
  --secondary: #64748b;
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --background: #ffffff;
  --surface: #f8fafc;
  --text: #1e293b;
}

/* Componentes base */
.btn-primary {
  @apply bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors;
}

.card {
  @apply bg-surface border border-gray-200 rounded-lg p-6 shadow-sm;
}

.input {
  @apply border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-transparent;
}
```

### Componentes React Base
```tsx
// Button Component
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline';
  size: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({ 
  variant, size, children, onClick 
}) => {
  const baseClasses = 'font-medium rounded-lg transition-colors';
  const variantClasses = {
    primary: 'bg-primary text-white hover:bg-primary/90',
    secondary: 'bg-secondary text-white hover:bg-secondary/90',
    outline: 'border border-primary text-primary hover:bg-primary hover:text-white'
  };
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  };
  
  return (
    <button 
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
```

## 🚀 Scripts de Deploy

### Deploy Render
```yaml
# render.yaml
services:
  - type: web
    name: app-creator-frontend
    env: node
    buildCommand: npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: NEXT_PUBLIC_API_URL
        fromService:
          type: web
          name: app-creator-backend
          property: host

  - type: web
    name: app-creator-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: app-creator-db
          property: connectionString

  - type: postgres
    name: app-creator-db
    databaseName: app_creator
    user: app_creator_user
```

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run tests
        run: npm test
        
      - name: Build
        run: npm run build
        
      - name: Deploy to Render
        uses: render-deploy/github-action@v1
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
```

---

**Este arquivo complementa a especificação principal com exemplos práticos para acelerar o desenvolvimento do agente criador de apps.**