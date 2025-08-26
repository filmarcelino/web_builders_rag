#!/usr/bin/env python3
"""
Script para processar o corpus de animação coletado
Extrai, limpa e chunka o conteúdo para ingestão no RAG
"""

import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any
import hashlib

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnimationCorpusProcessor:
    def __init__(self, source_dir="corpus/animations", output_dir="processed_corpus/animations"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações de chunking
        self.chunk_size = 1000  # Tamanho ideal para chunks de animação
        self.chunk_overlap = 200  # Overlap para manter contexto
        
        # Palavras-chave importantes para animação
        self.animation_keywords = [
            'animation', 'transition', 'transform', 'keyframes', 'ease', 'duration',
            'timing-function', 'delay', 'iteration-count', 'direction', 'fill-mode',
            'play-state', 'opacity', 'scale', 'rotate', 'translate', 'skew',
            'cubic-bezier', 'linear', 'ease-in', 'ease-out', 'ease-in-out',
            'hover', 'focus', 'active', 'before', 'after', 'nth-child',
            'gsap', 'timeline', 'tween', 'motion', 'parallax', 'scroll',
            'requestAnimationFrame', 'performance', 'fps', 'gpu', 'will-change',
            'backface-visibility', 'perspective', '3d', 'matrix', 'spring',
            'bounce', 'elastic', 'expo', 'circ', 'back', 'sine', 'quad',
            'cubic', 'quart', 'quint', 'loading', 'spinner', 'progress',
            'microinteraction', 'feedback', 'state', 'responsive', 'mobile'
        ]
    
    def process_all_content(self):
        """Processa todo o conteúdo coletado"""
        logger.info("Iniciando processamento do corpus de animação...")
        
        all_chunks = []
        
        # Processa documentações
        doc_chunks = self._process_documentation()
        all_chunks.extend(doc_chunks)
        
        # Processa repositórios
        repo_chunks = self._process_repositories()
        all_chunks.extend(repo_chunks)
        
        # Processa cursos
        course_chunks = self._process_courses()
        all_chunks.extend(course_chunks)
        
        # Processa técnicas
        technique_chunks = self._process_techniques()
        all_chunks.extend(technique_chunks)
        
        # Salva chunks processados
        self._save_processed_chunks(all_chunks)
        
        # Gera relatório
        report = self._generate_processing_report(all_chunks)
        
        logger.info(f"Processamento concluído! Total de chunks: {len(all_chunks)}")
        return report
    
    def _process_documentation(self):
        """Processa documentações HTML"""
        logger.info("Processando documentações...")
        chunks = []
        
        docs_dir = self.source_dir / "documentation"
        for html_file in docs_dir.glob("*.html"):
            try:
                # Carrega metadados
                metadata_file = docs_dir / f"{html_file.stem}_metadata.json"
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Processa HTML
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                doc_chunks = self._extract_chunks_from_html(html_content, metadata)
                chunks.extend(doc_chunks)
                
                logger.info(f"Processado {html_file.name}: {len(doc_chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Erro ao processar {html_file}: {e}")
        
        return chunks
    
    def _process_repositories(self):
        """Processa repositórios clonados"""
        logger.info("Processando repositórios...")
        chunks = []
        
        repos_dir = self.source_dir / "repositories"
        for repo_dir in repos_dir.iterdir():
            if repo_dir.is_dir():
                try:
                    # Carrega metadados
                    metadata_file = repos_dir / f"{repo_dir.name}_metadata.json"
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Processa arquivos do repositório
                    repo_chunks = self._extract_chunks_from_repo(repo_dir, metadata)
                    chunks.extend(repo_chunks)
                    
                    logger.info(f"Processado {repo_dir.name}: {len(repo_chunks)} chunks")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar repositório {repo_dir}: {e}")
        
        return chunks
    
    def _process_courses(self):
        """Processa conteúdo de cursos"""
        logger.info("Processando cursos...")
        chunks = []
        
        courses_dir = self.source_dir / "courses"
        for html_file in courses_dir.glob("*.html"):
            try:
                # Carrega metadados
                metadata_file = courses_dir / f"{html_file.stem}_metadata.json"
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Processa HTML
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                course_chunks = self._extract_chunks_from_html(html_content, metadata, content_type="course")
                chunks.extend(course_chunks)
                
                logger.info(f"Processado {html_file.name}: {len(course_chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Erro ao processar curso {html_file}: {e}")
        
        return chunks
    
    def _process_techniques(self):
        """Processa documentação de técnicas"""
        logger.info("Processando técnicas...")
        chunks = []
        
        techniques_dir = self.source_dir / "techniques"
        for md_file in techniques_dir.glob("*.md"):
            try:
                # Carrega metadados
                metadata_file = techniques_dir / f"{md_file.stem}_metadata.json"
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Processa Markdown
                with open(md_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                technique_chunks = self._extract_chunks_from_markdown(md_content, metadata)
                chunks.extend(technique_chunks)
                
                logger.info(f"Processado {md_file.name}: {len(technique_chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Erro ao processar técnica {md_file}: {e}")
        
        return chunks
    
    def _extract_chunks_from_html(self, html_content: str, metadata: Dict, content_type: str = "documentation") -> List[Dict]:
        """Extrai chunks de conteúdo HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts, styles e outros elementos não úteis
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        chunks = []
        
        # Extrai seções principais
        sections = soup.find_all(['section', 'article', 'div'], class_=re.compile(r'content|main|article|section'))
        
        if not sections:
            # Se não encontrar seções específicas, usa o body
            sections = [soup.find('body')] if soup.find('body') else [soup]
        
        for i, section in enumerate(sections):
            if section:
                text = self._clean_text(section.get_text())
                
                if len(text) > 100:  # Só processa seções com conteúdo substancial
                    section_chunks = self._create_chunks(text, metadata, content_type, section_index=i)
                    chunks.extend(section_chunks)
        
        return chunks
    
    def _extract_chunks_from_repo(self, repo_dir: Path, metadata: Dict) -> List[Dict]:
        """Extrai chunks de repositório"""
        chunks = []
        
        # Arquivos importantes para animação
        important_files = [
            '*.css', '*.scss', '*.sass', '*.less',
            '*.js', '*.ts', '*.jsx', '*.tsx',
            '*.md', '*.txt', '*.json'
        ]
        
        for pattern in important_files:
            for file_path in repo_dir.rglob(pattern):
                try:
                    # Ignora arquivos muito grandes ou de build
                    if file_path.stat().st_size > 1024 * 1024:  # 1MB
                        continue
                    
                    if any(ignore in str(file_path) for ignore in ['node_modules', 'dist', 'build', '.git']):
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Filtra apenas arquivos relacionados a animação
                    if self._is_animation_related(content):
                        file_chunks = self._create_chunks(
                            content, metadata, "repository", 
                            file_path=str(file_path.relative_to(repo_dir))
                        )
                        chunks.extend(file_chunks)
                
                except Exception as e:
                    logger.debug(f"Erro ao processar arquivo {file_path}: {e}")
        
        return chunks
    
    def _extract_chunks_from_markdown(self, md_content: str, metadata: Dict) -> List[Dict]:
        """Extrai chunks de conteúdo Markdown"""
        # Remove metadados YAML se existirem
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', md_content, flags=re.DOTALL)
        
        # Limpa o texto
        text = self._clean_text(content)
        
        return self._create_chunks(text, metadata, "technique")
    
    def _clean_text(self, text: str) -> str:
        """Limpa e normaliza texto"""
        # Remove múltiplas quebras de linha
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove espaços extras
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove caracteres de controle
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text.strip()
    
    def _is_animation_related(self, content: str) -> bool:
        """Verifica se o conteúdo é relacionado a animação"""
        content_lower = content.lower()
        
        # Conta quantas palavras-chave de animação estão presentes
        keyword_count = sum(1 for keyword in self.animation_keywords if keyword in content_lower)
        
        # Considera relacionado se tiver pelo menos 3 palavras-chave
        return keyword_count >= 3
    
    def _create_chunks(self, text: str, metadata: Dict, content_type: str, **kwargs) -> List[Dict]:
        """Cria chunks de texto com metadados"""
        chunks = []
        
        # Divide o texto em chunks
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text.strip()) < 50:  # Ignora chunks muito pequenos
                continue
            
            # Calcula score de relevância para animação
            animation_score = self._calculate_animation_score(chunk_text)
            
            # Cria ID único para o chunk
            chunk_id = hashlib.md5(chunk_text.encode()).hexdigest()[:12]
            
            chunk = {
                "id": f"anim_{chunk_id}",
                "text": chunk_text,
                "metadata": {
                    "source": metadata.get('source', 'unknown'),
                    "content_type": content_type,
                    "description": metadata.get('description', ''),
                    "license": metadata.get('license', ''),
                    "animation_score": animation_score,
                    "chunk_index": len(chunks),
                    **kwargs
                }
            }
            
            chunks.append(chunk)
        
        return chunks
    
    def _calculate_animation_score(self, text: str) -> float:
        """Calcula score de relevância para animação (0-1)"""
        text_lower = text.lower()
        
        # Conta palavras-chave com pesos diferentes
        score = 0
        total_weight = 0
        
        keyword_weights = {
            'animation': 3, 'keyframes': 3, 'transition': 3, 'transform': 3,
            'gsap': 2, 'timeline': 2, 'tween': 2, 'motion': 2,
            'ease': 1, 'duration': 1, 'opacity': 1, 'scale': 1,
            'rotate': 1, 'translate': 1, 'hover': 1, 'focus': 1
        }
        
        for keyword, weight in keyword_weights.items():
            if keyword in text_lower:
                score += weight
            total_weight += weight
        
        return min(score / total_weight, 1.0) if total_weight > 0 else 0
    
    def _save_processed_chunks(self, chunks: List[Dict]):
        """Salva chunks processados em batches"""
        logger.info("Salvando chunks processados...")
        
        batch_size = 1000
        batch_num = 1
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            batch_file = self.output_dir / f"animation_chunks_batch_{batch_num:04d}.json"
            
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "batch_info": {
                        "batch_number": batch_num,
                        "total_chunks": len(batch),
                        "chunk_range": [i, i + len(batch) - 1]
                    },
                    "chunks": batch
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Batch {batch_num} salvo: {len(batch)} chunks")
            batch_num += 1
    
    def _generate_processing_report(self, chunks: List[Dict]) -> Dict:
        """Gera relatório do processamento"""
        logger.info("Gerando relatório de processamento...")
        
        # Estatísticas por tipo de conteúdo
        content_types = {}
        animation_scores = []
        
        for chunk in chunks:
            content_type = chunk['metadata']['content_type']
            content_types[content_type] = content_types.get(content_type, 0) + 1
            animation_scores.append(chunk['metadata']['animation_score'])
        
        # Calcula estatísticas
        avg_score = sum(animation_scores) / len(animation_scores) if animation_scores else 0
        high_quality_chunks = sum(1 for score in animation_scores if score > 0.5)
        
        report = {
            "processing_summary": {
                "total_chunks": len(chunks),
                "content_types": content_types,
                "average_animation_score": round(avg_score, 3),
                "high_quality_chunks": high_quality_chunks,
                "quality_percentage": round((high_quality_chunks / len(chunks)) * 100, 1) if chunks else 0
            },
            "quality_distribution": {
                "excellent (>0.8)": sum(1 for score in animation_scores if score > 0.8),
                "good (0.5-0.8)": sum(1 for score in animation_scores if 0.5 <= score <= 0.8),
                "fair (0.2-0.5)": sum(1 for score in animation_scores if 0.2 <= score < 0.5),
                "poor (<0.2)": sum(1 for score in animation_scores if score < 0.2)
            }
        }
        
        # Salva relatório
        report_file = self.output_dir / "animation_processing_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Relatório salvo em: {report_file}")
        return report

if __name__ == "__main__":
    processor = AnimationCorpusProcessor()
    report = processor.process_all_content()
    
    print("\n=== RELATORIO DE PROCESSAMENTO ===")
    print(f"Total de chunks: {report['processing_summary']['total_chunks']}")
    print(f"Score médio de animação: {report['processing_summary']['average_animation_score']}")
    print(f"Chunks de alta qualidade: {report['processing_summary']['high_quality_chunks']} ({report['processing_summary']['quality_percentage']}%)")
    print("\nDistribuição de qualidade:")
    for quality, count in report['quality_distribution'].items():
        print(f"  {quality}: {count}")
    print("\nProcessamento concluído com sucesso!")