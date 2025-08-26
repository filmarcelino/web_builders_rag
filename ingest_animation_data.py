#!/usr/bin/env python3
"""
Script para ingerir dados de animação processados no sistema RAG
Integra os chunks de animação com o índice FAISS existente
"""

import os
import json
import numpy as np
from pathlib import Path
import logging
from typing import List, Dict, Any
import time

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv não instalado. Execute: pip install python-dotenv")

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("OpenAI não instalado. Execute: pip install openai")
    exit(1)

try:
    import faiss
except ImportError:
    print("FAISS não instalado. Execute: pip install faiss-cpu")
    exit(1)

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnimationDataIngestor:
    def __init__(self, 
                 animation_chunks_dir="processed_corpus/animations",
                 rag_data_dir="rag_data",
                 embedding_model="text-embedding-3-small"):
        
        self.animation_chunks_dir = Path(animation_chunks_dir)
        self.rag_data_dir = Path(rag_data_dir)
        self.embedding_model = embedding_model
        
        # Configuração OpenAI
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Arquivos do sistema RAG
        self.faiss_index_file = self.rag_data_dir / "faiss_index.bin"
        self.metadata_file = self.rag_data_dir / "chunk_metadata.json"
        
        # Backup dos arquivos originais
        self.backup_dir = self.rag_data_dir / "backup"
        self.backup_dir.mkdir(exist_ok=True)
    
    def ingest_animation_data(self):
        """Ingere dados de animação no sistema RAG"""
        logger.info("Iniciando ingestão de dados de animação...")
        
        try:
            # 1. Carrega chunks de animação
            animation_chunks = self._load_animation_chunks()
            logger.info(f"Carregados {len(animation_chunks)} chunks de animação")
            
            # 2. Gera embeddings para os chunks
            embeddings = self.generate_embeddings(animation_chunks)
            logger.info(f"Gerados {len(embeddings)} embeddings")
            
            # 3. Carrega índice FAISS existente
            existing_index, existing_metadata = self._load_existing_rag_data()
            
            # 4. Faz backup dos dados existentes
            self._backup_existing_data()
            
            # 5. Integra novos dados com os existentes
            updated_index, updated_metadata = self._integrate_data(
                existing_index, existing_metadata, 
                embeddings, animation_chunks
            )
            
            # 6. Salva dados atualizados
            self._save_updated_rag_data(updated_index, updated_metadata)
            
            # 7. Gera relatório
            report = self._generate_ingestion_report(animation_chunks, existing_metadata, updated_metadata)
            
            logger.info("Ingestão de dados de animação concluída com sucesso!")
            return report
            
        except Exception as e:
            logger.error(f"Erro durante a ingestão: {e}")
            self._restore_from_backup()
            raise
    
    def _load_animation_chunks(self) -> List[Dict]:
        """Carrega todos os chunks de animação processados"""
        logger.info("Carregando chunks de animação...")
        
        all_chunks = []
        
        # Carrega todos os arquivos de batch
        for batch_file in self.animation_chunks_dir.glob("animation_chunks_batch_*.json"):
            try:
                with open(batch_file, 'r', encoding='utf-8') as f:
                    batch_data = json.load(f)
                
                chunks = batch_data.get('chunks', [])
                all_chunks.extend(chunks)
                
                logger.info(f"Carregado {batch_file.name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Erro ao carregar {batch_file}: {e}")
        
        return all_chunks
    
    def filter_and_prepare_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtra e prepara chunks para evitar problemas de limite de tokens."""
        filtered_chunks = []
        max_chars = 6000  # Limite seguro para evitar problemas de tokens
        
        for chunk in chunks:
            text = chunk.get('text', '')
            
            # Pula chunks vazios
            if not text.strip():
                continue
                
            # Trunca chunks muito grandes
            if len(text) > max_chars:
                chunk['text'] = text[:max_chars] + "...[truncated]"
                chunk['metadata']['truncated'] = True
                logger.warning(f"Chunk truncado de {len(text)} para {max_chars} caracteres")
            
            filtered_chunks.append(chunk)
        
        logger.info(f"Filtrados {len(filtered_chunks)} chunks de {len(chunks)} originais")
        return filtered_chunks
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> np.ndarray:
        """Gera embeddings para os chunks usando OpenAI."""
        logger.info(f"Gerando embeddings para {len(chunks)} chunks...")
        
        # Filtra e prepara chunks
        chunks = self.filter_and_prepare_chunks(chunks)
        
        embeddings = []
        batch_size = 5  # Batch ainda menor para segurança
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_texts = [chunk['text'] for chunk in batch]
            
            try:
                # Gera embeddings para o batch
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch_texts
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                logger.info(f"Processado batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao gerar embeddings para batch {i//batch_size + 1}: {e}")
                raise
        
        return np.array(embeddings, dtype=np.float32)
    
    def _load_existing_rag_data(self):
        """Carrega dados RAG existentes"""
        logger.info("Carregando dados RAG existentes...")
        
        # Carrega índice FAISS
        if self.faiss_index_file.exists():
            index = faiss.read_index(str(self.faiss_index_file))
            logger.info(f"Índice FAISS carregado: {index.ntotal} vetores")
        else:
            logger.warning("Índice FAISS não encontrado, criando novo")
            # Cria novo índice (assumindo dimensão 1536 para text-embedding-3-small)
            index = faiss.IndexFlatIP(1536)
        
        # Carrega metadados
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            logger.info(f"Metadados carregados: {len(metadata)} chunks")
        else:
            logger.warning("Metadados não encontrados, criando novos")
            metadata = []
        
        return index, metadata
    
    def _backup_existing_data(self):
        """Faz backup dos dados existentes"""
        logger.info("Fazendo backup dos dados existentes...")
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        if self.faiss_index_file.exists():
            backup_index = self.backup_dir / f"faiss_index_backup_{timestamp}.bin"
            import shutil
            shutil.copy2(self.faiss_index_file, backup_index)
            logger.info(f"Backup do índice: {backup_index}")
        
        if self.metadata_file.exists():
            backup_metadata = self.backup_dir / f"chunk_metadata_backup_{timestamp}.json"
            import shutil
            shutil.copy2(self.metadata_file, backup_metadata)
            logger.info(f"Backup dos metadados: {backup_metadata}")
    
    def _integrate_data(self, existing_index, existing_metadata, new_embeddings, new_chunks):
        """Integra novos dados com os existentes"""
        logger.info("Integrando novos dados...")
        
        # Adiciona novos embeddings ao índice
        existing_index.add(new_embeddings)
        
        # Prepara metadados dos novos chunks
        new_metadata = []
        base_id = len(existing_metadata)
        
        for i, chunk in enumerate(new_chunks):
            metadata_entry = {
                "id": base_id + i,
                "chunk_id": chunk['id'],
                "text": chunk['text'],
                "source": chunk['metadata']['source'],
                "content_type": chunk['metadata']['content_type'],
                "description": chunk['metadata']['description'],
                "license": chunk['metadata']['license'],
                "animation_score": chunk['metadata']['animation_score'],
                "chunk_index": chunk['metadata']['chunk_index'],
                "ingested_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "data_source": "animation_enhancement"
            }
            
            # Adiciona campos específicos se existirem
            if 'file_path' in chunk['metadata']:
                metadata_entry['file_path'] = chunk['metadata']['file_path']
            if 'section_index' in chunk['metadata']:
                metadata_entry['section_index'] = chunk['metadata']['section_index']
            
            new_metadata.append(metadata_entry)
        
        # Combina metadados
        updated_metadata = existing_metadata + new_metadata
        
        logger.info(f"Dados integrados: {len(new_chunks)} novos chunks adicionados")
        return existing_index, updated_metadata
    
    def _save_updated_rag_data(self, index, metadata):
        """Salva dados RAG atualizados"""
        logger.info("Salvando dados RAG atualizados...")
        
        # Salva índice FAISS
        faiss.write_index(index, str(self.faiss_index_file))
        logger.info(f"Índice FAISS salvo: {index.ntotal} vetores")
        
        # Salva metadados
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"Metadados salvos: {len(metadata)} chunks")
    
    def _restore_from_backup(self):
        """Restaura dados do backup em caso de erro"""
        logger.warning("Restaurando dados do backup...")
        
        try:
            # Encontra backups mais recentes
            backup_files = list(self.backup_dir.glob("*_backup_*.bin"))
            if backup_files:
                latest_index_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
                import shutil
                shutil.copy2(latest_index_backup, self.faiss_index_file)
                logger.info(f"Índice restaurado de: {latest_index_backup}")
            
            backup_metadata = list(self.backup_dir.glob("*_backup_*.json"))
            if backup_metadata:
                latest_metadata_backup = max(backup_metadata, key=lambda x: x.stat().st_mtime)
                import shutil
                shutil.copy2(latest_metadata_backup, self.metadata_file)
                logger.info(f"Metadados restaurados de: {latest_metadata_backup}")
                
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
    
    def _generate_ingestion_report(self, animation_chunks, old_metadata, new_metadata) -> Dict:
        """Gera relatório da ingestão"""
        logger.info("Gerando relatório de ingestão...")
        
        # Estatísticas dos chunks de animação
        animation_stats = {
            "total_chunks": len(animation_chunks),
            "content_types": {},
            "avg_animation_score": 0,
            "high_quality_chunks": 0
        }
        
        scores = []
        for chunk in animation_chunks:
            content_type = chunk['metadata']['content_type']
            animation_stats['content_types'][content_type] = animation_stats['content_types'].get(content_type, 0) + 1
            
            score = chunk['metadata']['animation_score']
            scores.append(score)
            
            if score > 0.5:
                animation_stats['high_quality_chunks'] += 1
        
        animation_stats['avg_animation_score'] = sum(scores) / len(scores) if scores else 0
        
        # Estatísticas do sistema RAG
        rag_stats = {
            "before_ingestion": len(old_metadata),
            "after_ingestion": len(new_metadata),
            "chunks_added": len(animation_chunks),
            "growth_percentage": round((len(animation_chunks) / len(old_metadata)) * 100, 1) if old_metadata else 0
        }
        
        report = {
            "ingestion_summary": {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "status": "success",
                "animation_data": animation_stats,
                "rag_system": rag_stats
            },
            "quality_analysis": {
                "animation_focused_chunks": animation_stats['high_quality_chunks'],
                "quality_percentage": round((animation_stats['high_quality_chunks'] / len(animation_chunks)) * 100, 1),
                "average_relevance_score": round(animation_stats['avg_animation_score'], 3)
            },
            "recommendations": [
                "Testar consultas específicas sobre animações CSS",
                "Verificar melhoria na qualidade das respostas",
                "Monitorar performance do sistema com dados expandidos",
                "Considerar ajustes nos prompts para melhor utilização do conteúdo de animação"
            ]
        }
        
        # Salva relatório
        report_file = self.rag_data_dir / "animation_ingestion_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Relatório salvo em: {report_file}")
        return report

if __name__ == "__main__":
    try:
        ingestor = AnimationDataIngestor()
        report = ingestor.ingest_animation_data()
        
        print("\n=== RELATORIO DE INGESTAO ===")
        print(f"Status: {report['ingestion_summary']['status']}")
        print(f"Chunks de animação adicionados: {report['ingestion_summary']['animation_data']['total_chunks']}")
        print(f"Total no sistema RAG: {report['ingestion_summary']['rag_system']['after_ingestion']}")
        print(f"Crescimento: {report['ingestion_summary']['rag_system']['growth_percentage']}%")
        print(f"Chunks de alta qualidade: {report['quality_analysis']['animation_focused_chunks']} ({report['quality_analysis']['quality_percentage']}%)")
        print(f"Score médio de relevância: {report['quality_analysis']['average_relevance_score']}")
        print("\nIngestão concluída com sucesso!")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        print("Verifique as configurações e tente novamente.")