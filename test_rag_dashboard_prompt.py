#!/usr/bin/env python3
"""
Teste do RAG com prompt: "crie um dashboard financeiro"
Este script demonstra como o sistema RAG responde a prompts específicos
utilizando os dados indexados.
"""

import os
import sys
import json
import faiss
import numpy as np
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração
RAG_DATA_DIR = "rag_data"
FAISS_INDEX_PATH = os.path.join(RAG_DATA_DIR, "faiss_index.bin")
METADATA_PATH = os.path.join(RAG_DATA_DIR, "chunk_metadata.json")

class RAGTester:
    def __init__(self):
        # Usar a chave OpenAI correta do .env
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")
        self.client = OpenAI(api_key=openai_key)
        self.index = None
        self.metadata = []
        
    def load_rag_data(self):
        """Carrega o índice FAISS e metadados"""
        print("🔄 Carregando dados do RAG...")
        
        # Carregar índice FAISS
        if os.path.exists(FAISS_INDEX_PATH):
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            print(f"✅ Índice FAISS carregado: {self.index.ntotal} vetores")
        else:
            print("❌ Índice FAISS não encontrado")
            return False
            
        # Carregar metadados
        if os.path.exists(METADATA_PATH):
            try:
                with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f"✅ Metadados carregados: {len(self.metadata)} chunks")
            except Exception as e:
                print(f"⚠️ Erro ao carregar metadados: {e}")
                self.metadata = []
        else:
            print("❌ Arquivo de metadados não encontrado")
            
        return True
        
    def get_embedding(self, text):
        """Gera embedding para o texto"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            print(f"❌ Erro ao gerar embedding: {e}")
            return None
            
    def search_similar_chunks(self, query, top_k=5):
        """Busca chunks similares no índice FAISS"""
        if not self.index:
            return []
            
        # Gerar embedding da query
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            return []
            
        # Buscar no índice
        query_embedding = query_embedding.reshape(1, -1)
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Recuperar chunks relevantes
        relevant_chunks = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.metadata):
                chunk_data = self.metadata[idx].copy()
                chunk_data['similarity_score'] = float(score)
                chunk_data['rank'] = i + 1
                relevant_chunks.append(chunk_data)
                
        return relevant_chunks
        
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
Se as informações não forem suficientes, indique claramente essa limitação.
Sempre cite as fontes quando possível.
"""
        
        user_prompt = f"""
Contexto disponível:
{context}

---

Pergunta: {query}

Por favor, responda baseando-se exclusivamente no contexto fornecido.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Erro ao gerar resposta: {e}"
            
    def test_dashboard_prompt(self):
        """Testa o prompt específico sobre dashboard financeiro"""
        query = "crie um dashboard financeiro"
        
        print(f"\n🎯 Testando prompt: '{query}'")
        print("=" * 60)
        
        # Buscar chunks relevantes
        print("\n🔍 Buscando chunks relevantes...")
        relevant_chunks = self.search_similar_chunks(query, top_k=5)
        
        if not relevant_chunks:
            print("❌ Nenhum chunk relevante encontrado")
            return
            
        # Mostrar chunks encontrados
        print(f"\n📋 Chunks encontrados ({len(relevant_chunks)}):")
        for chunk in relevant_chunks:
            source = chunk.get('source', 'Desconhecido')[:50]
            score = chunk.get('similarity_score', 0)
            rank = chunk.get('rank', 0)
            content_preview = chunk.get('content', '')[:100].replace('\n', ' ')
            print(f"  {rank}. [{source}...] (Score: {score:.4f})")
            print(f"     Preview: {content_preview}...")
            
        # Gerar resposta RAG
        print("\n🤖 Gerando resposta RAG...")
        rag_response = self.generate_rag_response(query, relevant_chunks)
        
        # Mostrar resposta
        print("\n📝 RESPOSTA DO RAG:")
        print("-" * 40)
        print(rag_response)
        print("-" * 40)
        
        # Salvar resultado
        result = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "relevant_chunks_count": len(relevant_chunks),
            "relevant_chunks": relevant_chunks,
            "rag_response": rag_response
        }
        
        with open("test_dashboard_prompt_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Resultado salvo em: test_dashboard_prompt_result.json")
        
def main():
    print("🧪 Teste do RAG - Prompt Dashboard Financeiro")
    print("=" * 60)
    
    # Verificar se os dados RAG existem
    if not os.path.exists(FAISS_INDEX_PATH):
        print("❌ Dados do RAG não encontrados. Execute a ingestão primeiro.")
        return
        
    # Inicializar tester
    tester = RAGTester()
    
    # Carregar dados
    if not tester.load_rag_data():
        print("❌ Falha ao carregar dados do RAG")
        return
        
    # Executar teste
    tester.test_dashboard_prompt()
    
    print("\n✅ Teste concluído!")
    
if __name__ == "__main__":
    main()