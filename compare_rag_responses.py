#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparação entre Respostas RAG: Prompt Simples vs Prompt Detalhado
Analisa as diferenças em qualidade, conteúdo e complexidade das respostas.
"""

import json
import re
from datetime import datetime
from pathlib import Path

def analyze_response(response_data):
    """Analisa uma resposta RAG e extrai métricas."""
    rag_response = response_data.get('rag_response', '')
    
    # Métricas básicas
    word_count = len(rag_response.split())
    char_count = len(rag_response)
    line_count = len(rag_response.split('\n'))
    
    # Contagem de blocos de código
    code_blocks = len(re.findall(r'```[\s\S]*?```', rag_response))
    
    # Contagem de seções/títulos
    sections = len(re.findall(r'^#{1,6}\s+', rag_response, re.MULTILINE))
    
    # Contagem de listas
    lists = len(re.findall(r'^[-*+]\s+', rag_response, re.MULTILINE))
    
    # Análise de chunks relevantes
    chunks_count = response_data.get('relevant_chunks_count', 0)
    avg_similarity = 0
    if 'relevant_chunks' in response_data:
        similarities = [chunk.get('similarity_score', 0) for chunk in response_data['relevant_chunks']]
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
    
    # Análise de tecnologias mencionadas
    technologies = []
    tech_patterns = {
        'React': r'\bReact\b',
        'JavaScript': r'\bJavaScript\b',
        'CSS': r'\bCSS\b',
        'HTML': r'\bHTML\b',
        'Chart.js': r'\bChart\.js\b',
        'Grid': r'\bGrid\b',
        'Flexbox': r'\bFlexbox\b',
        'API': r'\bAPI\b',
        'Redux': r'\bRedux\b',
        'Context API': r'\bContext API\b'
    }
    
    for tech, pattern in tech_patterns.items():
        if re.search(pattern, rag_response, re.IGNORECASE):
            technologies.append(tech)
    
    # Análise de funcionalidades específicas
    features = []
    feature_patterns = {
        'Animações': r'\banimação|animation\b',
        'Responsividade': r'\bresponsiv|media queries\b',
        'Gráficos': r'\bgráfico|chart|graph\b',
        'KPI/Métricas': r'\bKPI|métrica|metric\b',
        'Dashboard': r'\bdashboard\b',
        'Finanças Pessoais': r'\bfinanças pessoais|personal finance\b',
        'Setor Financeiro': r'\bsetor|sector|industry\b'
    }
    
    for feature, pattern in feature_patterns.items():
        if re.search(pattern, rag_response, re.IGNORECASE):
            features.append(feature)
    
    return {
        'metrics': {
            'word_count': word_count,
            'char_count': char_count,
            'line_count': line_count,
            'code_blocks': code_blocks,
            'sections': sections,
            'lists': lists
        },
        'rag_metrics': {
            'chunks_count': chunks_count,
            'avg_similarity': round(avg_similarity, 3)
        },
        'content_analysis': {
            'technologies': technologies,
            'features': features,
            'tech_count': len(technologies),
            'feature_count': len(features)
        }
    }

def compare_responses():
    """Compara as duas respostas RAG."""
    
    # Carrega o arquivo de demonstração atual (resposta detalhada)
    demo_file = Path('rag_dashboard_demonstration.json')
    
    if not demo_file.exists():
        print("❌ Arquivo de demonstração não encontrado!")
        return
    
    with open(demo_file, 'r', encoding='utf-8') as f:
        detailed_response = json.load(f)
    
    # Simula resposta simples baseada no teste anterior
    simple_response = {
        'query': 'faça um app financeiro completo',
        'relevant_chunks_count': 5,
        'relevant_chunks': [
            {'similarity_score': 0.85},
            {'similarity_score': 0.78},
            {'similarity_score': 0.82},
            {'similarity_score': 0.79},
            {'similarity_score': 0.75}
        ],
        'rag_response': '''Para criar um dashboard financeiro interativo em React, você pode seguir este guia passo a passo, utilizando os componentes e técnicas mencionadas no contexto fornecido. Vamos construir um dashboard que inclui uma estrutura HTML semântica, estilos CSS para layout responsivo, e gráficos usando Chart.js.

### 1. Estrutura HTML

Utilizaremos a estrutura HTML básica para o nosso dashboard financeiro:

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
```

### 2. Estilos CSS

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
.main-content { grid-area: main; padding: 20px; }

.kpi-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.kpi-card {
  flex: 1 1 300px;
  min-height: 200px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 20px;
}
```

### 3. Gráficos com Chart.js

```javascript
const revenueData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
        label: 'Receita',
        data: [12000, 15000, 13000, 17000, 16000, 19000],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
    }]
};

const ctxRevenue = document.getElementById('revenueChart').getContext('2d');
const revenueChart = new Chart(ctxRevenue, {
    type: 'line',
    data: revenueData,
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Tendência de Receita Mensal'
            }
        }
    }
});
```

### 4. Conclusão

Com essa configuração, você terá um dashboard financeiro interativo que exibe receitas, despesas e lucros através de gráficos e cards informativos. Você pode expandir essa base adicionando funcionalidades como filtros, integração com APIs para dados em tempo real, e gerenciando o estado da aplicação usando Redux ou Context API conforme necessário.

Esse guia fornece uma base sólida e pode ser aprimorado de acordo com as necessidades específicas do seu projeto.'''
    }
    
    # Analisa ambas as respostas
    print("🔍 ANÁLISE COMPARATIVA: PROMPT SIMPLES vs PROMPT DETALHADO")
    print("=" * 70)
    
    simple_analysis = analyze_response(simple_response)
    detailed_analysis = analyze_response(detailed_response)
    
    # Comparação de métricas
    print("\n📊 MÉTRICAS BÁSICAS:")
    print(f"{'Métrica':<20} {'Simples':<15} {'Detalhado':<15} {'Diferença':<15}")
    print("-" * 65)
    
    metrics = ['word_count', 'char_count', 'code_blocks', 'sections']
    for metric in metrics:
        simple_val = simple_analysis['metrics'][metric]
        detailed_val = detailed_analysis['metrics'][metric]
        diff = detailed_val - simple_val
        diff_pct = (diff / simple_val * 100) if simple_val > 0 else 0
        
        print(f"{metric.replace('_', ' ').title():<20} {simple_val:<15} {detailed_val:<15} {diff:+} ({diff_pct:+.1f}%)")
    
    # Comparação de conteúdo
    print("\n🎯 ANÁLISE DE CONTEÚDO:")
    print(f"{'Aspecto':<25} {'Simples':<15} {'Detalhado':<15}")
    print("-" * 55)
    
    print(f"{'Tecnologias Mencionadas':<25} {simple_analysis['content_analysis']['tech_count']:<15} {detailed_analysis['content_analysis']['tech_count']:<15}")
    print(f"{'Funcionalidades':<25} {simple_analysis['content_analysis']['feature_count']:<15} {detailed_analysis['content_analysis']['feature_count']:<15}")
    print(f"{'Chunks Recuperados':<25} {simple_analysis['rag_metrics']['chunks_count']:<15} {detailed_analysis['rag_metrics']['chunks_count']:<15}")
    print(f"{'Similaridade Média':<25} {simple_analysis['rag_metrics']['avg_similarity']:<15} {detailed_analysis['rag_metrics']['avg_similarity']:<15}")
    
    # Análise qualitativa
    print("\n💡 ANÁLISE QUALITATIVA:")
    print("\n🔹 PROMPT SIMPLES ('faça um app financeiro completo'):")
    print(f"   • Tecnologias: {', '.join(simple_analysis['content_analysis']['technologies'])}")
    print(f"   • Funcionalidades: {', '.join(simple_analysis['content_analysis']['features'])}")
    
    print("\n🔹 PROMPT DETALHADO ('dashboard financeiro com campos importantes, finanças pessoais, gráficos robustos e animações'):")
    print(f"   • Tecnologias: {', '.join(detailed_analysis['content_analysis']['technologies'])}")
    print(f"   • Funcionalidades: {', '.join(detailed_analysis['content_analysis']['features'])}")
    
    # Conclusões
    print("\n🎯 CONCLUSÕES:")
    
    word_improvement = ((detailed_analysis['metrics']['word_count'] - simple_analysis['metrics']['word_count']) / simple_analysis['metrics']['word_count']) * 100
    code_improvement = detailed_analysis['metrics']['code_blocks'] - simple_analysis['metrics']['code_blocks']
    
    print(f"\n✅ O prompt detalhado resultou em:")
    print(f"   • {word_improvement:+.1f}% mais palavras")
    print(f"   • {code_improvement:+} blocos de código adicionais")
    print(f"   • {detailed_analysis['content_analysis']['feature_count'] - simple_analysis['content_analysis']['feature_count']:+} funcionalidades extras")
    
    if detailed_analysis['content_analysis']['feature_count'] > simple_analysis['content_analysis']['feature_count']:
        print("   • Maior cobertura de funcionalidades específicas")
    
    if 'Animações' in detailed_analysis['content_analysis']['features'] and 'Animações' not in simple_analysis['content_analysis']['features']:
        print("   • Inclusão específica de animações (solicitado no prompt)")
    
    if 'Finanças Pessoais' in detailed_analysis['content_analysis']['features']:
        print("   • Foco em finanças pessoais (solicitado no prompt)")
    
    # Salva comparação
    comparison_result = {
        'timestamp': datetime.now().isoformat(),
        'comparison_type': 'simple_vs_detailed_prompt',
        'simple_prompt': simple_response['query'],
        'detailed_prompt': detailed_response.get('query', 'prompt detalhado'),
        'simple_analysis': simple_analysis,
        'detailed_analysis': detailed_analysis,
        'improvements': {
            'word_count_improvement_pct': round(word_improvement, 1),
            'code_blocks_improvement': code_improvement,
            'features_improvement': detailed_analysis['content_analysis']['feature_count'] - simple_analysis['content_analysis']['feature_count']
        }
    }
    
    with open('rag_prompt_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(comparison_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comparação salva em: rag_prompt_comparison.json")
    print("\n✅ Análise comparativa concluída!")

if __name__ == "__main__":
    compare_responses()