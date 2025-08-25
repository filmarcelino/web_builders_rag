#!/usr/bin/env python3
"""
Teste para debugar diferenças de caminhos entre teste isolado e teste principal.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar diretório atual ao path
sys.path.append(str(Path.cwd()))

from ingest_to_rag import RAGIngestor

def test_paths_comparison():
    """Compara caminhos entre teste isolado e teste principal."""
    
    print("=== TESTE DE COMPARAÇÃO DE CAMINHOS ===")
    
    # Simular exatamente o que o teste principal faz
    base_dir = Path.cwd()
    test_processed_dir = base_dir / "test_processed_corpus"
    test_rag_data_dir = base_dir / "test_rag_data"
    
    # Usar caminhos absolutos como no teste principal
    test_processed_dir = test_processed_dir.resolve()
    test_rag_data_dir = test_rag_data_dir.resolve()
    
    print(f"Base dir: {base_dir}")
    print(f"Processed dir: {test_processed_dir}")
    print(f"RAG data dir: {test_rag_data_dir}")
    
    # Verificar se diretórios existem
    print(f"\nProcessed dir exists: {test_processed_dir.exists()}")
    print(f"RAG data dir exists: {test_rag_data_dir.exists()}")
    
    # Criar diretórios se não existirem
    test_processed_dir.mkdir(exist_ok=True)
    test_rag_data_dir.mkdir(exist_ok=True)
    
    print(f"\nApós criação:")
    print(f"Processed dir exists: {test_processed_dir.exists()}")
    print(f"RAG data dir exists: {test_rag_data_dir.exists()}")
    
    # Verificar permissões
    print(f"\nPermissões:")
    print(f"Processed dir writable: {os.access(test_processed_dir, os.W_OK)}")
    print(f"RAG data dir writable: {os.access(test_rag_data_dir, os.W_OK)}")
    
    # Testar criação de arquivo no diretório RAG
    test_file = test_rag_data_dir / "test_write.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("teste")
        print(f"✅ Conseguiu escrever arquivo de teste: {test_file}")
        test_file.unlink()  # Remover arquivo de teste
    except Exception as e:
        print(f"❌ Erro ao escrever arquivo de teste: {e}")
    
    # Criar dados de teste mínimos
    test_chunks = [
        {
            "id": "test_1",
            "content": "Teste de conteúdo.",
            "title": "Teste",
            "source_file": "test.md",
            "metadata": {"type": "test"},
            "token_count": 5
        }
    ]
    
    # Salvar chunks de teste
    batch_file = test_processed_dir / "chunks_batch_0.json"
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump(test_chunks, f, ensure_ascii=False, indent=2)
    
    # Salvar metadados
    metadata = {
        "total_chunks": len(test_chunks),
        "total_files_processed": 1,
        "processing_time": 1.0,
        "statistics": {
            "total_chunks": len(test_chunks),
            "avg_token_count": 5
        }
    }
    
    metadata_file = test_processed_dir / "processing_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dados de teste criados")
    
    try:
        # Criar RAGIngestor exatamente como no teste principal
        print("\nCriando RAGIngestor com caminhos do teste principal...")
        ingestor = RAGIngestor(
            processed_corpus_dir=str(test_processed_dir),
            rag_data_dir=str(test_rag_data_dir)
        )
        print("✅ RAGIngestor criado")
        
        # Verificar caminhos internos
        print(f"\nCaminhos internos do RAGIngestor:")
        print(f"processed_corpus_dir: {ingestor.processed_corpus_dir}")
        print(f"rag_data_dir: {ingestor.rag_data_dir}")
        
        # Testar criação de índice
        print("\nCriando índice...")
        ingestor.create_new_index()
        print("✅ Índice criado")
        
        # Testar salvamento
        print("\nTestando salvamento...")
        ingestor.save_index()
        print("✅ Salvamento concluído")
        
        # Verificar arquivos
        index_file = test_rag_data_dir / "faiss_index.bin"
        metadata_file = test_rag_data_dir / "chunk_metadata.json"
        
        print(f"\nVerificação de arquivos:")
        print(f"Index file exists: {index_file.exists()}")
        print(f"Metadata file exists: {metadata_file.exists()}")
        
        if index_file.exists() and metadata_file.exists():
            print("\n✅ TESTE PASSOU - Arquivos criados com sucesso")
            return True
        else:
            print("\n❌ TESTE FALHOU - Arquivos não foram criados")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpar arquivos de teste
        import shutil
        for test_dir in [test_processed_dir, test_rag_data_dir]:
            if test_dir.exists():
                shutil.rmtree(test_dir)
        print("\n🧹 Diretórios de teste limpos")

if __name__ == "__main__":
    success = test_paths_comparison()
    
    if success:
        print("\n✅ TESTE DE CAMINHOS PASSOU")
    else:
        print("\n❌ TESTE DE CAMINHOS FALHOU")