/**
 * Exemplo de Integração RAG em JavaScript/Node.js
 * URL: https://web-builders-rag.onrender.com
 * 
 * Este exemplo mostra como conectar aplicações JavaScript ao RAG
 * tanto no frontend (browser) quanto no backend (Node.js)
 */

// ============================================================================
// VERSÃO PARA NODE.JS (Backend)
// ============================================================================

const https = require('https');
const http = require('http');

class RAGClient {
    constructor(baseUrl = 'https://web-builders-rag.onrender.com') {
        this.baseUrl = baseUrl;
        this.timeout = 30000; // 30 segundos
    }

    /**
     * Faz requisição HTTP/HTTPS
     */
    async makeRequest(path, method = 'GET', data = null) {
        return new Promise((resolve, reject) => {
            const url = new URL(this.baseUrl + path);
            const isHttps = url.protocol === 'https:';
            const client = isHttps ? https : http;
            
            const options = {
                hostname: url.hostname,
                port: url.port || (isHttps ? 443 : 80),
                path: url.pathname + url.search,
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'User-Agent': 'RAG-Client-JS/1.0'
                },
                timeout: this.timeout
            };

            if (data && method !== 'GET') {
                const jsonData = JSON.stringify(data);
                options.headers['Content-Length'] = Buffer.byteLength(jsonData);
            }

            const req = client.request(options, (res) => {
                let responseData = '';
                
                res.on('data', (chunk) => {
                    responseData += chunk;
                });
                
                res.on('end', () => {
                    try {
                        const jsonResponse = JSON.parse(responseData);
                        if (res.statusCode >= 200 && res.statusCode < 300) {
                            resolve(jsonResponse);
                        } else {
                            reject(new Error(`HTTP ${res.statusCode}: ${jsonResponse.message || responseData}`));
                        }
                    } catch (e) {
                        if (res.statusCode >= 200 && res.statusCode < 300) {
                            resolve(responseData);
                        } else {
                            reject(new Error(`HTTP ${res.statusCode}: ${responseData}`));
                        }
                    }
                });
            });

            req.on('error', reject);
            req.on('timeout', () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });

            if (data && method !== 'GET') {
                req.write(JSON.stringify(data));
            }
            
            req.end();
        });
    }

    /**
     * Verifica saúde do serviço
     */
    async healthCheck() {
        try {
            const response = await this.makeRequest('/health');
            console.log('✅ RAG Service Status:', response.status);
            return response;
        } catch (error) {
            console.error('❌ Health check failed:', error.message);
            return { status: 'error', message: error.message };
        }
    }

    /**
     * Realiza busca no RAG
     */
    async search(query, options = {}) {
        const payload = {
            query: query,
            top_k: options.top_k || 5,
            search_type: options.search_type || 'hybrid',
            include_rationale: options.include_rationale !== false
        };

        if (options.filtros) {
            payload.filtros = options.filtros;
        }

        try {
            console.log(`🔍 Searching: "${query}"...`);
            const startTime = Date.now();
            
            const response = await this.makeRequest('/search', 'POST', payload);
            
            const duration = Date.now() - startTime;
            console.log(`✅ Found ${response.total_results || 0} results in ${duration}ms`);
            
            return response;
        } catch (error) {
            console.error('❌ Search failed:', error.message);
            return null;
        }
    }

    /**
     * Busca com contexto específico
     */
    async searchWithContext(query, context) {
        const enhancedQuery = `Contexto: ${context}\n\nPergunta: ${query}`;
        return await this.search(enhancedQuery, { top_k: 3 });
    }
}

// ============================================================================
// VERSÃO PARA BROWSER (Frontend)
// ============================================================================

class RAGClientBrowser {
    constructor(baseUrl = 'https://web-builders-rag.onrender.com') {
        this.baseUrl = baseUrl;
    }

