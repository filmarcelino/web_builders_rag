# 🚀 Guia de Integração com o RAG em Produção

## 📍 Informações do Serviço

- **URL Base**: `https://web-builders-rag.onrender.com`
- **Status**: ✅ Online e funcionando
- **Autenticação**: Não requerida (endpoints públicos)
- **Formato**: JSON REST API

## 🔍 Endpoints Disponíveis

### 1. Health Check
```http
GET https://web-builders-rag.onrender.com/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": 6231356.09597254,
  "components": {
    "search_engine": true,
    "metrics": true,
    "logging": true
  }
}
```

### 2. Busca Principal
```http
POST https://web-builders-rag.onrender.com/search
Content-Type: application/json
```

**Payload:**
```json
{
  "query": "sua consulta aqui",
  "top_k": 5,
  "search_type": "hybrid",
  "include_rationale": true,
  "filtros": {
    "stack": "nextjs",
    "categoria": "frontend",
    "min_quality_score": 0.7
  }
}
```

**Parâmetros:**
- `query` (obrigatório): Texto da consulta (1-500 caracteres)
- `top_k` (opcional): Número de resultados (1-20, padrão: 5)
- `search_type` (opcional): Tipo de busca - `vector`, `text`, `hybrid` (padrão: `hybrid`)
- `include_rationale` (opcional): Incluir explicação dos resultados (padrão: `true`)
- `filtros` (opcional): Filtros de busca

**Resposta:**
```json
{
  "results": [
    {
      "chunk": "conteúdo do documento...",
      "fonte": {
        "title": "React Documentation",
        "url": "https://react.dev/hooks"
      },
      "licenca": "MIT",
      "score": 0.85,
      "rationale": "Relevante porque explica useState em detalhes",
      "metadata": {
        "categoria": "frontend",
        "stack": "react"
      }
    }
  ],
  "query_info": {
    "original_query": "React hooks useState",
    "processed_query": "React hooks useState"
  },
  "search_stats": {
    "total_chunks_searched": 1500,
    "vector_results": 10,
    "text_results": 8
  },
  "total_results": 3,
  "search_time_ms": 1250,
  "cached": false
}
```

## 💻 Exemplos de Integração

### JavaScript/Node.js

```javascript
// Usando fetch (nativo)
async function buscarRAG(query, options = {}) {
  const payload = {
    query,
    top_k: options.topK || 5,
    search_type: options.searchType || 'hybrid',
    include_rationale: options.includeRationale !== false,
    filtros: options.filtros || {}
  };

  try {
    const response = await fetch('https://web-builders-rag.onrender.com/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Erro ao buscar no RAG:', error);
    throw error;
  }
}

// Exemplo de uso
const resultados = await buscarRAG('Como criar um componente React com hooks', {
  topK: 3,
  filtros: {
    stack: 'react',
    categoria: 'frontend'
  }
});

console.log('Resultados encontrados:', resultados.total_results);
resultados.results.forEach((resultado, index) => {
  console.log(`${index + 1}. ${resultado.fonte.title}`);
  console.log(`   Score: ${resultado.score}`);
  console.log(`   Rationale: ${resultado.rationale}`);
});
```

### Python

```python
import requests
import json
from typing import Dict, List, Optional

class RAGClient:
    def __init__(self, base_url: str = "https://web-builders-rag.onrender.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def health_check(self) -> Dict:
        """Verifica se o serviço está funcionando"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def search(self, 
               query: str, 
               top_k: int = 5,
               search_type: str = 'hybrid',
               include_rationale: bool = True,
               filtros: Optional[Dict] = None) -> Dict:
        """Realiza busca no RAG"""
        
        payload = {
            'query': query,
            'top_k': top_k,
            'search_type': search_type,
            'include_rationale': include_rationale
        }
        
        if filtros:
            payload['filtros'] = filtros
        
        response = self.session.post(
            f"{self.base_url}/search",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def search_with_context(self, query: str, **kwargs) -> List[str]:
        """Busca e retorna apenas o conteúdo dos chunks"""
        results = self.search(query, **kwargs)
        return [result['chunk'] for result in results['results']]

# Exemplo de uso
if __name__ == "__main__":
    rag = RAGClient()
    
    # Verificar se está funcionando
    health = rag.health_check()
    print(f"Status do RAG: {health['status']}")
    
    # Fazer uma busca
    resultados = rag.search(
        query="Next.js API routes com TypeScript",
        top_k=3,
        filtros={
            'stack': 'nextjs',
            'categoria': 'backend'
        }
    )
    
    print(f"\nEncontrados {resultados['total_results']} resultados:")
    for i, resultado in enumerate(resultados['results'], 1):
        print(f"\n{i}. {resultado['fonte']['title']}")
        print(f"   Score: {resultado['score']:.2f}")
        print(f"   Licença: {resultado['licenca']}")
        print(f"   Rationale: {resultado['rationale']}")
        print(f"   Conteúdo: {resultado['chunk'][:200]}...")
```

