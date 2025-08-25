#!/usr/bin/env python3
"""
Pipeline de processamento de dados do corpus para o sistema RAG.
Normaliza, chunka e prepara os dados para ingestão.
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import markdown
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import tiktoken

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('corpus_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Representa um chunk de documento processado."""
    id: str
    source_file: str
    source_type: str  # 'git_repo', 'documentation', 'markdown', 'code'
    title: str
    content: str
    metadata: Dict
    token_count: int
    chunk_index: int
    total_chunks: int

class CorpusProcessor:
    def __init__(self, corpus_dir: str = "corpus", output_dir: str = "processed_corpus"):
        self.corpus_dir = Path(corpus_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configurações de chunking
        self.max_chunk_size = 500   # tokens (reduzido para evitar limite do modelo)
        self.chunk_overlap = 100    # tokens
        
        # Inicializar tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Extensões de arquivo suportadas
        self.supported_extensions = {
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.txt': 'text',
            '.html': 'html',
            '.htm': 'html',
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'jsx',
            '.tsx': 'tsx',
            '.css': 'css',
            '.scss': 'scss',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.rst': 'rst'
        }
        
        # Padrões para ignorar
        self.ignore_patterns = [
            r'\.git/',
            r'node_modules/',
            r'__pycache__/',
            r'\.pytest_cache/',
            r'dist/',
            r'build/',
            r'\.vscode/',
            r'\.idea/',
            r'\.(png|jpg|jpeg|gif|svg|ico|pdf|zip|tar|gz)$',
            r'package-lock\.json$',
            r'yarn\.lock$'
        ]
    
    def should_ignore_file(self, file_path: Path) -> bool:
        """Verifica se um arquivo deve ser ignorado."""
        file_str = str(file_path)
        return any(re.search(pattern, file_str, re.IGNORECASE) for pattern in self.ignore_patterns)
    
    def extract_text_from_html(self, html_content: str) -> Tuple[str, str]:
        """Extrai texto e título de conteúdo HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remover scripts e estilos
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extrair título
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        else:
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text().strip()
        
        # Extrair texto principal
        text = soup.get_text()
        
        # Limpar texto
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        return text, title
    
    def extract_text_from_markdown(self, md_content: str) -> Tuple[str, str]:
        """Extrai texto e título de conteúdo Markdown."""
        # Converter para HTML primeiro
        html = markdown.markdown(md_content)
        text, title = self.extract_text_from_html(html)
        
        # Se não encontrou título no HTML, procurar no markdown
        if not title:
            lines = md_content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
        
        return text, title
    
    def count_tokens(self, text: str) -> int:
        """Conta tokens no texto."""
        try:
            return len(self.tokenizer.encode(text))
        except:
            # Fallback: aproximação baseada em palavras
            return len(text.split()) * 1.3
    
    def chunk_text(self, text: str, metadata: Dict) -> List[str]:
        """Divide texto em chunks baseado em tokens."""
        if not text.strip():
            return []
        
        # Dividir por parágrafos primeiro
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for paragraph in paragraphs:
            paragraph_tokens = self.count_tokens(paragraph)
            
            # Se o parágrafo sozinho é muito grande, dividir por sentenças
            if paragraph_tokens > self.max_chunk_size:
                sentences = re.split(r'[.!?]+', paragraph)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    sentence_tokens = self.count_tokens(sentence)
                    
                    if current_tokens + sentence_tokens > self.max_chunk_size and current_chunk:
                        chunks.append(current_chunk.strip())
                        # Manter overlap
                        overlap_text = self._get_overlap_text(current_chunk)
                        current_chunk = overlap_text + sentence
                        current_tokens = self.count_tokens(current_chunk)
                    else:
                        current_chunk += " " + sentence if current_chunk else sentence
                        current_tokens += sentence_tokens
            else:
                # Verificar se cabe no chunk atual
                if current_tokens + paragraph_tokens > self.max_chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    # Manter overlap
                    overlap_text = self._get_overlap_text(current_chunk)
                    current_chunk = overlap_text + "\n\n" + paragraph
                    current_tokens = self.count_tokens(current_chunk)
                else:
                    current_chunk += "\n\n" + paragraph if current_chunk else paragraph
                    current_tokens += paragraph_tokens
        
        # Adicionar último chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Obtém texto de overlap para manter contexto entre chunks."""
        words = text.split()
        overlap_words = int(self.chunk_overlap / 1.3)  # Aproximação de tokens para palavras
        
        if len(words) <= overlap_words:
            return text
        
        return " ".join(words[-overlap_words:])
    
    def process_file(self, file_path: Path) -> List[DocumentChunk]:
        """Processa um arquivo individual."""
        if self.should_ignore_file(file_path):
            return []
        
        try:
            # Determinar tipo de arquivo
            extension = file_path.suffix.lower()
            if extension not in self.supported_extensions:
                return []
            
            file_type = self.supported_extensions[extension]
            
            # Ler conteúdo
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extrair texto e título baseado no tipo
            if file_type == 'html':
                text, title = self.extract_text_from_html(content)
            elif file_type == 'markdown':
                text, title = self.extract_text_from_markdown(content)
            else:
                text = content
                title = file_path.stem
            
            # Determinar tipo de fonte
            source_type = 'git_repo' if 'git_repos' in str(file_path) else 'documentation'
            
            # Metadados
            metadata = {
                'file_extension': extension,
                'file_type': file_type,
                'file_size': file_path.stat().st_size,
                'relative_path': str(file_path.relative_to(self.corpus_dir)),
                'source_type': source_type
            }
            
            # Chunkar texto
            chunks = self.chunk_text(text, metadata)
            
            # Criar objetos DocumentChunk
            document_chunks = []
            for i, chunk_text in enumerate(chunks):
                chunk_id = hashlib.md5(
                    f"{file_path}_{i}_{chunk_text[:100]}".encode()
                ).hexdigest()
                
                chunk = DocumentChunk(
                    id=chunk_id,
                    source_file=str(file_path),
                    source_type=source_type,
                    title=title or file_path.stem,
                    content=chunk_text,
                    metadata=metadata,
                    token_count=self.count_tokens(chunk_text),
                    chunk_index=i,
                    total_chunks=len(chunks)
                )
                document_chunks.append(chunk)
            
            return document_chunks
            
        except Exception as e:
            logger.error(f"Erro ao processar {file_path}: {e}")
            return []
    
    def process_corpus(self, max_workers: int = 4) -> List[DocumentChunk]:
        """Processa todo o corpus usando processamento paralelo."""
        logger.info("Iniciando processamento do corpus...")
        
        # Encontrar todos os arquivos
        all_files = []
        for file_path in self.corpus_dir.rglob('*'):
            if file_path.is_file():
                all_files.append(file_path)
        
        logger.info(f"Encontrados {len(all_files)} arquivos para processar")
        
        # Processar arquivos em paralelo
        all_chunks = []
        processed_files = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(self.process_file, file_path): file_path 
                            for file_path in all_files}
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    chunks = future.result()
                    all_chunks.extend(chunks)
                    processed_files += 1
                    
                    if processed_files % 100 == 0:
                        logger.info(f"Processados {processed_files}/{len(all_files)} arquivos")
                        
                except Exception as e:
                    logger.error(f"Erro ao processar {file_path}: {e}")
        
        logger.info(f"Processamento concluído: {len(all_chunks)} chunks gerados")
        return all_chunks
    
    def save_processed_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Salva chunks processados em arquivos JSON."""
        logger.info("Salvando chunks processados...")
        
        # Salvar em batches para evitar arquivos muito grandes
        batch_size = 1000
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_file = self.output_dir / f"chunks_batch_{i // batch_size + 1:04d}.json"
            
            batch_data = [asdict(chunk) for chunk in batch]
            
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(batch_data, f, ensure_ascii=False, indent=2)
        
        # Salvar metadados do processamento
        metadata = {
            'total_chunks': len(chunks),
            'total_batches': (len(chunks) + batch_size - 1) // batch_size,
            'batch_size': batch_size,
            'processing_config': {
                'max_chunk_size': self.max_chunk_size,
                'chunk_overlap': self.chunk_overlap,
                'supported_extensions': list(self.supported_extensions.keys())
            },
            'statistics': self._calculate_statistics(chunks)
        }
        
        with open(self.output_dir / "processing_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Chunks salvos em {metadata['total_batches']} batches")
    
    def _calculate_statistics(self, chunks: List[DocumentChunk]) -> Dict:
        """Calcula estatísticas dos chunks processados."""
        if not chunks:
            return {}
        
        token_counts = [chunk.token_count for chunk in chunks]
        source_types = {}
        file_types = {}
        
        for chunk in chunks:
            source_types[chunk.source_type] = source_types.get(chunk.source_type, 0) + 1
            file_type = chunk.metadata.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            'total_chunks': len(chunks),
            'avg_token_count': sum(token_counts) / len(token_counts),
            'min_token_count': min(token_counts),
            'max_token_count': max(token_counts),
            'source_type_distribution': source_types,
            'file_type_distribution': file_types
        }
    
    def run_processing(self) -> None:
        """Executa todo o pipeline de processamento."""
        logger.info("=== INICIANDO PROCESSAMENTO DO CORPUS ===")
        
        if not self.corpus_dir.exists():
            logger.error(f"Diretório do corpus não encontrado: {self.corpus_dir}")
            return
        
        try:
            # Processar corpus
            chunks = self.process_corpus()
            
            if not chunks:
                logger.warning("Nenhum chunk foi gerado")
                return
            
            # Salvar chunks processados
            self.save_processed_chunks(chunks)
            
            # Mostrar estatísticas finais
            stats = self._calculate_statistics(chunks)
            logger.info("=== ESTATÍSTICAS DO PROCESSAMENTO ===")
            logger.info(f"Total de chunks: {stats['total_chunks']:,}")
            logger.info(f"Média de tokens por chunk: {stats['avg_token_count']:.1f}")
            logger.info(f"Distribuição por tipo de fonte: {stats['source_type_distribution']}")
            logger.info(f"Distribuição por tipo de arquivo: {stats['file_type_distribution']}")
            logger.info("=== PROCESSAMENTO CONCLUÍDO ===")
            
        except Exception as e:
            logger.error(f"Erro durante o processamento: {e}")
            raise

def main():
    """Função principal."""
    processor = CorpusProcessor()
    processor.run_processing()

if __name__ == "__main__":
    main()