# 🚀 Como Conectar sua Aplicação ao RAG

**URL do RAG:** `https://web-builders-rag.onrender.com`

## ⚡ Conexão Rápida

### 1. **JavaScript/Node.js** (Mais Simples)

```javascript
// Copie e cole este código em seu projeto
const https = require('https');

class RAGClient {
    constructor() {
        this.baseUrl = 'https://web-builders-rag.onrender.com';
    }

    async search(query, options = {}) {
        const payload = {
            query: query,
            top_k: options.top_k || 5,
            search_type: options.search_type || 'hybrid',
            include_rationale: true
        };

        if (options.filtros) {
            payload.filtros = options.filtros;
        }

        return new Promise((resolve, reject) => {
            const data = JSON.stringify(payload);
            
            const options = {
                hostname: 'web-builders-rag.onrender.com',
                port: 443,
                path: '/search',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': data.length
                }
            };

            const req = https.request(options, (res) => {
                let responseData = '';
                res.on('data', (chunk) => responseData += chunk);
                res.on('end', () => {
                    try {
                        resolve(JSON.parse(responseData));
                    } catch (e) {
                        reject(e);
                    }
                });
            });

            req.on('error', reject);
            req.write(data);
            req.end();
        });
    }
}

// USO:
const rag = new RAGClient();
rag.search('Como criar componentes React').then(results => {
    console.log('Resultados:', results.results);
});
```

### 2. **Python** (Usando requests)

```python
import requests

class RAGClient:
    def __init__(self):
        self.base_url = "https://web-builders-rag.onrender.com"
    
    def search(self, query, top_k=5, filtros=None):
        payload = {
            "query": query,
            "top_k": top_k,
            "search_type": "hybrid",
            "include_rationale": True
        }
        
        if filtros:
            payload["filtros"] = filtros
        
        try:
            response = requests.post(
                f"{self.base_url}/search", 
                json=payload, 
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro: {e}")
            return None

# USO:
rag = RAGClient()
results = rag.search("Como usar React hooks")
if results:
    for result in results['results']:
        print(f"Título: {result['fonte']['title']}")
        print(f"Conteúdo: {result['chunk'][:200]}...")
```

### 3. **Frontend (Fetch API)**

```javascript
// Para usar no browser (React, Vue, etc.)
class RAGClientBrowser {
    constructor() {
        this.baseUrl = 'https://web-builders-rag.onrender.com';
    }

    async search(query, options = {}) {
        const payload = {
            query: query,
            top_k: options.top_k || 5,
            search_type: 'hybrid',
            include_rationale: true,
            filtros: options.filtros
        };

        try {
            const response = await fetch(`${this.baseUrl}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erro na busca:', error);
            return null;
        }
    }
}

// USO EM REACT:
const [results, setResults] = useState([]);
const rag = new RAGClientBrowser();

const handleSearch = async (query) => {
    const response = await rag.search(query);
    if (response) {
        setResults(response.results);
    }
};
```

### 4. **PHP**

```php
<?php
class RAGClient {
    private $baseUrl = 'https://web-builders-rag.onrender.com';
    
    public function search($query, $options = []) {
        $payload = [
            'query' => $query,
            'top_k' => $options['top_k'] ?? 5,
            'search_type' => 'hybrid',
            'include_rationale' => true
        ];
        
        if (isset($options['filtros'])) {
            $payload['filtros'] = $options['filtros'];
        }
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $this->baseUrl . '/search',
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($payload),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json'
            ],
            CURLOPT_TIMEOUT => 30
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200) {
            return json_decode($response, true);
        }
        
        return null;
    }
}

// USO:
$rag = new RAGClient();
$results = $rag->search('Laravel Eloquent relationships');
if ($results) {
    foreach ($results['results'] as $result) {
        echo $result['fonte']['title'] . "\n";
        echo substr($result['chunk'], 0, 200) . "...\n\n";
    }
}
?>
```

## 🎯 Exemplos de Uso Prático

### Chatbot Simples

```javascript
const rag = new RAGClient();

async function chatbot(pergunta, contexto = '') {
    const query = contexto ? 
        `Contexto: ${contexto}\nPergunta: ${pergunta}` : 
        pergunta;
    
    const results = await rag.search(query, { top_k: 3 });
    
    if (!results || results.total_results === 0) {
        return "Desculpe, não encontrei informações sobre isso.";
    }
    
    const melhorResultado = results.results[0];
    return `Baseado em ${melhorResultado.fonte.title}: ${melhorResultado.chunk.substring(0, 300)}...`;
}

