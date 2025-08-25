import faiss
import numpy as np
import os

def check_faiss_index():
    index_file = 'rag_data/faiss_index.bin'
    
    print("=== Verificação do Índice FAISS ===")
    
    if not os.path.exists(index_file):
        print("✗ Arquivo do índice FAISS não encontrado")
        return
    
    try:
        # Carregar o índice FAISS
        index = faiss.read_index(index_file)
        
        print(f"✓ Índice FAISS carregado com sucesso")
        print(f"✓ Número total de vetores no índice: {index.ntotal:,}")
        print(f"✓ Dimensão dos vetores: {index.d}")
        
        # Verificar o tipo do índice
        print(f"✓ Tipo do índice: {type(index).__name__}")
        
        # Estimar o progresso baseado no tamanho do arquivo
        file_size = os.path.getsize(index_file)
        print(f"✓ Tamanho do arquivo: {file_size:,} bytes")
        
        # Calcular estimativa de chunks processados
        # Assumindo que cada vetor tem ~1536 dimensões (OpenAI) e 4 bytes por float
        estimated_vector_size = index.d * 4  # 4 bytes por float32
        estimated_vectors = file_size // estimated_vector_size
        
        print(f"✓ Estimativa baseada no tamanho: ~{estimated_vectors:,} vetores")
        
        if index.ntotal > 0:
            print(f"\n🎯 PROGRESSO: {index.ntotal:,} chunks foram processados e indexados com sucesso!")
        else:
            print(f"\n⚠️  O índice existe mas não contém vetores")
            
    except Exception as e:
        print(f"✗ Erro ao carregar índice FAISS: {e}")

if __name__ == "__main__":
    check_faiss_index()