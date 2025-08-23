import re
import html
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from bs4 import BeautifulSoup, NavigableString
import markdown
from datetime import datetime

@dataclass
class NormalizedSection:
    """Seção normalizada de conteúdo"""
    title: str
    content: str
    section_type: str
    tokens_estimate: int
    code_blocks: List[str]
    links: List[Dict[str, str]]
    importance_score: float

class ContentNormalizer:
    """Normalizador de conteúdo para o sistema RAG"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões para limpeza
        self.noise_patterns = [
            r'\s+',  # Múltiplos espaços
            r'\n{3,}',  # Múltiplas quebras de linha
            r'\t+',  # Múltiplas tabs
            r'<!--.*?-->',  # Comentários HTML
            r'\[\d+\]',  # Referências numéricas
        ]
        
        # Elementos HTML a remover
        self.remove_elements = [
            'script', 'style', 'nav', 'header', 'footer', 
            'aside', 'advertisement', 'banner', 'cookie'
        ]
        
        # Seções importantes para priorizar
        self.important_sections = {
            'usage': 1.0,
            'examples': 0.9,
            'api': 0.8,
            'props': 0.8,
            'accessibility': 0.7,
            'installation': 0.6,
            'configuration': 0.6,
            'gotchas': 0.5
        }
    
    def normalize_content(self, raw_content: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza conteúdo bruto coletado"""
        try:
            self.logger.info(f"Normalizando conteúdo: {raw_content.get('title', 'Sem título')}")
            
            normalized_sections = []
            
            # Processa cada seção
            for section in raw_content.get('sections', []):
                normalized_section = self._normalize_section(section)
                if normalized_section and self._is_section_useful(normalized_section):
                    normalized_sections.append(normalized_section)
            
            # Se não há seções, tenta extrair do conteúdo bruto
            if not normalized_sections and 'raw_html' in raw_content:
                normalized_sections = self._extract_from_raw_html(raw_content['raw_html'])
            
            return {
                'title': self._clean_title(raw_content.get('title', '')),
                'url': raw_content.get('url', ''),
                'content_type': raw_content.get('content_type', 'unknown'),
                'sections': [self._section_to_dict(s) for s in normalized_sections],
                'metadata': raw_content.get('metadata', {}),
                'normalized_at': datetime.now().isoformat(),
                'total_sections': len(normalized_sections),
                'estimated_tokens': sum(s.tokens_estimate for s in normalized_sections)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao normalizar conteúdo: {str(e)}")
            return None
    
    def _normalize_section(self, section: Dict[str, Any]) -> Optional[NormalizedSection]:
        """Normaliza uma seção individual"""
        try:
            title = self._clean_text(section.get('title', ''))
            content = self._clean_text(section.get('content', ''))
            section_type = section.get('type', 'general')
            
            if not content or len(content.strip()) < 50:
                return None
            
            # Extrai blocos de código
            code_blocks = self._extract_code_blocks(content)
            
            # Extrai links
            links = self._extract_links(content)
            
            # Remove código do conteúdo principal para evitar duplicação
            clean_content = self._remove_code_blocks(content)
            
            # Estima tokens (aproximadamente 4 caracteres por token)
            tokens_estimate = len(clean_content) // 4
            
            # Calcula score de importância
            importance_score = self._calculate_importance_score(
                section_type, title, clean_content, code_blocks
            )
            
            return NormalizedSection(
                title=title,
                content=clean_content,
                section_type=section_type,
                tokens_estimate=tokens_estimate,
                code_blocks=code_blocks,
                links=links,
                importance_score=importance_score
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao normalizar seção: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Limpa texto removendo ruído"""
        if not text:
            return ''
        
        # Decodifica HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags se houver
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        
        # Aplica padrões de limpeza
        for pattern in self.noise_patterns:
            text = re.sub(pattern, ' ', text, flags=re.MULTILINE | re.DOTALL)
        
        # Normaliza espaços
        text = re.sub(r'\s+', ' ', text)
        
        # Remove espaços no início e fim
        text = text.strip()
        
        return text
    
    def _clean_title(self, title: str) -> str:
        """Limpa título"""
        title = self._clean_text(title)
        
        # Remove prefixos comuns
        prefixes_to_remove = [
            'Documentation - ',
            'Docs - ',
            'Guide - ',
            'Tutorial - '
        ]
        
        for prefix in prefixes_to_remove:
            if title.startswith(prefix):
                title = title[len(prefix):]
        
        return title.strip()
    
    def _extract_code_blocks(self, content: str) -> List[str]:
        """Extrai blocos de código do conteúdo"""
        code_blocks = []
        
        # Padrões para diferentes tipos de código
        patterns = [
            r'```[\w]*\n([\s\S]*?)```',  # Markdown code blocks
            r'<code[^>]*>([\s\S]*?)</code>',  # HTML code tags
            r'<pre[^>]*>([\s\S]*?)</pre>',  # HTML pre tags
            r'`([^`\n]+)`',  # Inline code
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                clean_code = self._clean_text(match).strip()
                if clean_code and len(clean_code) > 10:
                    code_blocks.append(clean_code)
        
        return code_blocks
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extrai links do conteúdo"""
        links = []
        
        # Padrão para links markdown
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        for text, url in markdown_links:
            links.append({'text': text.strip(), 'url': url.strip()})
        
        # Padrão para URLs simples
        url_pattern = r'https?://[^\s<>"]+'
        urls = re.findall(url_pattern, content)
        for url in urls:
            if not any(link['url'] == url for link in links):
                links.append({'text': url, 'url': url})
        
        return links
    
    def _remove_code_blocks(self, content: str) -> str:
        """Remove blocos de código do conteúdo"""
        # Remove markdown code blocks
        content = re.sub(r'```[\w]*\n[\s\S]*?```', '[CODE_BLOCK]', content)
        
        # Remove HTML code/pre tags
        content = re.sub(r'<(code|pre)[^>]*>[\s\S]*?</\1>', '[CODE_BLOCK]', content)
        
        # Remove inline code
        content = re.sub(r'`[^`\n]+`', '[INLINE_CODE]', content)
        
        return content
    
    def _calculate_importance_score(self, section_type: str, title: str, 
                                  content: str, code_blocks: List[str]) -> float:
        """Calcula score de importância da seção"""
        base_score = self.important_sections.get(section_type.lower(), 0.3)
        
        # Bônus por ter exemplos de código
        if code_blocks:
            base_score += 0.2
        
        # Bônus por palavras-chave importantes no título
        important_keywords = [
            'example', 'usage', 'how to', 'tutorial', 'guide',
            'api', 'props', 'accessibility', 'best practice'
        ]
        
        title_lower = title.lower()
        keyword_bonus = sum(0.1 for keyword in important_keywords 
                          if keyword in title_lower)
        
        # Penalidade por conteúdo muito curto
        if len(content) < 200:
            base_score *= 0.7
        
        # Bônus por conteúdo substancial
        elif len(content) > 1000:
            base_score *= 1.2
        
        return min(1.0, base_score + keyword_bonus)
    
    def _is_section_useful(self, section: NormalizedSection) -> bool:
        """Verifica se uma seção é útil para incluir no índice"""
        # Critérios mínimos
        if len(section.content) < 50:
            return False
        
        if section.importance_score < 0.2:
            return False
        
        # Rejeita seções que são apenas navegação ou metadata
        navigation_indicators = [
            'table of contents', 'navigation', 'breadcrumb',
            'next page', 'previous page', 'edit this page'
        ]
        
        content_lower = section.content.lower()
        if any(indicator in content_lower for indicator in navigation_indicators):
            return False
        
        return True
    
    def _extract_from_raw_html(self, raw_html: str) -> List[NormalizedSection]:
        """Extrai seções do HTML bruto quando não há seções estruturadas"""
        sections = []
        
        try:
            soup = BeautifulSoup(raw_html, 'html.parser')
            
            # Remove elementos de ruído
            for element_type in self.remove_elements:
                for element in soup.find_all(element_type):
                    element.decompose()
            
            # Procura por headings e extrai conteúdo
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                title = heading.get_text().strip()
                content = self._get_content_after_heading(heading)
                
                if content and len(content) > 100:
                    section = NormalizedSection(
                        title=title,
                        content=self._clean_text(content),
                        section_type='general',
                        tokens_estimate=len(content) // 4,
                        code_blocks=self._extract_code_blocks(content),
                        links=self._extract_links(content),
                        importance_score=0.5
                    )
                    
                    if self._is_section_useful(section):
                        sections.append(section)
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair do HTML bruto: {str(e)}")
        
        return sections
    
    def _get_content_after_heading(self, heading) -> str:
        """Extrai conteúdo após um heading até o próximo heading"""
        content_parts = []
        current = heading.next_sibling
        
        while current:
            if current.name and current.name.startswith('h'):
                break
            
            if isinstance(current, NavigableString):
                text = str(current).strip()
                if text:
                    content_parts.append(text)
            elif hasattr(current, 'get_text'):
                text = current.get_text().strip()
                if text:
                    content_parts.append(text)
            
            current = current.next_sibling
        
        return '\n'.join(content_parts)
    
    def _section_to_dict(self, section: NormalizedSection) -> Dict[str, Any]:
        """Converte NormalizedSection para dicionário"""
        return {
            'title': section.title,
            'content': section.content,
            'section_type': section.section_type,
            'tokens_estimate': section.tokens_estimate,
            'code_blocks': section.code_blocks,
            'links': section.links,
            'importance_score': section.importance_score
        }
    
    def normalize_batch(self, raw_contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normaliza múltiplos conteúdos em lote"""
        normalized = []
        
        for raw_content in raw_contents:
            result = self.normalize_content(raw_content)
            if result:
                normalized.append(result)
        
        self.logger.info(f"Normalizados {len(normalized)} de {len(raw_contents)} conteúdos")
        return normalized