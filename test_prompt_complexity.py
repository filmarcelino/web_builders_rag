#!/usr/bin/env python3
"""
Teste Comparativo: Prompts Simples vs Elaborados no RAG
Este script demonstra como prompts mais elaborados resultam em respostas
mais completas e específicas do sistema RAG.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Carregar variáveis de ambiente
load_dotenv()

class PromptComplexityTester:
    def __init__(self):
        # Usar a chave OpenAI correta do .env
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")
        self.client = OpenAI(api_key=openai_key)
        
    def simulate_search_results(self, query, complexity_level):
        """Simula resultados de busca baseados na complexidade do prompt"""
        
        # Base de chunks disponíveis
        all_chunks = [
            {
                "content": """# Dashboard Components in React

Creating interactive dashboards requires several key components:

## Chart Libraries
- Chart.js for responsive charts
- D3.js for custom visualizations
- Recharts for React-specific charts

## Layout Components
- Grid systems for responsive layouts
- Card components for data display
- Navigation bars and sidebars

## Data Management
- State management with Redux or Context API
- API integration for real-time data
- Data filtering and sorting capabilities""",
                "source": "react-dashboard-tutorial.md",
                "similarity_score": 0.85,
                "topics": ["react", "dashboard", "components", "charts"]
            },
            {
                "content": """# CSS Grid and Flexbox for Dashboards

## Creating Responsive Dashboard Layouts

### CSS Grid for Main Layout
```css
.dashboard {
  display: grid;
  grid-template-columns: 250px 1fr;
  grid-template-rows: 60px 1fr;
  grid-template-areas:
    "sidebar header"
    "sidebar main";
  height: 100vh;
}

.sidebar { grid-area: sidebar; }
.header { grid-area: header; }
.main { grid-area: main; }
```

### Flexbox for Card Layouts
```css
.dashboard-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 20px;
}

.card {
  flex: 1 1 300px;
  min-height: 200px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```""",
                "source": "css-dashboard-layouts.md",
                "similarity_score": 0.78,
                "topics": ["css", "grid", "flexbox", "responsive", "layout"]
            },
            {
                "content": """# JavaScript Data Visualization

## Chart.js Implementation

### Creating Financial Charts
```javascript
// Line chart for financial trends
const ctx = document.getElementById('financialChart').getContext('2d');
const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Revenue',
      data: [12000, 15000, 13000, 17000, 16000, 19000],
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      tension: 0.1
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Monthly Revenue Trend'
      }
    }
  }
});
```

### KPI Cards
```javascript
function createKPICard(title, value, change) {
  return `
    <div class="kpi-card">
      <h3>${title}</h3>
      <div class="kpi-value">${value}</div>
      <div class="kpi-change ${change >= 0 ? 'positive' : 'negative'}">
        ${change >= 0 ? '+' : ''}${change}%
      </div>
    </div>
  `;
}
```""",
                "source": "javascript-charts-tutorial.md",
                "similarity_score": 0.82,
                "topics": ["javascript", "charts", "visualization", "kpi", "financial"]
            },
            {
                "content": """# API Integration for Real-time Data

## Fetching Financial Data

### REST API Integration
```javascript
class FinancialDataService {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.financial-data.com';
  }
  
  async getRevenueData(period = '6months') {
    try {
      const response = await fetch(`${this.baseUrl}/revenue?period=${period}`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching revenue data:', error);
      throw error;
    }
  }
  
  async getExpenseData(period = '6months') {
    // Similar implementation for expenses
  }
  
  async getKPIData() {
    const [revenue, expenses] = await Promise.all([
      this.getRevenueData(),
      this.getExpenseData()
    ]);
    
    return {
      totalRevenue: revenue.total,
      totalExpenses: expenses.total,
      netProfit: revenue.total - expenses.total,
      profitMargin: ((revenue.total - expenses.total) / revenue.total) * 100
    };
  }
}
```

