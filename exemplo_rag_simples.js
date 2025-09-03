/**
 * Exemplo Simples de Integração RAG em JavaScript/Node.js
 * URL: https://web-builders-rag.onrender.com
 * 
 * Este exemplo mostra como conectar aplicações JavaScript ao RAG
 * sem dependências externas, usando apenas módulos nativos do Node.js
 */

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

/**
 * Demonstração prática de uso
 */
async function demonstrarIntegracao() {
    console.log('🚀 Demonstração de Integração com RAG Web Builders');
    console.log('=' .repeat(55));
    
    const rag = new RAGClient();
    
    // 1. Health Check
    console.log('\n1️⃣ Verificando status do serviço...');
    const health = await rag.healthCheck();
    
    if (health.status !== 'healthy') {
        console.log('⚠️ Serviço não está saudável, mas continuando...');
    }
    
    // 2. Busca simples sobre React
    console.log('\n2️⃣ Busca sobre React Hooks...');
    const reactResults = await rag.search('Como usar React hooks useState e useEffect');
    
    if (reactResults && reactResults.results && reactResults.results.length > 0) {
        console.log('\n📄 Primeiros resultados:');
        reactResults.results.slice(0, 2).forEach((result, index) => {
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
    
    // 3. Busca com filtros específicos
    console.log('\n3️⃣ Busca com filtros (Node.js + Backend)...');
    const filteredResults = await rag.search('autenticação JWT token', {
        top_k: 3,
        filtros: {
            stack: 'nodejs',
            categoria: 'backend'
        }
    });
    
    if (filteredResults && filteredResults.results) {
        console.log(`✅ Encontrados ${filteredResults.results.length} resultados filtrados`);
        if (filteredResults.results.length > 0) {
            console.log('\n📋 Resultados filtrados:');
            filteredResults.results.forEach((result, index) => {
                console.log(`   ${index + 1}. ${result.fonte?.title || 'N/A'} (Score: ${result.score?.toFixed(2)})`);
            });
        }
    }
    
    // 4. Busca contextual
    console.log('\n4️⃣ Busca contextual...');
    const contextResults = await rag.searchWithContext(
        'Como implementar autenticação?',
        'Desenvolvendo API REST com Node.js e Express'
    );
    
    if (contextResults) {
        console.log('✅ Busca contextual realizada');
        console.log(`Query original: ${contextResults.query_info?.original_query || 'N/A'}`);
        console.log(`Query processada: ${contextResults.query_info?.processed_query || 'N/A'}`);
        
        if (contextResults.search_stats) {
            const stats = contextResults.search_stats;
            console.log('\n📊 Estatísticas da busca:');
            console.log(`   Chunks pesquisados: ${stats.total_chunks_searched || 0}`);
            console.log(`   Resultados vetoriais: ${stats.vector_results || 0}`);
            console.log(`   Resultados textuais: ${stats.text_results || 0}`);
        }
    }
    
    // 5. Teste de diferentes tipos de busca
    console.log('\n5️⃣ Testando diferentes tipos de busca...');
    
    const searchTypes = ['vector', 'text', 'hybrid'];
    const testQuery = 'React components best practices';
    
    for (const searchType of searchTypes) {
        console.log(`\n   🔍 Tipo: ${searchType}`);
        const typeResults = await rag.search(testQuery, {
            search_type: searchType,
            top_k: 2
        });
        
        if (typeResults) {
            console.log(`      Resultados: ${typeResults.total_results || 0}`);
            console.log(`      Tempo: ${typeResults.search_time_ms || 0}ms`);
            console.log(`      Cache: ${typeResults.cached ? 'Sim' : 'Não'}`);
        }
    }
}

/**
 * Exemplo de chatbot simples usando RAG
 */
async function exemplochatbot() {
    console.log('\n🤖 Exemplo de Chatbot com RAG');
    console.log('=' .repeat(35));
    
    const rag = new RAGClient();
    
    // Função para processar pergunta do usuário
    async function processarPergunta(pergunta, contextoUsuario = '') {
        console.log(`\n👤 Usuário: ${pergunta}`);
        
        // Construir query contextual
        let query = pergunta;
        if (contextoUsuario) {
            query = `Contexto do usuário: ${contextoUsuario}\n\nPergunta: ${pergunta}`;
        }
        
        const results = await rag.search(query, {
            top_k: 3,
            include_rationale: true
        });
        
        if (!results || !results.results || results.results.length === 0) {
            console.log('🤖 Bot: Desculpe, não encontrei informações relevantes sobre isso. O sistema ainda está indexando dados.');
            return;
        }
        
        // Construir resposta baseada nos resultados mais relevantes
        const respostasRelevantes = results.results.filter(r => r.score > 0.7);
        
        if (respostasRelevantes.length === 0) {
            console.log('🤖 Bot: Encontrei algumas informações, mas não são muito específicas para sua pergunta.');
            return;
        }
        
        console.log('🤖 Bot: Baseado no que encontrei:');
        
        respostasRelevantes.slice(0, 2).forEach((result, index) => {
            console.log(`\n   📚 Fonte ${index + 1}: ${result.fonte?.title || 'N/A'}`);
            console.log(`   📄 Conteúdo: ${result.chunk?.substring(0, 200)}...`);
            if (result.rationale) {
                console.log(`   💡 Explicação: ${result.rationale}`);
            }
            console.log(`   ⭐ Relevância: ${result.score?.toFixed(2)}`);
        });
    }
    
    // Simular conversação
    const perguntas = [
        { pergunta: 'Como fazer deploy de uma aplicação React?', contexto: 'Desenvolvedor iniciante' },
        { pergunta: 'Qual a diferença entre useState e useEffect?', contexto: 'Aprendendo React hooks' },
        { pergunta: 'Como configurar autenticação JWT?', contexto: 'API Node.js com Express' },
        { pergunta: 'Melhores práticas para CSS?', contexto: 'Frontend moderno' }
    ];
    
    for (const { pergunta, contexto } of perguntas) {
        await processarPergunta(pergunta, contexto);
        
        // Pequena pausa entre perguntas
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}

/**
 * Exemplo de cache simples
 */
class RAGClientComCache extends RAGClient {
    constructor(baseUrl) {
        super(baseUrl);
        this.cache = new Map();
        this.cacheTTL = 5 * 60 * 1000; // 5 minutos
    }
    
    _getCacheKey(query, options = {}) {
        return JSON.stringify({ query, options });
    }
    
    async search(query, options = {}) {
        const cacheKey = this._getCacheKey(query, options);
        const now = Date.now();
        
        // Verificar cache
        if (this.cache.has(cacheKey)) {
            const { data, timestamp } = this.cache.get(cacheKey);
            if (now - timestamp < this.cacheTTL) {
                console.log('💾 Resultado do cache local');
                return data;
            } else {
                this.cache.delete(cacheKey);
            }
        }
        
        // Buscar no RAG
        const result = await super.search(query, options);
        
        // Salvar no cache
        if (result) {
            this.cache.set(cacheKey, { data: result, timestamp: now });
        }
        
        return result;
    }
}

async function exemploCache() {
    console.log('\n💾 Exemplo com Cache Local');
    console.log('=' .repeat(30));
    
    const ragComCache = new RAGClientComCache();
    
    console.log('Primeira busca (vai para o servidor):');
    const start1 = Date.now();
    const result1 = await ragComCache.search('React components best practices');
    const time1 = Date.now() - start1;
    console.log(`Tempo: ${time1}ms`);
    
    console.log('\nSegunda busca (do cache):');
    const start2 = Date.now();
    const result2 = await ragComCache.search('React components best practices');
    const time2 = Date.now() - start2;
    console.log(`Tempo: ${time2}ms`);
    
    if (time2 > 0) {
        console.log(`\n⚡ Aceleração com cache: ${(time1/time2).toFixed(1)}x`);
    }
}

/**
 * Função principal
 */
async function main() {
    try {
        await demonstrarIntegracao();
        await exemplochatbot();
        await exemploCache();
        
        console.log('\n' + '='.repeat(60));
        console.log('✅ Demonstração completa de integração RAG concluída!');
        console.log('\n📋 O que foi demonstrado:');
        console.log('1. ✅ Verificação de saúde do serviço');
        console.log('2. ✅ Busca simples com diferentes queries');
        console.log('3. ✅ Busca com filtros específicos');
        console.log('4. ✅ Busca contextual para melhor relevância');
        console.log('5. ✅ Diferentes tipos de busca (vector, text, hybrid)');
        console.log('6. ✅ Exemplo de chatbot usando RAG');
        console.log('7. ✅ Sistema de cache local para performance');
        
        console.log('\n🔗 Informações importantes:');
        console.log('   URL do RAG: https://web-builders-rag.onrender.com');
        console.log('   Status atual: Serviço online, dados sendo indexados');
        console.log('   Endpoints: /health (GET) e /search (POST)');
        
        console.log('\n💡 Próximos passos:');
        console.log('1. Aguardar indexação completa dos dados');
        console.log('2. Implementar em sua aplicação usando este código');
        console.log('3. Adicionar tratamento de erros robusto');
        console.log('4. Considerar implementar cache para produção');
        
    } catch (error) {
        console.error('❌ Erro durante execução:', error.message);
        console.error('Stack trace:', error.stack);
    }
}

// Executar demonstração
if (require.main === module) {
    main();
}

// Exportar para uso em outros módulos
module.exports = {
    RAGClient,
    RAGClientComCache
};