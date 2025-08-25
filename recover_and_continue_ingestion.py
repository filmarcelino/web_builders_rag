import json
import os
import faiss
import asyncio
from datetime import datetime
from src.indexing.index_manager import IndexManager
from src.ingestion.pipeline import IngestionPipeline
from config.config import RAGConfig

def recover_metadata():
    """Tenta recuperar metadados básicos baseado no índice FAISS"""
    print("=== Recuperação de Metadados ===")
    
    index_file = 'rag_data/faiss_index.bin'
    metadata_file = 'rag_data/chunk_metadata.json'
    
    if not os.path.exists(index_file):
        print("✗ Índice FAISS não encontrado")
        return False
    
    try:
        # Carregar índice FAISS
        index = faiss.read_index(index_file)
        total_vectors = index.ntotal
        
        print(f"✓ Índice FAISS carregado: {total_vectors:,} vetores")
        
        # Criar metadados básicos para continuar
        # Como o arquivo está corrompido, vamos criar um backup e começar novo
        if os.path.exists(metadata_file):
            backup_file = f"{metadata_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(metadata_file, backup_file)
            print(f"✓ Backup do arquivo corrompido criado: {backup_file}")
        
        # Criar novo arquivo de metadados vazio
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        
        print(f"✓ Novo arquivo de metadados criado")
        print(f"⚠️  ATENÇÃO: {total_vectors:,} chunks já foram processados")
        print(f"⚠️  O processo continuará do início, mas pode pular chunks já indexados")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro na recuperação: {e}")
        return False

async def continue_ingestion():
    """Continua o processo de ingestão"""
    print("\n=== Continuando Ingestão ===")
    
    try:
        # Inicializar pipeline
        pipeline = IngestionPipeline()
        
        # Executar pipeline completo
        print("🚀 Iniciando pipeline de ingestão...")
        stats = await pipeline.run_full_pipeline()
        
        print(f"\n✅ Pipeline concluído!")
        print(f"📊 Estatísticas:")
        print(f"   - Fontes coletadas: {stats.collected_sources}")
        print(f"   - Fontes normalizadas: {stats.normalized_sources}")
        print(f"   - Fontes válidas: {stats.valid_sources}")
        print(f"   - Total de seções: {stats.total_sections}")
        print(f"   - Tempo de processamento: {stats.processing_time_seconds:.2f}s")
        
        if stats.errors:
            print(f"⚠️  Erros encontrados: {len(stats.errors)}")
            for error in stats.errors[:5]:  # Mostrar apenas os primeiros 5
                print(f"   - {error}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro durante ingestão: {e}")
        return False

def main():
    """Função principal de recuperação e continuação"""
    print("🔧 Iniciando recuperação e continuação da ingestão do RAG")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Passo 1: Recuperar metadados
    if not recover_metadata():
        print("❌ Falha na recuperação. Abortando.")
        return
    
    # Passo 2: Continuar ingestão
    print("\n⏳ Aguarde enquanto o processo de ingestão continua...")
    print("💡 Este processo pode levar várias horas dependendo do volume de dados")
    
    try:
        asyncio.run(continue_ingestion())
        print("\n🎉 Processo concluído com sucesso!")
    except KeyboardInterrupt:
        print("\n⏹️  Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()