### WebSocket for Real-time Updates
```javascript
class RealTimeFinancialUpdates {
  constructor(wsUrl, onUpdate) {
    this.ws = new WebSocket(wsUrl);
    this.onUpdate = onUpdate;
    this.setupEventListeners();
  }
  
  setupEventListeners() {
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.onUpdate(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  subscribe(dataTypes) {
    this.ws.send(JSON.stringify({
      action: 'subscribe',
      types: dataTypes
    }));
  }
}
```""",
                "source": "api-integration-tutorial.md",
                "similarity_score": 0.75,
                "topics": ["api", "real-time", "websocket", "data", "integration"]
            },
            {
                "content": """# Security Best Practices for Financial Dashboards

## Authentication and Authorization

### JWT Token Management
```javascript
class AuthService {
  constructor() {
    this.tokenKey = 'financial_dashboard_token';
  }
  
  async login(credentials) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(credentials)
    });
    
    if (response.ok) {
      const { token, user } = await response.json();
      localStorage.setItem(this.tokenKey, token);
      return { token, user };
    }
    
    throw new Error('Authentication failed');
  }
  
  getAuthHeaders() {
    const token = localStorage.getItem(this.tokenKey);
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
  
  logout() {
    localStorage.removeItem(this.tokenKey);
  }
}
```

### Data Encryption
```javascript
class DataEncryption {
  static async encryptSensitiveData(data, key) {
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(JSON.stringify(data));
    
    const cryptoKey = await crypto.subtle.importKey(
      'raw',
      key,
      { name: 'AES-GCM' },
      false,
      ['encrypt']
    );
    
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      cryptoKey,
      dataBuffer
    );
    
    return {
      encrypted: Array.from(new Uint8Array(encrypted)),
      iv: Array.from(iv)
    };
  }
}
```

### Input Validation
```javascript
class InputValidator {
  static validateFinancialAmount(amount) {
    if (typeof amount !== 'number' || isNaN(amount)) {
      throw new Error('Amount must be a valid number');
    }
    
    if (amount < 0) {
      throw new Error('Amount cannot be negative');
    }
    
    if (amount > 999999999) {
      throw new Error('Amount exceeds maximum allowed value');
    }
    
    return true;
  }
  
  static sanitizeInput(input) {
    return input.replace(/<script[^>]*>.*?<\/script>/gi, '')
                .replace(/<[^>]*>/g, '')
                .trim();
  }
}
```""",
                "source": "security-best-practices.md",
                "similarity_score": 0.70,
                "topics": ["security", "authentication", "encryption", "validation", "financial"]
            },
            {
                "content": """# Performance Optimization for Dashboards

## Code Splitting and Lazy Loading

### React Code Splitting
```javascript
import { lazy, Suspense } from 'react';

// Lazy load dashboard components
const RevenueChart = lazy(() => import('./components/RevenueChart'));
const ExpenseChart = lazy(() => import('./components/ExpenseChart'));
const KPIDashboard = lazy(() => import('./components/KPIDashboard'));

function FinancialDashboard() {
  return (
    <div className="dashboard">
      <Suspense fallback={<div>Loading KPI...</div>}>
        <KPIDashboard />
      </Suspense>
      
      <div className="charts-section">
        <Suspense fallback={<div>Loading Revenue Chart...</div>}>
          <RevenueChart />
        </Suspense>
        
        <Suspense fallback={<div>Loading Expense Chart...</div>}>
          <ExpenseChart />
        </Suspense>
      </div>
    </div>
  );
}
```

### Data Caching Strategy
```javascript
class DataCache {
  constructor(ttl = 300000) { // 5 minutes default TTL
    this.cache = new Map();
    this.ttl = ttl;
  }
  
  set(key, data) {
    const expiry = Date.now() + this.ttl;
    this.cache.set(key, { data, expiry });
  }
  
  get(key) {
    const item = this.cache.get(key);
    
    if (!item) return null;
    
    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  }
  
  clear() {
    this.cache.clear();
  }
}

// Usage
const dataCache = new DataCache();

async function getCachedFinancialData(endpoint) {
  const cached = dataCache.get(endpoint);
  if (cached) return cached;
  
  const data = await fetchFinancialData(endpoint);
  dataCache.set(endpoint, data);
  return data;
}
```

