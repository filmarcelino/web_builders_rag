import json
import os

def check_rag_status():
    rag_data_dir = 'rag_data'
    metadata_file = os.path.join(rag_data_dir, 'chunk_metadata.json')
    index_file = os.path.join(rag_data_dir, 'faiss_index.bin')
    
    print("=== Status da Alimentação do RAG ===")
    
    # Verificar se os arquivos existem
    if os.path.exists(metadata_file):
        file_size = os.path.getsize(metadata_file)
        print(f"✓ Arquivo de metadados encontrado: {file_size:,} bytes")
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_chunks = len(data)
            print(f"✓ Total de chunks processados: {total_chunks:,}")
            
            if data:
                # Pegar alguns IDs para mostrar o progresso
                chunk_ids = list(data.keys())
                print(f"✓ Primeiro chunk ID: {chunk_ids[0]}")
                print(f"✓ Último chunk ID: {chunk_ids[-1]}")
                
                # Verificar alguns metadados
                sample_chunk = data[chunk_ids[0]]
                print(f"✓ Exemplo de fonte: {sample_chunk.get('source', 'N/A')}")
            
        except Exception as e:
            print(f"✗ Erro ao ler metadados: {e}")
    else:
        print("✗ Arquivo de metadados não encontrado")
    
    if os.path.exists(index_file):
        file_size = os.path.getsize(index_file)
        print(f"✓ Índice FAISS encontrado: {file_size:,} bytes")
    else:
        print("✗ Índice FAISS não encontrado")
    
    # Verificar diretório de corpus processado
    processed_dir = 'processed_corpus'
    if os.path.exists(processed_dir):
        files = [f for f in os.listdir(processed_dir) if f.endswith('.json')]
        print(f"✓ Arquivos processados no corpus: {len(files)}")
    else:
        print("✗ Diretório de corpus processado não encontrado")

if __name__ == "__main__":
    check_rag_status()