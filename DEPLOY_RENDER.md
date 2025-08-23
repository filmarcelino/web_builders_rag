# 🚀 Deploy do Sistema RAG no Render.com

Guia completo para fazer deploy do Sistema RAG (Retrieval-Augmented Generation) no Render.com.

## 📋 Pré-requisitos

- Conta no [Render.com](https://render.com)
- Repositório Git com o código
- Chave da API OpenAI
- Python 3.11+

## 🔧 Configuração Rápida

### 1. Preparar o Repositório

```bash
# Fazer commit de todos os arquivos
git add .
git commit -m "Preparar para deploy no Render"
git push origin main
```

### 2. Criar Serviço no Render

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório Git
4. Configure:
   - **Name**: `vina-rag-api`
   - **Environment**: `Python 3`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

### 3. Configurar Variáveis de Ambiente

No painel do Render, adicione estas variáveis:

```env
# OBRIGATÓRIAS
OPENAI_API_KEY=sk-your-openai-api-key-here
PORT=8000
ENVIRONMENT=production

# OPCIONAIS (com valores padrão)
HOST=0.0.0.0
WORKERS=1
LOG_LEVEL=info
PYTHONPATH=/opt/render/project/src
MAX_SEARCH_RESULTS=50
SEARCH_TIMEOUT=30
```

### 4. Configurar Health Check

- **Health Check Path**: `/health`
- **Health Check Timeout**: `30 seconds`

## 📁 Estrutura de Arquivos para Deploy

```
vina_base_agent/
├── main.py                 # Ponto de entrada principal
├── requirements.txt        # Dependências Python
├── Dockerfile             # Container Docker
├── render.yaml            # Configuração Render
├── start.sh               # Script de inicialização
├── .env.example           # Exemplo de variáveis
├── .dockerignore          # Arquivos ignorados no Docker
├── src/                   # Código fonte
├── config/                # Configurações
└── data/                  # Dados (será criado automaticamente)
```

## 🔍 Endpoints Disponíveis

Após o deploy, sua API estará disponível em:

- **Base URL**: `https://vina-rag-api.onrender.com`
- **Health Check**: `/health`
- **Busca**: `/search?query=sua-busca`
- **Métricas**: `/metrics`
- **Status**: `/status`
- **Documentação**: `/docs`

## 🧪 Testando o Deploy

### 1. Verificar Saúde
```bash
curl https://vina-rag-api.onrender.com/health
```

### 2. Testar Busca
```bash
curl "https://vina-rag-api.onrender.com/search?query=animation&limit=5"
```

### 3. Verificar Status
```bash
curl https://vina-rag-api.onrender.com/status
```

## 📊 Monitoramento

### Logs do Render
- Acesse o painel do serviço
- Vá para a aba "Logs"
- Monitore inicialização e erros

### Métricas Personalizadas
```bash
curl https://vina-rag-api.onrender.com/metrics
```

## ⚡ Otimizações de Performance

### 1. Configurações de Produção
- **Workers**: 1 (Render Starter Plan)
- **Memory**: 512MB
- **CPU**: Compartilhado
- **Timeout**: 30s

### 2. Cache e Persistência
- Dados são armazenados em disco persistente
- Cache em memória para consultas frequentes
- Backup automático configurado

## 🔒 Segurança

### Variáveis Sensíveis
- ✅ `OPENAI_API_KEY` configurada como variável de ambiente
- ✅ CORS configurado para produção
- ✅ Rate limiting implementado
- ✅ Logs não expõem informações sensíveis

### Headers de Segurança
- HTTPS automático no Render
- Headers de segurança configurados
- Validação de entrada implementada

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Erro de Inicialização
```
❌ Erro: ModuleNotFoundError
```
**Solução**: Verificar `requirements.txt` e `PYTHONPATH`

#### 2. API Key Inválida
```
❌ Erro: OpenAI API key not found
```
**Solução**: Configurar `OPENAI_API_KEY` no painel do Render

#### 3. Timeout na Inicialização
```
❌ Erro: Health check failed
```
**Solução**: Aumentar timeout ou otimizar inicialização

#### 4. Erro de Memória
```
❌ Erro: Out of memory
```
**Solução**: Otimizar uso de memória ou upgrade do plano

### Logs Úteis
```bash
# Ver logs em tempo real
render logs --service vina-rag-api --follow

# Ver logs específicos
render logs --service vina-rag-api --since 1h
```

## 🔄 Atualizações e Deploy Contínuo

### Auto Deploy
- Configurado para deploy automático no push para `main`
- Build time: ~3-5 minutos
- Zero downtime deployment

### Deploy Manual
```bash
# Trigger manual deploy
render deploy --service vina-rag-api
```

## 💰 Custos Estimados

### Render Starter Plan
- **Custo**: $7/mês
- **Recursos**: 512MB RAM, CPU compartilhado
- **Bandwidth**: 100GB/mês
- **Builds**: Ilimitados

### Uso da OpenAI API
- **GPT-4**: ~$0.03 por 1K tokens
- **Embeddings**: ~$0.0001 por 1K tokens
- **Estimativa**: $10-50/mês (dependendo do uso)

## 📞 Suporte

### Recursos
- [Documentação Render](https://render.com/docs)
- [Status Render](https://status.render.com)
- [Comunidade Render](https://community.render.com)

### Contato
- Issues no repositório Git
- Logs detalhados no painel do Render
- Métricas em tempo real via `/metrics`

---

## ✅ Checklist de Deploy

- [ ] Repositório Git configurado
- [ ] `requirements.txt` atualizado
- [ ] `OPENAI_API_KEY` configurada
- [ ] Serviço criado no Render
- [ ] Variáveis de ambiente configuradas
- [ ] Health check funcionando
- [ ] Endpoints testados
- [ ] Logs monitorados
- [ ] Métricas verificadas
- [ ] Documentação acessível

🎉 **Parabéns! Seu Sistema RAG está rodando em produção!**