# 🚀 Guia Completo de Deploy no Render

## Pré-requisitos

✅ **Aplicação preparada para contêiner**
- Dockerfile configurado
- Endpoint `/health` implementado
- Variáveis de ambiente configuradas
- Autenticação Bearer implementada
- Rate limiting configurado

## Passo 1: Criar conta no Render

1. Acesse [render.com](https://render.com)
2. Crie uma conta ou faça login
3. Conecte sua conta GitHub/GitLab

## Passo 2: Criar Web Service

1. No dashboard do Render, clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: `vina-rag-api`
   - **Environment**: `Docker`
   - **Region**: `Oregon` (mais barato)
   - **Branch**: `main`
   - **Plan**: `Starter` ($7/mês)

## Passo 3: Configurar Variáveis de Ambiente

No painel do Render, vá em "Environment" e adicione:

### 🔑 Chaves de API (OBRIGATÓRIAS)
```
RAG_API_KEY=sua-chave-rag-secreta-aqui
OPENAI_API_KEY=sk-sua-chave-openai-aqui
VECTOR_API_KEY=sua-chave-vector-store
```

### 🗄️ URLs de Serviços
```
VECTOR_URL=https://sua-instancia-qdrant.com
DB_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua-service-role-key
```

### ⚙️ Configurações (já definidas no render.yaml)
```
ENVIRONMENT=production
PORT=8000
LOG_LEVEL=info
CORS_ORIGINS=*
API_RATE_LIMIT=60
```

## Passo 4: Deploy

1. Clique em "Create Web Service"
2. O Render fará o build automaticamente
3. Aguarde o status ficar "Live" (5-10 minutos)

## Passo 5: Verificar Deploy

### ✅ Testes básicos
```bash
# Health check
curl https://sua-app.onrender.com/health

# Teste de autenticação (deve retornar 401)
curl https://sua-app.onrender.com/search

# Teste com autenticação
curl -H "Authorization: Bearer SUA_RAG_API_KEY" \
     "https://sua-app.onrender.com/search?query=test"
```

### 📊 Endpoints disponíveis
- `GET /health` - Health check (público)
- `GET /` - Informações da API (público)
- `GET /docs` - Documentação Swagger (público)
- `POST /search` - Busca principal (autenticado)
- `GET /metrics` - Métricas do sistema (autenticado)
- `GET /status` - Status detalhado (público)

## Passo 6: Configurar Vector Store

### Opção A: Qdrant Cloud
1. Acesse [cloud.qdrant.io](https://cloud.qdrant.io)
2. Crie um cluster gratuito
3. Copie a URL e API Key
4. Configure no Render:
   ```
   VECTOR_URL=https://xyz.eu-central.aws.cloud.qdrant.io:6333
   VECTOR_API_KEY=sua-api-key
   ```

### Opção B: Pinecone
1. Acesse [pinecone.io](https://pinecone.io)
2. Crie um índice
3. Configure no Render:
   ```
   VECTOR_URL=https://seu-index.svc.environment.pinecone.io
   VECTOR_API_KEY=sua-api-key
   ```

## Passo 7: Configurar Jobs (Opcional)

Para ingestão automática:

1. Crie um "Background Worker" no Render
2. Use a mesma imagem Docker
3. Configure Cron Jobs:
   - **Semanal**: `0 2 * * 0` (domingo 2h)
   - **Mensal**: `0 2 1 * *` (dia 1, 2h)

## Passo 8: Monitoramento

### 📈 Métricas no Render
- CPU/RAM usage
- Response times
- Error rates
- Request volume

### 🔍 Logs
```bash
# Ver logs em tempo real
render logs --service=vina-rag-api --follow
```

## Passo 9: Domínio Customizado (Opcional)

1. No painel do Render, vá em "Settings" > "Custom Domains"
2. Adicione seu domínio: `rag.seudominio.com`
3. Configure DNS CNAME apontando para `sua-app.onrender.com`
4. SSL será configurado automaticamente

## 🚨 Troubleshooting

### Build falha
- Verifique se `requirements.txt` está correto
- Confirme que `faiss-cpu` está incluído
- Verifique logs de build no Render

### App não inicia
- Verifique variáveis de ambiente obrigatórias
- Confirme que porta 8000 está sendo usada
- Verifique logs de runtime

### Erro 503 no /health
- Componentes não inicializaram corretamente
- Verifique conexão com vector store
- Verifique chaves de API

### Rate limit muito restritivo
- Ajuste `API_RATE_LIMIT` no Render
- Considere usar Redis para rate limiting em produção

## 💰 Custos Estimados

- **Render Starter**: $7/mês
- **Qdrant Cloud Free**: $0/mês (1GB)
- **Supabase Free**: $0/mês (500MB)
- **Total mínimo**: ~$7/mês

## 🔄 Atualizações

Para atualizar a aplicação:
1. Faça push para a branch `main`
2. Render fará deploy automático
3. Ou desabilite auto-deploy e faça deploy manual

## 📞 Suporte

Em caso de problemas:
1. Verifique logs no painel do Render
2. Teste endpoints localmente primeiro
3. Confirme todas as variáveis de ambiente
4. Verifique status dos serviços externos (Qdrant, Supabase)

---

**✅ Checklist final:**
- [ ] App rodando em https://sua-app.onrender.com
- [ ] Health check retorna 200
- [ ] Autenticação funcionando (401 sem token)
- [ ] Busca funcionando com token válido
- [ ] Vector store conectado
- [ ] Logs estruturados visíveis
- [ ] Rate limiting ativo
- [ ] SSL configurado automaticamente