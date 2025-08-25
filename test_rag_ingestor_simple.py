#!/usr/bin/env python3
"""
Teste simples e isolado do RAGIngestor.
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

def test_rag_ingestor():
    """Teste isolado do RAGIngestor."""
    
    print("=== TESTE ISOLADO DO RAG INGESTOR ===")
    
    # Verificar se OPENAI_API_KEY está configurada
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY não configurada")
        return False
    
    print(f"✅ OPENAI_API_KEY configurada: {api_key[:10]}...")
    
    # Criar diretórios de teste
    test_processed_dir = Path("test_processed_simple")
    test_rag_data_dir = Path("test_rag_data_simple")
    
    # Limpar diretórios existentes
    import shutil
    for test_dir in [test_processed_dir, test_rag_data_dir]:
        if test_dir.exists():
            shutil.rmtree(test_dir)
    
    # Criar diretórios
    test_processed_dir.mkdir(exist_ok=True)
    test_rag_data_dir.mkdir(exist_ok=True)
    
    # Criar dados de teste simples
    test_chunks = [
        {
            "id": "test_1",
            "content": "React é uma biblioteca JavaScript para construir interfaces de usuário.",
            "title": "Introdução ao React",
            "source_file": "react_intro.md",
            "metadata": {"type": "documentation"},
            "token_count": 15
        },
        {
            "id": "test_2",
            "content": "Componentes são blocos de construção reutilizáveis em React.",
            "title": "Componentes React",
            "source_file": "react_components.md",
            "metadata": {"type": "documentation"},
            "token_count": 12
        }
    ]
    
    # Salvar chunks de teste
    batch_file = test_processed_dir / "chunks_batch_0.json"
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump(test_chunks, f, ensure_ascii=False, indent=2)
    
    # Salvar metadados
    metadata = {
        "total_chunks": len(test_chunks),
        "total_files_processed": 2,
        "processing_time": 1.0,
        "statistics": {
            "total_chunks": len(test_chunks),
            "avg_token_count": 13.5
        }
    }
    
    metadata_file = test_processed_dir / "processing_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Dados de teste criados em {test_processed_dir}")
    
    try:
        # Criar RAGIngestor
        print("Criando RAGIngestor...")
        ingestor = RAGIngestor(
            processed_corpus_dir=str(test_processed_dir),
            rag_data_dir=str(test_rag_data_dir)
        )
        print("✅ RAGIngestor criado com sucesso")
        
        # Testar criação de novo índice
        print("Criando novo índice...")
        ingestor.create_new_index()
        print(f"✅ Índice criado: {type(ingestor.index)}")
        
        # Testar salvamento do índice vazio
        print("Testando salvamento de índice vazio...")
        ingestor.save_index()
        print("✅ Índice vazio salvo com sucesso")
        
        # Verificar se arquivos foram criados
        index_file = test_rag_data_dir / "faiss_index.bin"
        metadata_file = test_rag_data_dir / "chunk_metadata.json"
        
        if index_file.exists() and metadata_file.exists():
            print("✅ Arquivos de índice criados com sucesso")
            print(f"  - Índice: {index_file}")
            print(f"  - Metadados: {metadata_file}")
            return True
        else:
            print("❌ Arquivos de índice não foram criados")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpar diretórios de teste
        for test_dir in [test_processed_dir, test_rag_data_dir]:
            if test_dir.exists():
                shutil.rmtree(test_dir)
        print("🧹 Diretórios de teste limpos")

if __name__ == "__main__":
    success = test_rag_ingestor()
    
    if success:
        print("\n✅ TESTE PASSOU - RAGIngestor funciona corretamente")
    else:
        print("\n❌ TESTE FALHOU - Problema com RAGIngestor")