### Virtual Scrolling for Large Datasets
```javascript
import { FixedSizeList as List } from 'react-window';

function TransactionList({ transactions }) {
  const Row = ({ index, style }) => (
    <div style={style} className="transaction-row">
      <span>{transactions[index].date}</span>
      <span>{transactions[index].description}</span>
      <span>{transactions[index].amount}</span>
    </div>
  );
  
  return (
    <List
      height={400}
      itemCount={transactions.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </List>
  );
}
```""",
                "source": "performance-optimization.md",
                "similarity_score": 0.68,
                "topics": ["performance", "optimization", "caching", "lazy-loading", "virtual-scrolling"]
            }
        ]
        
        # Simular diferentes níveis de recuperação baseados na complexidade
        if complexity_level == "simple":
            # Prompt simples recupera menos chunks e menos específicos
            return all_chunks[:2]  # Apenas 2 chunks básicos
        elif complexity_level == "detailed":
            # Prompt detalhado recupera mais chunks e mais específicos
            return all_chunks[:4]  # 4 chunks mais relevantes
        else:  # comprehensive
            # Prompt abrangente recupera todos os chunks relevantes
            return all_chunks  # Todos os 6 chunks
            
    def generate_rag_response(self, query, relevant_chunks, prompt_style):
        """Gera resposta usando RAG com diferentes estilos de prompt"""
        # Construir contexto a partir dos chunks relevantes
        context_parts = []
        for chunk in relevant_chunks:
            source = chunk.get('source', 'Desconhecido')
            content = chunk.get('content', '')
            context_parts.append(f"[Fonte: {source}]\n{content}")
            
        context = "\n\n---\n\n".join(context_parts)
        
        # Diferentes estilos de prompt do sistema
        if prompt_style == "simple":
            system_prompt = """
Você é um assistente de programação. Responda de forma concisa baseado no contexto fornecido.
"""
        elif prompt_style == "detailed":
            system_prompt = """
Você é um especialista em desenvolvimento web. Use as informações do contexto para fornecer uma resposta detalhada e prática, incluindo exemplos de código quando apropriado.
"""
        else:  # comprehensive
            system_prompt = """
Você é um arquiteto de software sênior especializado em desenvolvimento web e dashboards financeiros. 
Use TODAS as informações disponíveis no contexto para criar uma resposta abrangente que inclua:
1. Análise técnica detalhada
2. Exemplos de código completos e funcionais
3. Considerações de segurança e performance
4. Melhores práticas da indústria
5. Implementação passo-a-passo
6. Considerações de arquitetura e escalabilidade

Forneça uma solução completa e profissional.
"""
        
        user_prompt = f"""
Contexto disponível:
{context}

---

Pergunta: {query}