// Uso:
chatbot("Como fazer deploy no Vercel?", "Projeto Next.js")
    .then(resposta => console.log(resposta));
```

### Sistema de Busca com Filtros

```javascript
// Buscar conteúdo específico por tecnologia
const buscarPorStack = async (query, stack) => {
    return await rag.search(query, {
        filtros: {
            stack: stack,  // 'react', 'nodejs', 'python', etc.
            categoria: 'frontend'  // 'backend', 'fullstack', etc.
        }
    });
};

// Exemplos:
buscarPorStack("autenticação", "nodejs");  // Busca sobre auth em Node.js
buscarPorStack("componentes", "react");    // Busca sobre componentes React
```

## 📊 Estrutura da Resposta

```json
{
  "results": [
    {
      "chunk": "Conteúdo do resultado...",
      "score": 0.85,
      "fonte": {
        "title": "Título do documento",
        "url": "https://exemplo.com"
      },
      "licenca": "MIT",
      "rationale": "Explicação de por que este resultado é relevante"
    }
  ],
  "query_info": {
    "original_query": "Sua pergunta original",
    "processed_query": "Query processada pelo sistema"
  },
  "total_results": 5,
  "search_time_ms": 234,
  "cached": false
}
```

## 🔧 Filtros Disponíveis

```javascript
const filtros = {
    stack: 'react',           // react, nextjs, vue, nodejs, python, php
    categoria: 'frontend',    // frontend, backend, fullstack, devops
    licenca: 'MIT',          // MIT, Apache-2.0, BSD-3-Clause
    min_quality_score: 0.7   // Mínimo de relevância (0.0 a 1.0)
};
```

## ⚡ Dicas de Performance

### 1. **Cache Local**

```javascript
class RAGClientComCache extends RAGClient {
    constructor() {
        super();
        this.cache = new Map();
        this.cacheTTL = 5 * 60 * 1000; // 5 minutos
    }
    
    async search(query, options = {}) {
        const cacheKey = JSON.stringify({ query, options });
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
            return cached.data;
        }
        
        const result = await super.search(query, options);
        if (result) {
            this.cache.set(cacheKey, {
                data: result,
                timestamp: Date.now()
            });
        }
        
        return result;
    }
}
```

### 2. **Timeout e Retry**

```javascript
class RAGClientRobust extends RAGClient {
    async searchWithRetry(query, options = {}, maxRetries = 3) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await this.search(query, options);
            } catch (error) {
                if (i === maxRetries - 1) throw error;
                await new Promise(resolve => 
                    setTimeout(resolve, Math.pow(2, i) * 1000)
                );
            }
        }
    }
}
```

## 🚨 Status Atual

- ✅ **Serviço Online**: `https://web-builders-rag.onrender.com`
- ⚠️ **Dados**: Retornando 0 resultados (indexação em andamento)
- 🔄 **Indexação**: Processo ativo, deve completar em breve
- 📡 **Endpoints**: `/health` (GET) e `/search` (POST)

## 🔍 Testando a Conexão

### Verificar se está funcionando:

```bash
# Teste rápido via curl
curl -X GET https://web-builders-rag.onrender.com/health

# Teste de busca
curl -X POST https://web-builders-rag.onrender.com/search \
  -H "Content-Type: application/json" \
  -d '{"query": "React hooks", "top_k": 3}'
```

### Verificar no código:

```javascript
// Teste de conectividade
const rag = new RAGClient();

// 1. Health check
fetch('https://web-builders-rag.onrender.com/health')
    .then(res => res.json())
    .then(data => console.log('Status:', data.status));

// 2. Busca de teste
rag.search('test query')
    .then(results => {
        console.log('Conectado! Resultados:', results.total_results);
    })
    .catch(error => {
        console.error('Erro de conexão:', error);
    });
```

## 📞 Troubleshooting

### Problemas Comuns:

1. **0 resultados**: Normal, dados ainda sendo indexados
2. **Timeout**: Aumentar timeout para 30+ segundos
3. **CORS**: Adicionar headers apropriados no frontend
4. **Rate limiting**: Implementar delay entre requisições

### Códigos de Erro:

- **200**: Sucesso
- **400**: Query inválida
- **429**: Muitas requisições
- **500**: Erro interno (tente novamente)

---

**🎉 Pronto! Agora você pode conectar qualquer aplicação ao RAG usando estes exemplos.**

**📚 Documentação completa:** `GUIA_INTEGRACAO_RAG.md`
**🔗 URL do RAG:** `https://web-builders-rag.onrender.com`