    /**
     * Verifica saúde do serviço
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ RAG Service Status:', data.status);
            return data;
        } catch (error) {
            console.error('❌ Health check failed:', error.message);
            return { status: 'error', message: error.message };
        }
    }

    /**
     * Realiza busca no RAG
     */
    async search(query, options = {}) {
        const payload = {
            query: query,
            top_k: options.top_k || 5,
            search_type: options.search_type || 'hybrid',
            include_rationale: options.include_rationale !== false
        };

        if (options.filtros) {
            payload.filtros = options.filtros;
        }

        try {
            console.log(`🔍 Searching: "${query}"...`);
            
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

            const data = await response.json();
            console.log(`✅ Found ${data.total_results || 0} results in ${data.search_time_ms || 0}ms`);
            
            return data;
        } catch (error) {
            console.error('❌ Search failed:', error.message);
            return null;
        }
    }

    /**
     * Busca com contexto específico
     */
    async searchWithContext(query, context) {
        const enhancedQuery = `Contexto: ${context}\n\nPergunta: ${query}`;
        return await this.search(enhancedQuery, { top_k: 3 });
    }
}

// ============================================================================
// EXEMPLOS DE USO
// ============================================================================

/**
 * Exemplo para Node.js
 */
async function exemploNodeJS() {
    console.log('🚀 Exemplo Node.js - Integração com RAG');
    console.log('=' .repeat(50));
    
    const rag = new RAGClient();
    
    // 1. Health Check
    console.log('\n1️⃣ Verificando status do serviço...');
    await rag.healthCheck();
    
    // 2. Busca simples
    console.log('\n2️⃣ Busca sobre React Hooks...');
    const results = await rag.search('Como usar React hooks useState e useEffect');
    
    if (results && results.results && results.results.length > 0) {
        console.log('\n📄 Primeiros resultados:');
        results.results.slice(0, 2).forEach((result, index) => {
            console.log(`\n   ${index + 1}. ${result.fonte?.title || 'N/A'}`);
            console.log(`      Score: ${result.score?.toFixed(2)}`);
            console.log(`      Conteúdo: ${result.chunk?.substring(0, 150)}...`);
            if (result.rationale) {
                console.log(`      Explicação: ${result.rationale}`);
            }
        });
    } else {
        console.log('❌ Nenhum resultado encontrado (dados ainda sendo indexados)');
    }
    
    // 3. Busca com filtros
    console.log('\n3️⃣ Busca com filtros...');
    const filteredResults = await rag.search('autenticação JWT', {
        top_k: 3,
        filtros: {
            stack: 'nodejs',
            categoria: 'backend'
        }
    });
    
    if (filteredResults && filteredResults.results) {
        console.log(`✅ Encontrados ${filteredResults.results.length} resultados filtrados`);
    }
    
    // 4. Busca contextual
    console.log('\n4️⃣ Busca contextual...');
    const contextResults = await rag.searchWithContext(
        'Como implementar autenticação?',
        'Desenvolvendo API REST com Express.js'
    );
    
    if (contextResults) {
        console.log('✅ Busca contextual realizada');
        console.log(`Query processada: ${contextResults.query_info?.processed_query || 'N/A'}`);
    }
}

/**
 * Exemplo de integração em aplicação Express.js
 */
function exemploExpressApp() {
    console.log('\n🌐 Exemplo Express.js - API com RAG');
    console.log('=' .repeat(40));
    
    // Simulação de rotas Express
    const express = require('express');
    const app = express();
    const rag = new RAGClient();
    
    app.use(express.json());
    
    // Rota para busca no RAG
    app.post('/api/search', async (req, res) => {
        try {
            const { query, context, filters } = req.body;
            
            if (!query) {
                return res.status(400).json({ error: 'Query é obrigatória' });
            }
            
            let searchQuery = query;
            if (context) {
                searchQuery = `Contexto: ${context}\n\nPergunta: ${query}`;
            }
            
            const results = await rag.search(searchQuery, {
                top_k: req.body.top_k || 5,
                filtros: filters
            });
            
            if (!results) {
                return res.status(500).json({ error: 'Erro na busca RAG' });
            }
            
            // Processar resultados para resposta mais limpa
            const processedResults = results.results?.map(result => ({
                title: result.fonte?.title,
                content: result.chunk,
                score: result.score,
                rationale: result.rationale,
                source_url: result.fonte?.url,
                license: result.licenca
            })) || [];
            
            res.json({
                query: results.query_info?.original_query,
                results: processedResults,
                total: results.total_results,
                search_time: results.search_time_ms
            });
            
        } catch (error) {
            console.error('Erro na rota /api/search:', error);
            res.status(500).json({ error: 'Erro interno do servidor' });
        }
    });
    
    // Rota para health check
    app.get('/api/rag/health', async (req, res) => {
        const health = await rag.healthCheck();
        res.json(health);
    });
    
    console.log('📋 Rotas disponíveis:');
    console.log('   POST /api/search - Buscar no RAG');
    console.log('   GET /api/rag/health - Status do RAG');
    console.log('\n💡 Exemplo de uso:');
    console.log('   curl -X POST http://localhost:3000/api/search \\');
    console.log('        -H "Content-Type: application/json" \\');
    console.log('        -d \'{ "query": "React hooks", "context": "iniciante" }\'');
    
    return app;
}

