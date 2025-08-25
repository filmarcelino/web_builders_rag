#!/usr/bin/env python3
"""
Script para coletar dados do corpus para alimentar o sistema RAG.
Coleta repositórios Git e documentações web de forma organizada.
"""

import os
import subprocess
import requests
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from typing import List, Dict

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('corpus_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CorpusCollector:
    def __init__(self, base_dir: str = "corpus"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Repositórios Git para clonar
        self.git_repos = {
            'freeCodeCamp': 'https://github.com/freeCodeCamp/freeCodeCamp.git',
            'odin-project': 'https://github.com/TheOdinProject/curriculum.git',
            'web-dev-beginners': 'https://github.com/microsoft/Web-Dev-For-Beginners.git',
            'free-programming-books': 'https://github.com/EbookFoundation/free-programming-books.git',
            'awesome-opensource-apps': 'https://github.com/unicodeveloper/awesome-opensource-apps.git'
        }
        
        # URLs de documentação para scraping
        self.doc_urls = {
            'tailwind': 'https://tailwindcss.com/docs',
            'storybook': 'https://storybook.js.org/docs',
            'radix': 'https://www.radix-ui.com/primitives/docs',
            'shadcn': 'https://ui.shadcn.com/docs',
            'mdn-flexbox': 'https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout',
            'wcag': 'https://www.w3.org/WAI/WCAG22/quickref/',
            'aria': 'https://www.w3.org/WAI/ARIA/apg/'
        }
    
    def clone_git_repos(self) -> None:
        """Clona todos os repositórios Git configurados."""
        logger.info("Iniciando clonagem de repositórios Git...")
        
        git_dir = self.base_dir / "git_repos"
        git_dir.mkdir(exist_ok=True)
        
        for name, url in self.git_repos.items():
            repo_path = git_dir / name
            
            if repo_path.exists():
                logger.info(f"Repositório {name} já existe, fazendo pull...")
                try:
                    subprocess.run(
                        ['git', 'pull'], 
                        cwd=repo_path, 
                        check=True, 
                        capture_output=True
                    )
                    logger.info(f"✓ {name} atualizado com sucesso")
                except subprocess.CalledProcessError as e:
                    logger.error(f"✗ Erro ao atualizar {name}: {e}")
            else:
                logger.info(f"Clonando {name} de {url}...")
                try:
                    subprocess.run(
                        ['git', 'clone', url, str(repo_path)], 
                        check=True, 
                        capture_output=True
                    )
                    logger.info(f"✓ {name} clonado com sucesso")
                except subprocess.CalledProcessError as e:
                    logger.error(f"✗ Erro ao clonar {name}: {e}")
    
    def scrape_documentation(self, name: str, base_url: str, max_pages: int = 100) -> None:
        """Faz scraping de documentação web."""
        logger.info(f"Fazendo scraping de {name} ({base_url})...")
        
        docs_dir = self.base_dir / "documentation" / name
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        visited_urls = set()
        urls_to_visit = [base_url]
        pages_scraped = 0
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        while urls_to_visit and pages_scraped < max_pages:
            url = urls_to_visit.pop(0)
            
            if url in visited_urls:
                continue
                
            visited_urls.add(url)
            
            try:
                response = session.get(url, timeout=10)
                response.raise_for_status()
                
                # Salvar conteúdo HTML
                parsed_url = urlparse(url)
                filename = parsed_url.path.replace('/', '_') or 'index'
                if not filename.endswith('.html'):
                    filename += '.html'
                
                file_path = docs_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # Extrair links para páginas relacionadas
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    
                    # Filtrar apenas links da mesma documentação
                    if full_url.startswith(base_url) and full_url not in visited_urls:
                        urls_to_visit.append(full_url)
                
                pages_scraped += 1
                logger.info(f"✓ Página salva: {filename} ({pages_scraped}/{max_pages})")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"✗ Erro ao processar {url}: {e}")
        
        logger.info(f"✓ Scraping de {name} concluído: {pages_scraped} páginas")
    
    def collect_all_documentation(self) -> None:
        """Coleta toda a documentação configurada."""
        logger.info("Iniciando coleta de documentação...")
        
        for name, url in self.doc_urls.items():
            try:
                self.scrape_documentation(name, url)
            except Exception as e:
                logger.error(f"✗ Erro ao coletar {name}: {e}")
    
    def create_corpus_archive(self) -> None:
        """Cria arquivo compactado do corpus coletado."""
        logger.info("Criando arquivo do corpus...")
        
        try:
            import zipfile
            
            archive_path = Path("corpus-complete.zip")
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in self.base_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.base_dir.parent)
                        zipf.write(file_path, arcname)
            
            logger.info(f"✓ Arquivo criado: {archive_path} ({archive_path.stat().st_size / 1024 / 1024:.1f} MB)")
            
        except Exception as e:
            logger.error(f"✗ Erro ao criar arquivo: {e}")
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Retorna estatísticas da coleta."""
        stats = {
            'total_files': 0,
            'git_repos': 0,
            'doc_pages': 0,
            'total_size_mb': 0
        }
        
        if not self.base_dir.exists():
            return stats
        
        total_size = 0
        for file_path in self.base_dir.rglob('*'):
            if file_path.is_file():
                stats['total_files'] += 1
                total_size += file_path.stat().st_size
                
                if 'git_repos' in str(file_path):
                    stats['git_repos'] += 1
                elif 'documentation' in str(file_path):
                    stats['doc_pages'] += 1
        
        stats['total_size_mb'] = round(total_size / 1024 / 1024, 1)
        return stats
    
    def run_collection(self) -> None:
        """Executa todo o processo de coleta."""
        logger.info("=== INICIANDO COLETA DO CORPUS ===")
        start_time = time.time()
        
        try:
            # Clonar repositórios Git
            self.clone_git_repos()
            
            # Coletar documentação
            self.collect_all_documentation()
            
            # Criar arquivo compactado
            self.create_corpus_archive()
            
            # Mostrar estatísticas
            stats = self.get_collection_stats()
            logger.info("=== ESTATÍSTICAS DA COLETA ===")
            logger.info(f"Total de arquivos: {stats['total_files']:,}")
            logger.info(f"Repositórios Git: {stats['git_repos']:,} arquivos")
            logger.info(f"Páginas de documentação: {stats['doc_pages']:,}")
            logger.info(f"Tamanho total: {stats['total_size_mb']} MB")
            
            elapsed_time = time.time() - start_time
            logger.info(f"Tempo total: {elapsed_time:.1f} segundos")
            logger.info("=== COLETA CONCLUÍDA COM SUCESSO ===")
            
        except Exception as e:
            logger.error(f"✗ Erro durante a coleta: {e}")
            raise

def main():
    """Função principal."""
    collector = CorpusCollector()
    collector.run_collection()

if __name__ == "__main__":
    main()