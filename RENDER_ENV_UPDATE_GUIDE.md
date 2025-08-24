# Como Atualizar Variáveis de Ambiente no Render

## Acessando as Configurações do Serviço

1. **Faça login no Render**: Acesse [render.com](https://render.com) e faça login na sua conta

2. **Navegue até seu serviço**: 
   - Vá para o Dashboard
   - Clique no seu serviço `vina-rag-api` (ou o nome que você deu)

3. **Acesse Environment Variables**:
   - No painel do serviço, clique na aba **"Environment"**
   - Ou vá em **Settings** → **Environment**

## Adicionando/Atualizando Variáveis

### Método 1: Interface Web (Recomendado)

1. **Adicionar nova variável**:
   - Clique em **"Add Environment Variable"**
   - Digite o nome da variável (ex: `RAG_API_KEY`)
   - Digite o valor
   - Clique em **"Save Changes"**

2. **Editar variável existente**:
   - Encontre a variável na lista
   - Clique no ícone de edição (lápis)
   - Modifique o valor
   - Clique em **"Save Changes"**

### Método 2: Arquivo .env (Alternativo)

Você pode também definir variáveis no arquivo `render.yaml`:

```yaml
services:
  - type: web
    name: vina-rag-api
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: PORT
        value: 8000
      - key: ENVIRONMENT
        value: production
      # Adicione suas variáveis aqui
```

## Variáveis Essenciais para Adicionar

Baseado no seu `.env.example`, estas são as variáveis mais importantes:

### 🔑 Obrigatórias (Secrets)
```
OPENAI_API_KEY=sk-your-openai-api-key-here
RAG_API_KEY=your-rag-api-key-here
VECTOR_API_KEY=your-vector-api-key

# Novos modelos GPT-5 (disponíveis)
GPT5_FULL_MODEL=gpt-5
GPT5_NANO_MODEL=gpt-5-nano
```

### 🌐 URLs e Conexões
```
VECTOR_URL=https://your-vector-store-url
DB_URL=postgresql://user:password@host:port/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### ⚙️ Configurações de Produção
```
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
WORKERS=1
LOG_LEVEL=info
LOG_FORMAT=json
```

### 🔒 Segurança
```
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
API_RATE_LIMIT=100
API_RATE_WINDOW=60
```

### 📊 Monitoramento
```
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30
PERFORMANCE_MONITORING=true
```

## Dicas Importantes

### 🔐 Variáveis Sensíveis
- **SEMPRE** marque como **"Secret"** variáveis como:
  - `OPENAI_API_KEY`
  - `RAG_API_KEY`
  - `VECTOR_API_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `DB_URL`

### 🔄 Redeploy Automático
- Após salvar as variáveis, o Render fará **redeploy automático**
- Aguarde alguns minutos para o serviço reiniciar
- Monitore os logs durante o redeploy

### 📝 Validação
Após atualizar, teste os endpoints:
```bash
# Health check
curl https://your-app.onrender.com/health

# Teste com autenticação
curl -H "Authorization: Bearer your-rag-api-key" \
     "https://your-app.onrender.com/search?query=test"
```

## Troubleshooting

### ❌ Serviço não inicia após mudanças
1. Verifique os logs no Render Dashboard
2. Confirme que todas as variáveis obrigatórias estão definidas
3. Verifique se não há caracteres especiais mal escapados

### ❌ Erro de autenticação
1. Confirme que `RAG_API_KEY` está definida
2. Verifique se está usando o valor correto no header
3. Teste localmente primeiro

### ❌ Erro de conexão com Vector Store
1. Verifique `VECTOR_URL` e `VECTOR_API_KEY`
2. Teste a conectividade da URL externamente
3. Confirme as credenciais no provedor (Qdrant/Pinecone)

## Próximos Passos

1. ✅ Configure as variáveis essenciais
2. ✅ Teste o health check
3. ✅ Configure Vector Store (Qdrant Cloud ou Pinecone)
4. ✅ Configure banco de dados (Supabase)
5. ✅ Teste endpoints de busca
6. ✅ Configure monitoramento

---

**💡 Dica**: Mantenha uma cópia segura das suas chaves de API em um gerenciador de senhas!