/**
 * Exemplo de componente React (para copiar no frontend)
 */
function exemploReactComponent() {
    console.log('\n⚛️ Exemplo React Component');
    console.log('=' .repeat(30));
    
    const reactCode = `
// RAGSearch.jsx
import React, { useState, useCallback } from 'react';

const RAGSearch = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const rag = new RAGClientBrowser();
    
    const handleSearch = useCallback(async (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await rag.search(query, {
                top_k: 5,
                filtros: {
                    stack: 'react',
                    categoria: 'frontend'
                }
            });
            
            if (response && response.results) {
                setResults(response.results);
            } else {
                setError('Nenhum resultado encontrado');
            }
        } catch (err) {
            setError('Erro na busca: ' + err.message);
        } finally {
            setLoading(false);
        }
    }, [query]);
    
    return (
        <div className="max-w-4xl mx-auto p-6">
            <h1 className="text-2xl font-bold mb-6">Busca RAG</h1>
            
            <form onSubmit={handleSearch} className="mb-6">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Digite sua pergunta..."
                        className="flex-1 px-4 py-2 border rounded-lg"
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
                    {error}
                </div>
            )}
            
            <div className="space-y-4">
                {results.map((result, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                            <h3 className="font-semibold">{result.fonte?.title || 'Sem título'}</h3>
                            <span className="text-sm text-gray-500">Score: {result.score?.toFixed(2)}</span>
                        </div>
                        
                        {result.rationale && (
                            <p className="text-sm text-blue-600 mb-2 italic">{result.rationale}</p>
                        )}
                        
                        <p className="text-gray-700 mb-2">{result.chunk?.substring(0, 300)}...</p>
                        
                        <div className="flex gap-2 text-xs text-gray-500">
                            <span>Licença: {result.licenca}</span>
                            {result.fonte?.url && (
                                <a href={result.fonte.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
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
`;
    
    console.log('📋 Código React para copiar:');
    console.log(reactCode);
}

// ============================================================================
// EXECUÇÃO DOS EXEMPLOS
// ============================================================================

async function main() {
    try {
        // Detectar ambiente
        const isNode = typeof window === 'undefined';
        
        if (isNode) {
            console.log('🟢 Executando em Node.js');
            await exemploNodeJS();
            exemploExpressApp();
        } else {
            console.log('🌐 Executando no Browser');
            // No browser, usar RAGClientBrowser
        }
        
        exemploReactComponent();
        
        console.log('\n' + '='.repeat(50));
        console.log('✅ Exemplos de integração concluídos!');
        console.log('\n📋 Resumo das integrações:');
        console.log('1. ✅ Cliente Node.js com requisições nativas');
        console.log('2. ✅ Cliente Browser com Fetch API');
        console.log('3. ✅ Integração Express.js para APIs');
        console.log('4. ✅ Componente React para frontend');
        console.log('\n🔗 URL do RAG: https://web-builders-rag.onrender.com');
        console.log('📚 Documentação: GUIA_INTEGRACAO_RAG.md');
        
    } catch (error) {
        console.error('❌ Erro durante execução:', error);
    }
}

// Executar se for Node.js
if (typeof window === 'undefined') {
    main();
}

// Exportar para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        RAGClient,
        RAGClientBrowser
    };
}