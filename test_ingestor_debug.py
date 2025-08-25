#!/usr/bin/env python3
"""
Script para debugar o problema específico do RAGIngestor no teste principal.
"""

import asyncio
import os
import sys
import shutil
from pathlib import Path
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ingestor_with_main_data():
    """Testa o RAGIngestor usando os mesmos dados do teste principal."""
    
    # Diretórios - usando caminho mais simples para evitar problemas com caracteres especiais
    base_dir = Path.cwd()
    test_processed_dir = base_dir / "test_processed_corpus"
    test_rag_data_dir = Path("C:/Users/luisf/test_rag_debug")
    
    try:
        # Limpar diretório de destino
        if test_rag_data_dir.exists():
            shutil.rmtree(test_rag_data_dir)
        
        # Criar diretório
        test_rag_data_dir.mkdir(exist_ok=True)
        
        logger.info(f"Diretório criado: {test_rag_data_dir.exists()}")
        logger.info(f"Diretório de dados processados existe: {test_processed_dir.exists()}")
        
        # Verificar se há dados processados
        if not test_processed_dir.exists():
            logger.error("Diretório de dados processados não existe")
            return False
            
        # Listar arquivos no diretório processado
        processed_files = list(test_processed_dir.glob("*.json"))
        logger.info(f"Arquivos processados encontrados: {len(processed_files)}")
        for f in processed_files:
            logger.info(f"  - {f.name}")
        
        # Verificar OPENAI_API_KEY
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("OPENAI_API_KEY não configurada")
            return False
        
        # Importar RAGIngestor
        sys.path.append(str(base_dir))
        from ingest_to_rag import RAGIngestor
        
        logger.info("Criando RAGIngestor...")
        
        # Criar ingestor
        ingestor = RAGIngestor(
            processed_corpus_dir=str(test_processed_dir),
            rag_data_dir=str(test_rag_data_dir)
        )
        
        logger.info("RAGIngestor criado com sucesso")
        logger.info(f"Diretório RAG: {ingestor.rag_data_dir}")
        logger.info(f"Diretório processado: {ingestor.processed_corpus_dir}")
        
        # Verificar se diretório ainda existe antes da ingestão
        logger.info(f"Diretório RAG existe antes da ingestão: {test_rag_data_dir.exists()}")
        
        # Executar ingestão
        logger.info("Iniciando ingestão...")
        await ingestor.run_ingestion()
        logger.info("Ingestão concluída")
        
        # Verificar resultados
        index_file = test_rag_data_dir / "faiss_index.bin"
        metadata_file = test_rag_data_dir / "chunk_metadata.json"
        
        logger.info(f"Arquivo de índice existe: {index_file.exists()}")
        logger.info(f"Arquivo de metadados existe: {metadata_file.exists()}")
        
        if index_file.exists() and metadata_file.exists():
            logger.info("✅ Ingestão bem-sucedida")
            
            # Testar busca
            results = ingestor.test_search("Como criar um componente React?", top_k=3)
            logger.info(f"Busca retornou {len(results) if results else 0} resultados")
            
            return True
        else:
            logger.error("❌ Ingestão falhou")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpar
        if test_rag_data_dir.exists():
            shutil.rmtree(test_rag_data_dir)
            logger.info("Diretório de teste limpo")

if __name__ == "__main__":
    result = asyncio.run(test_ingestor_with_main_data())
    if result:
        print("\n✅ Teste passou")
    else:
        print("\n❌ Teste falhou")