#!/usr/bin/env python3
"""
Script para coletar recursos de animação para o sistema RAG
Coleta documentações, repositórios, cursos e técnicas de animação
"""

import os
import json
import requests
import subprocess
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnimationResourceCollector:
    def __init__(self, base_dir="corpus/animations"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Estrutura de diretórios
        self.docs_dir = self.base_dir / "documentation"
        self.repos_dir = self.base_dir / "repositories"
        self.courses_dir = self.base_dir / "courses"
        self.techniques_dir = self.base_dir / "techniques"
        
        for dir_path in [self.docs_dir, self.repos_dir, self.courses_dir, self.techniques_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def collect_documentation(self):
        """Coleta documentações de animação"""
        logger.info("Coletando documentações de animação...")
        
        docs_sources = {
            "mdn_animations": {
                "url": "https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Animations",
                "description": "MDN CSS Animations Documentation",
                "license": "CC BY-SA 4.0"
            },
            "mdn_transitions": {
                "url": "https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Transitions",
                "description": "MDN CSS Transitions Documentation",
                "license": "CC BY-SA 4.0"
            },
            "mdn_web_animations": {
                "url": "https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API",
                "description": "MDN Web Animations API Documentation",
                "license": "CC BY-SA 4.0"
            },
            "gsap_docs": {
                "url": "https://greensock.com/docs/",
                "description": "GreenSock (GSAP) Documentation",
                "license": "No-Charge License"
            },
            "motion_one": {
                "url": "https://motion.dev/",
                "description": "Motion One Documentation",
                "license": "MIT"
            },
            "tailwind_animations": {
                "url": "https://tailwindcss.com/docs/animation",
                "description": "Tailwind CSS Animation Utilities",
                "license": "MIT"
            }
        }
        
        for doc_name, doc_info in docs_sources.items():
            self._collect_web_documentation(doc_name, doc_info)
    
    def collect_repositories(self):
        """Coleta repositórios de animação do GitHub"""
        logger.info("Coletando repositórios de animação...")
        
        repos = {
            "animate-css": {
                "url": "https://github.com/animate-css/animate.css",
                "description": "CSS Animation Library",
                "license": "Hippocratic 2.1"
            },
            "hover-css": {
                "url": "https://github.com/IanLunn/Hover",
                "description": "CSS3 Hover Effects",
                "license": "MIT"
            },
            "anime-js": {
                "url": "https://github.com/juliangarnier/anime",
                "description": "JavaScript Animation Engine",
                "license": "MIT"
            },
            "three-js": {
                "url": "https://github.com/mrdoob/three.js",
                "description": "3D JavaScript Library",
                "license": "MIT"
            },
            "lottie-web": {
                "url": "https://github.com/airbnb/lottie-web",
                "description": "Lottie Animation Library",
                "license": "MIT"
            },
            "spinkit": {
                "url": "https://github.com/tobiasahlin/SpinKit",
                "description": "CSS Spinners Collection",
                "license": "MIT"
            }
        }
        
        for repo_name, repo_info in repos.items():
            self._clone_repository(repo_name, repo_info)
    
    def collect_courses_and_ebooks(self):
        """Coleta cursos e eBooks gratuitos"""
        logger.info("Coletando cursos e eBooks sobre animação...")
        
        courses = {
            "material_design_motion": {
                "url": "https://material.io/design/motion/",
                "description": "Google Material Design Motion Guidelines",
                "license": "Open Source"
            },
            "freecodecamp_animations": {
                "url": "https://www.freecodecamp.org/news/tag/animation/",
                "description": "FreeCodeCamp Animation Tutorials",
                "license": "CC BY-NC-SA"
            },
            "css_tricks_animations": {
                "url": "https://css-tricks.com/tag/animation/",
                "description": "CSS-Tricks Animation Articles",
                "license": "Educational Use"
            }
        }
        
        for course_name, course_info in courses.items():
            self._collect_course_content(course_name, course_info)
    
    def collect_techniques_and_practices(self):
        """Documenta técnicas e melhores práticas"""
        logger.info("Documentando técnicas e melhores práticas...")
        
        techniques_content = {
            "motion_design_principles": {
                "title": "Princípios de Motion Design",
                "content": [
                    "Clareza: Animações devem comunicar claramente o propósito",
                    "Sutileza: Movimentos suaves e não intrusivos",
                    "Consistência: Padrões uniformes em toda a aplicação",
                    "Rapidez: Durações curtas para manter a fluidez",
                    "Propósito: Cada animação deve ter uma função específica"
                ]
            },
            "performance_best_practices": {
                "title": "Melhores Práticas de Performance",
                "content": [
                    "Usar transform e opacity para animações suaves",
                    "Evitar animações em propriedades que causam reflow (top, left, width, height)",
                    "Manter 60fps com will-change e transform3d",
                    "Usar requestAnimationFrame para animações JavaScript",
                    "Implementar prefers-reduced-motion para acessibilidade"
                ]
            },
            "css_animation_techniques": {
                "title": "Técnicas de Animação CSS",
                "content": [
                    "@keyframes para animações complexas",
                    "transition para mudanças de estado simples",
                    "animation-timing-function para easing personalizado",
                    "animation-fill-mode para controlar estados inicial/final",
                    "animation-play-state para controle de reprodução"
                ]
            },
            "javascript_animation_patterns": {
                "title": "Padrões de Animação JavaScript",
                "content": [
                    "GSAP para animações complexas e timeline",
                    "Web Animations API para controle nativo",
                    "Intersection Observer para animações on-scroll",
                    "RAF (requestAnimationFrame) para animações customizadas",
                    "CSS-in-JS para animações dinâmicas"
                ]
            }
        }
        
        for technique_name, technique_info in techniques_content.items():
            self._save_technique_documentation(technique_name, technique_info)
    
    def _collect_web_documentation(self, doc_name, doc_info):
        """Coleta documentação web"""
        try:
            logger.info(f"Coletando documentação: {doc_name}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(doc_info['url'], headers=headers, timeout=30)
            response.raise_for_status()
            
            # Salva o conteúdo HTML
            doc_file = self.docs_dir / f"{doc_name}.html"
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Salva metadados
            metadata = {
                "source": doc_info['url'],
                "description": doc_info['description'],
                "license": doc_info['license'],
                "collected_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "file_path": str(doc_file)
            }
            
            metadata_file = self.docs_dir / f"{doc_name}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Documentação {doc_name} coletada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao coletar documentação {doc_name}: {e}")
    
    def _clone_repository(self, repo_name, repo_info):
        """Clona repositório do GitHub"""
        try:
            logger.info(f"Clonando repositório: {repo_name}")
            
            repo_dir = self.repos_dir / repo_name
            
            if repo_dir.exists():
                logger.info(f"Repositório {repo_name} já existe, atualizando...")
                subprocess.run(['git', 'pull'], cwd=repo_dir, check=True)
            else:
                subprocess.run([
                    'git', 'clone', '--depth', '1', 
                    repo_info['url'], str(repo_dir)
                ], check=True)
            
            # Salva metadados
            metadata = {
                "source": repo_info['url'],
                "description": repo_info['description'],
                "license": repo_info['license'],
                "cloned_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "local_path": str(repo_dir)
            }
            
            metadata_file = self.repos_dir / f"{repo_name}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Repositório {repo_name} clonado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao clonar repositório {repo_name}: {e}")
    
    def _collect_course_content(self, course_name, course_info):
        """Coleta conteúdo de cursos"""
        try:
            logger.info(f"Coletando curso: {course_name}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(course_info['url'], headers=headers, timeout=30)
            response.raise_for_status()
            
            # Salva o conteúdo
            course_file = self.courses_dir / f"{course_name}.html"
            with open(course_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Salva metadados
            metadata = {
                "source": course_info['url'],
                "description": course_info['description'],
                "license": course_info['license'],
                "collected_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "file_path": str(course_file)
            }
            
            metadata_file = self.courses_dir / f"{course_name}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Curso {course_name} coletado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao coletar curso {course_name}: {e}")
    
    def _save_technique_documentation(self, technique_name, technique_info):
        """Salva documentação de técnicas"""
        try:
            logger.info(f"Documentando técnica: {technique_name}")
            
            # Cria conteúdo markdown
            content = f"# {technique_info['title']}\n\n"
            for item in technique_info['content']:
                content += f"- {item}\n"
            
            technique_file = self.techniques_dir / f"{technique_name}.md"
            with open(technique_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Salva metadados
            metadata = {
                "title": technique_info['title'],
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "file_path": str(technique_file),
                "type": "technique_documentation"
            }
            
            metadata_file = self.techniques_dir / f"{technique_name}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Técnica {technique_name} documentada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao documentar técnica {technique_name}: {e}")
    
    def generate_collection_report(self):
        """Gera relatório da coleta"""
        logger.info("Gerando relatório da coleta...")
        
        report = {
            "collection_summary": {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "total_docs": len(list(self.docs_dir.glob("*.html"))),
                "total_repos": len(list(self.repos_dir.glob("*_metadata.json"))),
                "total_courses": len(list(self.courses_dir.glob("*.html"))),
                "total_techniques": len(list(self.techniques_dir.glob("*.md")))
            },
            "collected_resources": {
                "documentation": [f.stem for f in self.docs_dir.glob("*.html")],
                "repositories": [f.stem.replace('_metadata', '') for f in self.repos_dir.glob("*_metadata.json")],
                "courses": [f.stem for f in self.courses_dir.glob("*.html")],
                "techniques": [f.stem for f in self.techniques_dir.glob("*.md")]
            }
        }
        
        report_file = self.base_dir / "collection_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Relatório salvo em: {report_file}")
        return report
    
    def run_full_collection(self):
        """Executa coleta completa de recursos"""
        logger.info("Iniciando coleta completa de recursos de animação...")
        
        try:
            self.collect_documentation()
            self.collect_repositories()
            self.collect_courses_and_ebooks()
            self.collect_techniques_and_practices()
            
            report = self.generate_collection_report()
            
            logger.info("Coleta completa finalizada com sucesso!")
            logger.info(f"Total coletado: {report['collection_summary']}")
            
            return report
            
        except Exception as e:
            logger.error(f"Erro durante a coleta: {e}")
            raise

if __name__ == "__main__":
    collector = AnimationResourceCollector()
    report = collector.run_full_collection()
    
    print("\n=== RELATORIO DA COLETA ===")
    print(f"Documentacoes: {report['collection_summary']['total_docs']}")
    print(f"Repositorios: {report['collection_summary']['total_repos']}")
    print(f"Cursos: {report['collection_summary']['total_courses']}")
    print(f"Tecnicas: {report['collection_summary']['total_techniques']}")
    print("\nColeta concluida com sucesso!")