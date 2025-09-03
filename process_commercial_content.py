#!/usr/bin/env python3
"""
Processa conteúdo comercial coletado e integra ao RAG existente.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import hashlib

# Imports do sistema existente
from process_corpus import DocumentChunk
from ingest_to_rag import RAGIngestor
import tiktoken

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CommercialContentProcessor:
    """Processa conteúdo comercial coletado para integração no RAG."""
    
    def __init__(self, 
                 commercial_dir: str = "corpus/commercial_tools",
                 output_dir: str = "processed_corpus/commercial"):
        
        self.commercial_dir = Path(commercial_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações de chunking otimizadas para conteúdo comercial
        self.max_chunk_size = 800  # Chunks maiores para documentação técnica
        self.chunk_overlap = 150   # Overlap maior para manter contexto
        
        # Tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def load_commercial_content(self) -> Dict[str, List[Dict]]:
        """Carrega todo o conteúdo comercial coletado."""
        logger.info("Carregando conteúdo comercial coletado...")
        
        all_content = {}
        
        for source_dir in self.commercial_dir.iterdir():
            if not source_dir.is_dir():
                continue
            
            raw_file = source_dir / "raw_content.json"
            if not raw_file.exists():
                logger.warning(f"Arquivo raw_content.json não encontrado em {source_dir}")
                continue
            
            try:
                with open(raw_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                all_content[source_dir.name] = content
                logger.info(f"Carregado {len(content)} itens de {source_dir.name}")
                
            except Exception as e:
                logger.error(f"Erro ao carregar {raw_file}: {e}")
                continue
        
        total_items = sum(len(content) for content in all_content.values())
        logger.info(f"Total carregado: {total_items} itens de {len(all_content)} fontes")
        
        return all_content
    
    def create_commercial_chunks(self, content: str, source_name: str, metadata: Dict) -> List[DocumentChunk]:
        """Cria chunks otimizados para conteúdo comercial."""
        chunks = []
        
        # Tokenizar o conteúdo
        tokens = self.tokenizer.encode(content)
        
        # Se o conteúdo é pequeno, criar um único chunk
        if len(tokens) <= self.max_chunk_size:
            chunk_id = hashlib.md5(f"{source_name}_{metadata['url']}_0".encode()).hexdigest()[:12]
            
            chunk = DocumentChunk(
                id=f"comm_{chunk_id}",
                source_file=metadata['url'],
                source_type='commercial_documentation',
                title=metadata.get('title', f"{source_name} Documentation"),
                content=content,
                metadata={
                    'source_name': source_name,
                    'category': metadata['category'],
                    'url': metadata['url'],
                    'priority': metadata['priority'],
                    'collected_at': metadata['collected_at'],
                    'commercial_tool': True,
                    'tool_type': metadata['category']
                },
                token_count=len(tokens),
                chunk_index=0,
                total_chunks=1
            )
            
            chunks.append(chunk)
            return chunks
        
        # Dividir em chunks com overlap
        chunk_count = 0
        for i in range(0, len(tokens), self.max_chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.max_chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            if len(chunk_text.strip()) < 50:
                continue
            
            # Criar ID único
            chunk_id = hashlib.md5(f"{source_name}_{metadata['url']}_{chunk_count}".encode()).hexdigest()[:12]
            
            chunk = DocumentChunk(
                id=f"comm_{chunk_id}",
                source_file=metadata['url'],
                source_type='commercial_documentation',
                title=f"{metadata.get('title', source_name)} (Parte {chunk_count + 1})",
                content=chunk_text,
                metadata={
                    'source_name': source_name,
                    'category': metadata['category'],
                    'url': metadata['url'],
                    'priority': metadata['priority'],
                    'collected_at': metadata['collected_at'],
                    'commercial_tool': True,
                    'tool_type': metadata['category'],
                    'chunk_part': chunk_count + 1
                },
                token_count=len(chunk_tokens),
                chunk_index=chunk_count,
                total_chunks=0  # Será atualizado depois
            )
            
            chunks.append(chunk)
            chunk_count += 1
        
        # Atualizar total_chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        return chunks
    
    def process_all_commercial_content(self) -> Dict:
        """Processa todo o conteúdo comercial em chunks."""
        logger.info("=== INICIANDO PROCESSAMENTO DE CONTEÚDO COMERCIAL ===")
        
        # Carregar conteúdo
        all_content = self.load_commercial_content()
        
        if not all_content:
            logger.warning("Nenhum conteúdo comercial encontrado para processar")
            return {}
        
        all_chunks = []
        processing_stats = {
            'sources_processed': 0,
            'total_chunks': 0,
            'total_tokens': 0,
            'categories': {},
            'sources': {}
        }
        
        # Processar cada fonte
        for source_name, content_items in all_content.items():
            logger.info(f"Processando fonte: {source_name}")
            
            source_chunks = []
            
            for item in content_items:
                content = item['content']
                if len(content.strip()) < 100:  # Ignorar conteúdo muito pequeno
                    continue
                
                # Criar chunks do conteúdo
                item_chunks = self.create_commercial_chunks(
                    content=content,
                    source_name=source_name,
                    metadata=item
                )
                
                source_chunks.extend(item_chunks)
            
            all_chunks.extend(source_chunks)
            
            # Atualizar estatísticas
            processing_stats['sources_processed'] += 1
            processing_stats['sources'][source_name] = len(source_chunks)
            
            # Estatísticas por categoria
            if source_chunks:
                category = source_chunks[0].metadata['category']
                if category not in processing_stats['categories']:
                    processing_stats['categories'][category] = 0
                processing_stats['categories'][category] += len(source_chunks)
            
            logger.info(f"✅ {source_name}: {len(source_chunks)} chunks criados")
        
        processing_stats['total_chunks'] = len(all_chunks)
        processing_stats['total_tokens'] = sum(chunk.token_count for chunk in all_chunks)
        
        # Salvar chunks processados
        self._save_commercial_chunks(all_chunks)
        
        logger.info(f"=== PROCESSAMENTO CONCLUÍDO ===")
        logger.info(f"📊 Estatísticas:")
        logger.info(f"  - Fontes processadas: {processing_stats['sources_processed']}")
        logger.info(f"  - Total de chunks: {processing_stats['total_chunks']}")
        logger.info(f"  - Total de tokens: {processing_stats['total_tokens']}")
        logger.info(f"  - Categorias: {processing_stats['categories']}")
        
        return processing_stats
    
    def _save_commercial_chunks(self, chunks: List[DocumentChunk]):
        """Salva chunks comerciais processados."""
        logger.info(f"Salvando {len(chunks)} chunks comerciais...")
        
        # Converter para formato JSON
        chunks_data = []
        for chunk in chunks:
            chunk_dict = {
                'id': chunk.id,
                'source_file': chunk.source_file,
                'source_type': chunk.source_type,
                'title': chunk.title,
                'content': chunk.content,
                'metadata': chunk.metadata,
                'token_count': chunk.token_count,
                'chunk_index': chunk.chunk_index,
                'total_chunks': chunk.total_chunks
            }
            chunks_data.append(chunk_dict)
        
        # Salvar em arquivo único (já que é conteúdo limitado)
        output_file = self.output_dir / "commercial_chunks.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Chunks salvos em: {output_file}")
        
        # Salvar metadados de processamento
        metadata = {
            'total_chunks': len(chunks),
            'processing_date': datetime.now().isoformat(),
            'chunk_size': self.max_chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'sources': list(set(chunk.metadata['source_name'] for chunk in chunks)),
            'categories': list(set(chunk.metadata['category'] for chunk in chunks)),
            'total_tokens': sum(chunk.token_count for chunk in chunks)
        }
        
        metadata_file = self.output_dir / "commercial_processing_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📋 Metadados salvos em: {metadata_file}")

class CommercialRAGIntegrator:
    """Integra conteúdo comercial processado ao RAG existente."""
    
    def __init__(self):
        self.ingestor = RAGIngestor(
            processed_corpus_dir="processed_corpus",
            rag_data_dir="rag_data"
        )
    
    def integrate_commercial_content(self):
        """Integra conteúdo comercial ao RAG existente."""
        logger.info("=== INTEGRANDO CONTEÚDO COMERCIAL AO RAG ===")
        
        commercial_file = Path("processed_corpus/commercial/commercial_chunks.json")
        
        if not commercial_file.exists():
            logger.error(f"Arquivo de chunks comerciais não encontrado: {commercial_file}")
            return False
        
        try:
            # Carregar chunks comerciais
            with open(commercial_file, 'r', encoding='utf-8') as f:
                commercial_chunks = json.load(f)
            
            logger.info(f"Carregados {len(commercial_chunks)} chunks comerciais")
            
            # Integrar ao RAG
            logger.info("Iniciando integração ao índice FAISS...")
            
            # Usar o ingestor existente para adicionar os chunks
            added_count = 0
            for chunk_data in commercial_chunks:
                try:
                    # Converter de volta para formato esperado pelo ingestor
                    success = self.ingestor.add_single_chunk(chunk_data)
                    if success:
                        added_count += 1
                except Exception as e:
                    logger.warning(f"Erro ao adicionar chunk {chunk_data['id']}: {e}")
                    continue
            
            logger.info(f"✅ Integração concluída: {added_count}/{len(commercial_chunks)} chunks adicionados")
            
            # Salvar índice atualizado
            self.ingestor.save_index()
            logger.info("💾 Índice RAG atualizado e salvo")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro durante integração: {e}")
            return False
    
    def test_commercial_queries(self) -> Dict:
        """Testa queries específicas para conteúdo comercial."""
        logger.info("=== TESTANDO QUERIES COMERCIAIS ===")
        
        test_queries = [
            "Como configurar autenticação no Supabase?",
            "Como criar um script em GDScript no Godot?",
            "Como configurar Firebase para web?",
            "Como usar Webflow para criar componentes?",
            "Como fazer deploy de uma aplicação?",
            "Como configurar banco de dados?"
        ]
        
        results = {}
        
        for query in test_queries:
            logger.info(f"🔍 Testando: {query}")
            
            try:
                search_results = self.ingestor.search_similar(query, top_k=5)
                
                # Analisar resultados
                commercial_chunks = 0
                sources_found = set()
                
                for result in search_results:
                    metadata = result.get('metadata', {})
                    if metadata.get('commercial_tool', False):
                        commercial_chunks += 1
                        sources_found.add(metadata.get('source_name', 'unknown'))
                
                results[query] = {
                    'total_results': len(search_results),
                    'commercial_chunks': commercial_chunks,
                    'commercial_sources': list(sources_found),
                    'commercial_percentage': (commercial_chunks / len(search_results)) * 100 if search_results else 0
                }
                
                logger.info(f"  📊 {commercial_chunks}/{len(search_results)} chunks comerciais ({results[query]['commercial_percentage']:.1f}%)")
                logger.info(f"  🏢 Fontes: {list(sources_found)}")
                
            except Exception as e:
                logger.error(f"Erro ao testar query '{query}': {e}")
                results[query] = {'error': str(e)}
        
        return results

def main():
    """Função principal para processar e integrar conteúdo comercial."""
    print("\n" + "="*70)
    print("PROCESSAMENTO E INTEGRAÇÃO DE CONTEÚDO COMERCIAL")
    print("="*70)
    
    try:
        # 1. Processar conteúdo comercial
        processor = CommercialContentProcessor()
        processing_stats = processor.process_all_commercial_content()
        
        if not processing_stats:
            print("❌ Nenhum conteúdo para processar")
            return
        
        print("\n" + "-"*50)
        
        # 2. Integrar ao RAG
        integrator = CommercialRAGIntegrator()
        integration_success = integrator.integrate_commercial_content()
        
        if not integration_success:
            print("❌ Falha na integração")
            return
        
        print("\n" + "-"*50)
        
        # 3. Testar capacidades
        test_results = integrator.test_commercial_queries()
        
        print("\n" + "="*70)
        print("📊 RESUMO FINAL")
        print("="*70)
        print(f"✅ Fontes processadas: {processing_stats['sources_processed']}")
        print(f"✅ Chunks criados: {processing_stats['total_chunks']}")
        print(f"✅ Tokens processados: {processing_stats['total_tokens']}")
        print(f"✅ Categorias: {list(processing_stats['categories'].keys())}")
        
        print("\n🔍 RESULTADOS DOS TESTES:")
        for query, result in test_results.items():
            if 'error' not in result:
                print(f"  • {query}")
                print(f"    └─ {result['commercial_chunks']}/{result['total_results']} chunks comerciais ({result['commercial_percentage']:.1f}%)")
        
        print("\n🎉 INTEGRAÇÃO COMERCIAL CONCLUÍDA COM SUCESSO!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        raise

if __name__ == "__main__":
    main()