### React/TypeScript

```typescript
// types/rag.ts
export interface RAGSearchRequest {
  query: string;
  top_k?: number;
  search_type?: 'vector' | 'text' | 'hybrid';
  include_rationale?: boolean;
  filtros?: {
    stack?: string;
    categoria?: string;
    licenca?: string;
    min_quality_score?: number;
  };
}

export interface RAGResult {
  chunk: string;
  fonte: {
    title: string;
    url: string;
  };
  licenca: string;
  score: number;
  rationale?: string;
  metadata: Record<string, any>;
}

export interface RAGSearchResponse {
  results: RAGResult[];
  query_info: {
    original_query: string;
    processed_query: string;
  };
  search_stats: {
    total_chunks_searched: number;
    vector_results: number;
    text_results: number;
  };
  total_results: number;
  search_time_ms: number;
  cached: boolean;
}

// hooks/useRAG.ts
import { useState, useCallback } from 'react';
import { RAGSearchRequest, RAGSearchResponse } from '../types/rag';

const RAG_BASE_URL = 'https://web-builders-rag.onrender.com';

export const useRAG = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (request: RAGSearchRequest): Promise<RAGSearchResponse | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${RAG_BASE_URL}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: RAGSearchResponse = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      console.error('Erro ao buscar no RAG:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const healthCheck = useCallback(async (): Promise<boolean> => {
    try {
      const response = await fetch(`${RAG_BASE_URL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }, []);

  return {
    search,
    healthCheck,
    loading,
    error,
  };
};

// components/RAGSearch.tsx
import React, { useState } from 'react';
import { useRAG } from '../hooks/useRAG';
import { RAGResult } from '../types/rag';

const RAGSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<RAGResult[]>([]);
  const { search, loading, error } = useRAG();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const response = await search({
      query,
      top_k: 5,
      search_type: 'hybrid',
      filtros: {
        stack: 'react',
        categoria: 'frontend'
      }
    });

    if (response) {
      setResults(response.results);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Busca RAG</h1>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Digite sua consulta..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>
      </form>

      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          Erro: {error}
        </div>
      )}

      <div className="space-y-4">
        {results.map((result, index) => (
          <div key={index} className="p-4 border border-gray-200 rounded-lg">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-lg">{result.fonte.title}</h3>
              <span className="text-sm text-gray-500">Score: {result.score.toFixed(2)}</span>
            </div>
            
            {result.rationale && (
              <p className="text-sm text-blue-600 mb-2 italic">{result.rationale}</p>
            )}
            
            <p className="text-gray-700 mb-2">{result.chunk.substring(0, 300)}...</p>
            
            <div className="flex gap-2 text-xs text-gray-500">
              <span>Licença: {result.licenca}</span>
              {result.fonte.url && (
                <a 
                  href={result.fonte.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:underline"
                >
                  Ver fonte
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RAGSearch;
```

### PHP

```php
<?php

class RAGClient {
    private $baseUrl;
    private $httpClient;
    
    public function __construct($baseUrl = 'https://web-builders-rag.onrender.com') {
        $this->baseUrl = $baseUrl;
        $this->httpClient = curl_init();
        
        curl_setopt_array($this->httpClient, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HEADER => false,
            CURLOPT_TIMEOUT => 30,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'Accept: application/json'
            ]
        ]);
    }
    
    public function healthCheck() {
        curl_setopt($this->httpClient, CURLOPT_URL, $this->baseUrl . '/health');
        curl_setopt($this->httpClient, CURLOPT_HTTPGET, true);
        
        $response = curl_exec($this->httpClient);
        $httpCode = curl_getinfo($this->httpClient, CURLINFO_HTTP_CODE);
        
        if ($httpCode !== 200) {
            throw new Exception("Health check failed with status: $httpCode");
        }
        
        return json_decode($response, true);
    }
    
    public function search($query, $options = []) {
        $payload = [
            'query' => $query,
            'top_k' => $options['top_k'] ?? 5,
            'search_type' => $options['search_type'] ?? 'hybrid',
            'include_rationale' => $options['include_rationale'] ?? true
        ];
        
        if (isset($options['filtros'])) {
            $payload['filtros'] = $options['filtros'];
        }
        
        curl_setopt($this->httpClient, CURLOPT_URL, $this->baseUrl . '/search');
        curl_setopt($this->httpClient, CURLOPT_POST, true);
        curl_setopt($this->httpClient, CURLOPT_POSTFIELDS, json_encode($payload));
        
        $response = curl_exec($this->httpClient);
        $httpCode = curl_getinfo($this->httpClient, CURLINFO_HTTP_CODE);
        
        if ($httpCode !== 200) {
            throw new Exception("Search failed with status: $httpCode");
        }
        
        return json_decode($response, true);
    }
    
    public function __destruct() {
        if ($this->httpClient) {
            curl_close($this->httpClient);
        }
    }
}

// Exemplo de uso
try {
    $rag = new RAGClient();
    
    // Verificar saúde do serviço
    $health = $rag->healthCheck();
    echo "Status do RAG: " . $health['status'] . "\n";
    
    // Fazer busca
    $results = $rag->search('Laravel Eloquent relationships', [
        'top_k' => 3,
        'filtros' => [
            'stack' => 'laravel',
            'categoria' => 'backend'
        ]
    ]);
    
    echo "Encontrados {$results['total_results']} resultados:\n";
    
    foreach ($results['results'] as $index => $result) {
        echo "\n" . ($index + 1) . ". {$result['fonte']['title']}\n";
        echo "   Score: {$result['score']}\n";
        echo "   Rationale: {$result['rationale']}\n";
        echo "   Conteúdo: " . substr($result['chunk'], 0, 200) . "...\n";
    }
    
} catch (Exception $e) {
    echo "Erro: " . $e->getMessage() . "\n";
}

?>
```

## 🔧 Configurações Recomendadas

### Timeout e Retry
- **Timeout**: 30 segundos (o RAG pode demorar alguns segundos para processar)
- **Retry**: Implementar retry com backoff exponencial
- **Cache**: Considere cachear resultados por alguns minutos

### Filtros Úteis
- `stack`: `react`, `nextjs`, `vue`, `angular`, `nodejs`, `python`, `php`
- `categoria`: `frontend`, `backend`, `fullstack`, `devops`, `testing`
- `licenca`: `MIT`, `Apache-2.0`, `BSD-3-Clause`
- `min_quality_score`: 0.7 (para resultados mais relevantes)

### Tratamento de Erros
- **429**: Rate limiting - aguarde antes de tentar novamente
- **500**: Erro interno - tente novamente após alguns segundos
- **0 resultados**: Normal quando não há dados indexados ainda

## 📊 Status Atual

✅ **Serviço Online**: O RAG está funcionando em `https://web-builders-rag.onrender.com`

⚠️ **Dados**: Atualmente retornando 0 resultados pois a ingestão ainda está em andamento

🔄 **Ingestão**: Processo de ingestão dos dados está rodando e deve completar em breve

## 🚀 Próximos Passos

1. **Aguardar Ingestão**: O processo de ingestão está rodando e deve completar em alguns minutos
2. **Testar com Dados**: Após a ingestão, os endpoints retornarão resultados reais
3. **Monitorar Performance**: Acompanhar latência e qualidade dos resultados
4. **Implementar Cache**: Para melhorar performance em produção

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique o endpoint `/health` primeiro
2. Consulte os logs de erro retornados pela API
3. Teste com queries simples antes de usar filtros complexos

---

**Última atualização**: 2 de setembro de 2025
**Versão da API**: 1.0
**Status**: ✅ Operacional