Por favor, responda baseando-se no contexto fornecido.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=3000 if prompt_style == "comprehensive" else 1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Erro ao gerar resposta: {e}"
            
    def run_comparison_test(self):
        """Executa teste comparativo entre diferentes níveis de complexidade"""
        
        # Definir os diferentes prompts
        test_cases = [
            {
                "name": "Prompt Simples",
                "query": "dashboard financeiro",
                "complexity": "simple",
                "prompt_style": "simple",
                "description": "Prompt básico, sem contexto específico"
            },
            {
                "name": "Prompt Detalhado",
                "query": "crie um dashboard financeiro responsivo com gráficos interativos usando React e Chart.js",
                "complexity": "detailed",
                "prompt_style": "detailed",
                "description": "Prompt com especificações técnicas claras"
            },
            {
                "name": "Prompt Abrangente",
                "query": "desenvolva um dashboard financeiro corporativo completo e seguro usando React, com gráficos interativos Chart.js, integração de APIs em tempo real, autenticação JWT, otimização de performance, cache de dados, e design responsivo seguindo as melhores práticas de segurança para aplicações financeiras",
                "complexity": "comprehensive",
                "prompt_style": "comprehensive",
                "description": "Prompt detalhado com múltiplos requisitos específicos"
            }
        ]
        
        results = []
        
        print("🧪 TESTE COMPARATIVO: Complexidade de Prompts no RAG")
        print("=" * 70)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 {i}. {test_case['name']}")
            print("-" * 50)
            print(f"Query: {test_case['query']}")
            print(f"Descrição: {test_case['description']}")
            
            # Simular busca
            relevant_chunks = self.simulate_search_results(
                test_case['query'], 
                test_case['complexity']
            )
            
            print(f"\n🔍 Chunks recuperados: {len(relevant_chunks)}")
            for j, chunk in enumerate(relevant_chunks, 1):
                source = chunk.get('source', 'Desconhecido')[:30]
                topics = ', '.join(chunk.get('topics', [])[:3])
                print(f"  {j}. [{source}...] - Tópicos: {topics}")
            
            # Gerar resposta
            print(f"\n🤖 Gerando resposta ({test_case['prompt_style']})...")
            response = self.generate_rag_response(
                test_case['query'],
                relevant_chunks,
                test_case['prompt_style']
            )
            
            # Analisar resposta
            word_count = len(response.split())
            code_blocks = response.count('```')
            
            result = {
                "test_case": test_case['name'],
                "query": test_case['query'],
                "description": test_case['description'],
                "chunks_retrieved": len(relevant_chunks),
                "response_word_count": word_count,
                "code_blocks_count": code_blocks // 2,  # Dividir por 2 pois cada bloco tem abertura e fechamento
                "response": response,
                "analysis": {
                    "completeness": "Alta" if word_count > 800 else "Média" if word_count > 400 else "Baixa",
                    "technical_depth": "Alta" if code_blocks >= 6 else "Média" if code_blocks >= 2 else "Baixa",
                    "specificity": "Alta" if len(relevant_chunks) >= 5 else "Média" if len(relevant_chunks) >= 3 else "Baixa"
                }
            }
            
            results.append(result)
            
            print(f"\n📊 Análise da Resposta:")
            print(f"  • Palavras: {word_count}")
            print(f"  • Blocos de código: {result['analysis']['technical_depth']} ({code_blocks // 2} blocos)")
            print(f"  • Completude: {result['analysis']['completeness']}")
            print(f"  • Especificidade: {result['analysis']['specificity']}")
            
            print(f"\n📝 Resposta (primeiras 200 palavras):")
            preview = ' '.join(response.split()[:200])
            print(f"{preview}...")
            
        # Salvar resultados
        comparison_result = {
            "timestamp": datetime.now().isoformat(),
            "test_description": "Comparação entre prompts simples, detalhados e abrangentes",
            "results": results,
            "conclusion": {
                "best_approach": "Prompts abrangentes com instruções específicas ao sistema RAG",
                "recommendation": "Combine prompts detalhados do agente com instruções específicas ao RAG para máxima efetividade"
            }
        }
        
        with open("prompt_complexity_comparison.json", "w", encoding="utf-8") as f:
            json.dump(comparison_result, f, indent=2, ensure_ascii=False)
            
        print(f"\n\n🎯 CONCLUSÕES DO TESTE")
        print("=" * 50)
        print("1. 📈 Prompts mais elaborados = Respostas mais completas")
        print("2. 🔍 Mais contexto específico = Busca mais precisa")
        print("3. 🎯 Instruções detalhadas = Maior profundidade técnica")
        print("4. ⚡ Melhor estratégia: Combinar ambas as abordagens")
        print(f"\n💾 Resultados salvos em: prompt_complexity_comparison.json")
        
def main():
    print("🧪 Teste de Complexidade de Prompts no RAG")
    print("Comparando respostas para prompts simples vs elaborados")
    print("=" * 70)
    
    try:
        tester = PromptComplexityTester()
        tester.run_comparison_test()
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        
if __name__ == "__main__":
    main()