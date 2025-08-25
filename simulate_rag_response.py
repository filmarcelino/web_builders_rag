#!/usr/bin/env python3
"""
Simulação de como o RAG responde ao prompt: "crie um dashboard financeiro"
Este script demonstra o processo de busca e resposta do RAG sem acessar o índice real.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Carregar variáveis de ambiente
load_dotenv()

class RAGSimulator:
    def __init__(self):
        # Usar a chave OpenAI correta do .env
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")
        self.client = OpenAI(api_key=openai_key)
        
    def simulate_search_results(self, query):
        """Simula resultados de busca baseados no corpus conhecido"""
        # Chunks simulados que seriam encontrados para "dashboard financeiro"
        simulated_chunks = [
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
                "rank": 1
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
                "rank": 2
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
                "rank": 3
            },
            {
                "content": """# HTML Structure for Dashboards

## Semantic HTML for Financial Dashboards

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Financeiro</title>
    <link rel="stylesheet" href="dashboard.css">
</head>
<body>
    <div class="dashboard">
        <aside class="sidebar">
            <nav class="nav-menu">
                <ul>
                    <li><a href="#overview">Visão Geral</a></li>
                    <li><a href="#revenue">Receitas</a></li>
                    <li><a href="#expenses">Despesas</a></li>
                    <li><a href="#reports">Relatórios</a></li>
                </ul>
            </nav>
        </aside>
        
        <header class="header">
            <h1>Dashboard Financeiro</h1>
            <div class="user-info">
                <span>Bem-vindo, Usuário</span>
            </div>
        </header>
        
        <main class="main-content">
            <section class="kpi-section">
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <h3>Receita Total</h3>
                        <div class="kpi-value">R$ 125.000</div>
                    </div>
                    <div class="kpi-card">
                        <h3>Despesas</h3>
                        <div class="kpi-value">R$ 85.000</div>
                    </div>
                    <div class="kpi-card">
                        <h3>Lucro Líquido</h3>
                        <div class="kpi-value">R$ 40.000</div>
                    </div>
                </div>
            </section>
            
            <section class="charts-section">
                <div class="chart-container">
                    <canvas id="revenueChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="expenseChart"></canvas>
                </div>
            </section>
        </main>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="dashboard.js"></script>
</body>
</html>
```""",
                "source": "html-dashboard-structure.md",
                "similarity_score": 0.79,
                "rank": 4
            },
            {
                "content": """# Responsive Design for Dashboards

## Mobile-First Dashboard Design

### Media Queries for Dashboard
```css
/* Mobile First */
.dashboard {
  display: flex;
  flex-direction: column;
}

.sidebar {
  order: 2;
  width: 100%;
  height: auto;
}

.main-content {
  order: 1;
  padding: 10px;
}

/* Tablet */
@media (min-width: 768px) {
  .dashboard {
    display: grid;
    grid-template-columns: 200px 1fr;
  }
  
  .sidebar {
    order: initial;
    width: auto;
    height: 100vh;
  }
  
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .dashboard {
    grid-template-columns: 250px 1fr;
  }
  
  .kpi-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .charts-section {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
  }
}
```

### Accessibility Features
```css
/* High contrast mode */
@media (prefers-contrast: high) {
  .dashboard {
    background: #000;
    color: #fff;
  }
  
  .card {
    border: 2px solid #fff;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .chart-animation {
    animation: none;
  }
}
```""",
                "source": "responsive-dashboard-design.md",
                "similarity_score": 0.75,
                "rank": 5
            }
        ]
        
        return simulated_chunks
        
    def generate_rag_response(self, query, relevant_chunks):
        """Gera resposta usando RAG"""
        # Construir contexto a partir dos chunks relevantes
        context_parts = []
        for chunk in relevant_chunks:
            source = chunk.get('source', 'Desconhecido')
            content = chunk.get('content', '')
            context_parts.append(f"[Fonte: {source}]\n{content}")
            
        context = "\n\n---\n\n".join(context_parts)
        
        # Prompt para o modelo
        system_prompt = """
Você é um assistente especializado em desenvolvimento web e programação.
Use APENAS as informações fornecidas no contexto para responder à pergunta.
Forneça uma resposta prática e detalhada, incluindo código quando apropriado.
Sempre cite as fontes quando possível.
"""
        
        user_prompt = f"""
Contexto disponível:
{context}

---

Pergunta: {query}

Por favor, crie um guia completo baseando-se exclusivamente no contexto fornecido.
Inclua exemplos de código e estrutura quando disponível.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Erro ao gerar resposta: {e}"
            
    def demonstrate_rag_process(self):
        """Demonstra o processo completo do RAG"""
        query = "crie um dashboard financeiro"
        
        print(f"\n🎯 Demonstração RAG - Prompt: '{query}'")
        print("=" * 70)
        
        # Simular busca
        print("\n🔍 1. BUSCA SEMÂNTICA")
        print("-" * 30)
        print("O RAG converte o prompt em embedding e busca chunks similares...")
        
        relevant_chunks = self.simulate_search_results(query)
        
        print(f"\n📋 2. CHUNKS ENCONTRADOS ({len(relevant_chunks)}):")
        print("-" * 40)
        for chunk in relevant_chunks:
            source = chunk.get('source', 'Desconhecido')
            score = chunk.get('similarity_score', 0)
            rank = chunk.get('rank', 0)
            content_preview = chunk.get('content', '')[:150].replace('\n', ' ')
            print(f"  {rank}. [{source}] (Score: {score:.2f})")
            print(f"     Preview: {content_preview}...\n")
            
        # Gerar resposta RAG
        print("\n🤖 3. GERAÇÃO DA RESPOSTA")
        print("-" * 30)
        print("Enviando contexto + prompt para o modelo de linguagem...")
        
        rag_response = self.generate_rag_response(query, relevant_chunks)
        
        # Mostrar resposta
        print("\n📝 4. RESPOSTA FINAL DO RAG:")
        print("=" * 50)
        print(rag_response)
        print("=" * 50)
        
        # Salvar resultado
        result = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "process_steps": [
                "1. Conversão do prompt em embedding",
                "2. Busca semântica no índice FAISS",
                "3. Recuperação de chunks relevantes",
                "4. Construção do contexto",
                "5. Geração da resposta com LLM"
            ],
            "relevant_chunks_count": len(relevant_chunks),
            "relevant_chunks": relevant_chunks,
            "rag_response": rag_response,
            "explanation": "Esta é uma simulação do processo RAG baseada no corpus de desenvolvimento web indexado."
        }
        
        with open("rag_dashboard_demonstration.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Demonstração salva em: rag_dashboard_demonstration.json")
        
def main():
    print("🧪 Demonstração do Sistema RAG")
    print("Como o RAG responde ao prompt: 'crie um dashboard financeiro'")
    print("=" * 70)
    
    try:
        # Inicializar simulador
        simulator = RAGSimulator()
        
        # Executar demonstração
        simulator.demonstrate_rag_process()
        
        print("\n✅ Demonstração concluída!")
        print("\n💡 RESUMO DO PROCESSO RAG:")
        print("1. 🔍 Busca semântica encontra chunks relevantes sobre dashboards")
        print("2. 📊 Recupera informações sobre React, CSS, HTML e JavaScript")
        print("3. 🤖 Combina conhecimento para criar resposta personalizada")
        print("4. ✨ Gera código e instruções específicas para dashboard financeiro")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        
if __name__ == "__main__":
    main()