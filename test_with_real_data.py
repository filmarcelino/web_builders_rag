#!/usr/bin/env python3
"""
Teste usando exatamente os dados processados pelo teste principal.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar diretório atual ao path
sys.path.append(str(Path.cwd()))

from ingest_to_rag import RAGIngestor

async def test_with_real_data():
    """Testa usando os dados reais processados pelo teste principal."""
    
    print("=== TESTE COM DADOS REAIS ===")
    
    # Verificar se OPENAI_API_KEY está configurada
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY não configurada")
        return False
    
    print(f"✅ OPENAI_API_KEY configurada: {api_key[:10]}...")
    
    # Usar os diretórios reais do teste principal
    test_processed_dir = Path("test_processed_corpus")
    test_rag_data_dir = Path("test_rag_data_real")
    
    # Verificar se dados processados existem
    if not test_processed_dir.exists():
        print(f"❌ Diretório de dados processados não existe: {test_processed_dir}")
        return False
    
    # Verificar arquivos de chunks
    batch_files = list(test_processed_dir.glob("chunks_batch_*.json"))
    if not batch_files:
        print(f"❌ Nenhum arquivo de chunks encontrado em {test_processed_dir}")
        return False
    
    print(f"✅ Encontrados {len(batch_files)} arquivos de chunks:")
    for batch_file in batch_files:
        print(f"  - {batch_file.name}")
    
    # Limpar diretório de destino se existir
    import shutil
    if test_rag_data_dir.exists():
        shutil.rmtree(test_rag_data_dir)
    
    # Criar diretório de destino
    test_rag_data_dir.mkdir(exist_ok=True)
    print(f"✅ Diretório de destino criado: {test_rag_data_dir}")
    
    try:
        # Criar RAGIngestor
        print("\nCriando RAGIngestor...")
        ingestor = RAGIngestor(
            processed_corpus_dir=str(test_processed_dir),
            rag_data_dir=str(test_rag_data_dir)
        )
        print("✅ RAGIngestor criado com sucesso")
        
        # Verificar caminhos
        print(f"\nCaminhos configurados:")
        print(f"  - Processed: {ingestor.processed_corpus_dir}")
        print(f"  - RAG Data: {ingestor.rag_data_dir}")
        
        # Carregar chunks para verificar
        print("\nCarregando chunks...")
        chunks = ingestor.load_processed_chunks()
        print(f"✅ Carregados {len(chunks)} chunks")
        
        if chunks:
            print(f"Exemplo de chunk:")
            print(f"  - ID: {chunks[0]['id']}")
            print(f"  - Título: {chunks[0]['title']}")
            print(f"  - Tokens: {chunks[0]['token_count']}")
        
        # Executar ingestão
        print("\nExecutando ingestão...")
        await ingestor.run_ingestion()
        print("✅ Ingestão concluída")
        
        # Verificar se arquivos foram criados
        index_file = test_rag_data_dir / "faiss_index.bin"
        metadata_file = test_rag_data_dir / "chunk_metadata.json"
        
        print(f"\nVerificação de arquivos:")
        print(f"  - Index file exists: {index_file.exists()}")
        print(f"  - Metadata file exists: {metadata_file.exists()}")
        
        if index_file.exists() and metadata_file.exists():
            print("\n✅ Arquivos de índice criados com sucesso")
            
            # Testar busca
            print("\nTestando busca...")
            results = ingestor.test_search("Como criar um componente React?", top_k=3)
            if results:
                print(f"✅ Busca funcionando - {len(results)} resultados encontrados")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['title']} (Score: {result['similarity_score']:.3f})")
            else:
                print("⚠️ Busca não retornou resultados")
            
            return True
        else:
            print("\n❌ Arquivos de índice não foram criados")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpar diretório de teste
        if test_rag_data_dir.exists():
            shutil.rmtree(test_rag_data_dir)
        print("\n🧹 Diretório de teste limpo")

if __name__ == "__main__":
    success = asyncio.run(test_with_real_data())
    
    if success:
        print("\n✅ TESTE COM DADOS REAIS PASSOU")
    else:
        print("\n❌ TESTE COM DADOS REAIS FALHOU")