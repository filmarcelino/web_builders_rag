from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import re
from urllib.parse import urlparse

from config.config import RAGConfig

@dataclass
class ValidationResult:
    """Resultado da validação de metadados"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    quality_score: float
    recommendations: List[str]

class MetadataValidator:
    """Validador de metadados para garantir qualidade e conformidade"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões de URL válidos
        self.valid_url_patterns = [
            r'https?://[\w\.-]+\.[a-z]{2,}',
            r'https://github\.com/[\w\.-]+/[\w\.-]+',
            r'https://[\w\.-]+\.vercel\.app',
            r'https://[\w\.-]+\.netlify\.app'
        ]
        
        # Licenças conhecidas e suas variações
        self.known_licenses = {
            'MIT': ['MIT', 'MIT License', 'mit'],
            'Apache-2.0': ['Apache-2.0', 'Apache 2.0', 'Apache License 2.0', 'apache-2.0'],
            'BSD-3-Clause': ['BSD-3-Clause', 'BSD 3-Clause', 'bsd-3-clause'],
            'GPL-3.0': ['GPL-3.0', 'GPL v3', 'GNU GPL v3'],
            'ISC': ['ISC', 'ISC License', 'isc'],
            'CC0-1.0': ['CC0-1.0', 'CC0', 'Public Domain']
        }
        
        # Stacks válidas
        self.valid_stacks = RAGConfig.SUPPORTED_STACKS
        
        # Categorias válidas
        self.valid_categories = list(RAGConfig.CONTENT_CATEGORIES.keys())
        
        # Níveis de maturidade válidos
        self.valid_maturity_levels = ['alpha', 'beta', 'stable', 'deprecated']
    
    def validate_content(self, content: Dict[str, Any]) -> ValidationResult:
        """Valida conteúdo completo incluindo metadados"""
        errors = []
        warnings = []
        recommendations = []
        
        # Valida estrutura básica
        structure_errors = self._validate_structure(content)
        errors.extend(structure_errors)
        
        # Valida metadados obrigatórios
        if 'metadata' in content:
            metadata_result = self.validate_metadata(content['metadata'])
            errors.extend(metadata_result.errors)
            warnings.extend(metadata_result.warnings)
            recommendations.extend(metadata_result.recommendations)
        else:
            errors.append("Metadados ausentes")
        
        # Valida qualidade do conteúdo
        quality_warnings = self._validate_content_quality(content)
        warnings.extend(quality_warnings)
        
        # Calcula score de qualidade
        quality_score = self._calculate_quality_score(content, errors, warnings)
        
        # Adiciona recomendações baseadas no score
        if quality_score < 0.7:
            recommendations.append("Considere melhorar a qualidade do conteúdo")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score,
            recommendations=recommendations
        )
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> ValidationResult:
        """Valida metadados obrigatórios"""
        errors = []
        warnings = []
        recommendations = []
        
        # Verifica campos obrigatórios
        for required_field in RAGConfig.REQUIRED_METADATA:
            if required_field not in metadata:
                errors.append(f"Campo obrigatório ausente: {required_field}")
            elif not metadata[required_field]:
                errors.append(f"Campo obrigatório vazio: {required_field}")
        
        # Valida campos específicos
        if 'source_url' in metadata:
            url_errors = self._validate_url(metadata['source_url'])
            errors.extend(url_errors)
        
        if 'license' in metadata:
            license_warnings = self._validate_license(metadata['license'])
            warnings.extend(license_warnings)
        
        if 'updated_at' in metadata:
            date_errors = self._validate_date(metadata['updated_at'])
            errors.extend(date_errors)
        
        if 'stack' in metadata:
            stack_errors = self._validate_stack(metadata['stack'])
            errors.extend(stack_errors)
        
        if 'category' in metadata:
            category_errors = self._validate_category(metadata['category'])
            errors.extend(category_errors)
        
        if 'language' in metadata:
            lang_warnings = self._validate_language(metadata['language'])
            warnings.extend(lang_warnings)
        
        if 'maturity' in metadata:
            maturity_errors = self._validate_maturity(metadata['maturity'])
            errors.extend(maturity_errors)
        
        if 'quality_score' in metadata:
            score_errors = self._validate_quality_score(metadata['quality_score'])
            errors.extend(score_errors)
        
        # Recomendações baseadas nos metadados
        recommendations.extend(self._generate_metadata_recommendations(metadata))
        
        quality_score = 1.0 - (len(errors) * 0.2) - (len(warnings) * 0.1)
        quality_score = max(0.0, min(1.0, quality_score))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score,
            recommendations=recommendations
        )
    
    def _validate_structure(self, content: Dict[str, Any]) -> List[str]:
        """Valida estrutura básica do conteúdo"""
        errors = []
        
        required_fields = ['title', 'url', 'content_type', 'sections']
        for field in required_fields:
            if field not in content:
                errors.append(f"Campo estrutural ausente: {field}")
        
        # Valida seções
        if 'sections' in content:
            if not isinstance(content['sections'], list):
                errors.append("Campo 'sections' deve ser uma lista")
            elif len(content['sections']) == 0:
                errors.append("Conteúdo deve ter pelo menos uma seção")
            else:
                for i, section in enumerate(content['sections']):
                    section_errors = self._validate_section_structure(section, i)
                    errors.extend(section_errors)
        
        return errors
    
    def _validate_section_structure(self, section: Dict[str, Any], index: int) -> List[str]:
        """Valida estrutura de uma seção"""
        errors = []
        
        required_section_fields = ['title', 'content', 'section_type']
        for field in required_section_fields:
            if field not in section:
                errors.append(f"Seção {index}: campo ausente '{field}'")
        
        # Valida conteúdo mínimo
        if 'content' in section and len(section['content'].strip()) < 50:
            errors.append(f"Seção {index}: conteúdo muito curto (mínimo 50 caracteres)")
        
        return errors
    
    def _validate_url(self, url: str) -> List[str]:
        """Valida URL"""
        errors = []
        
        if not url:
            errors.append("URL não pode estar vazia")
            return errors
        
        # Verifica formato básico
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            errors.append(f"URL inválida: {url}")
        
        # Verifica se é HTTPS (recomendado)
        if parsed.scheme != 'https':
            errors.append(f"URL deve usar HTTPS: {url}")
        
        return errors
    
    def _validate_license(self, license_str: str) -> List[str]:
        """Valida licença"""
        warnings = []
        
        if not license_str:
            warnings.append("Licença não especificada")
            return warnings
        
        # Normaliza licença
        normalized_license = self._normalize_license(license_str)
        
        if normalized_license not in self.known_licenses:
            warnings.append(f"Licença desconhecida: {license_str}")
        
        # Verifica se é uma licença preferida
        if normalized_license not in RAGConfig.PREFERRED_LICENSES:
            warnings.append(f"Licença não está na lista preferida: {license_str}")
        
        return warnings
    
    def _validate_date(self, date_str: str) -> List[str]:
        """Valida formato de data"""
        errors = []
        
        try:
            # Tenta parsear ISO format
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Verifica se não é muito antiga (mais de 2 anos)
            two_years_ago = datetime.now() - timedelta(days=730)
            if date_obj < two_years_ago:
                errors.append(f"Conteúdo muito antigo: {date_str}")
            
            # Verifica se não é no futuro
            if date_obj > datetime.now():
                errors.append(f"Data no futuro: {date_str}")
                
        except ValueError:
            errors.append(f"Formato de data inválido: {date_str}")
        
        return errors
    
    def _validate_stack(self, stack: str) -> List[str]:
        """Valida stack"""
        errors = []
        
        if stack.lower() not in [s.lower() for s in self.valid_stacks]:
            errors.append(f"Stack não suportada: {stack}")
        
        return errors
    
    def _validate_category(self, category: str) -> List[str]:
        """Valida categoria"""
        errors = []
        
        if category not in self.valid_categories:
            errors.append(f"Categoria inválida: {category}")
        
        return errors
    
    def _validate_language(self, language: str) -> List[str]:
        """Valida idioma"""
        warnings = []
        
        valid_languages = ['pt-br', 'en', 'es', 'fr']
        if language.lower() not in valid_languages:
            warnings.append(f"Idioma não reconhecido: {language}")
        
        return warnings
    
    def _validate_maturity(self, maturity: str) -> List[str]:
        """Valida nível de maturidade"""
        errors = []
        
        if maturity.lower() not in self.valid_maturity_levels:
            errors.append(f"Nível de maturidade inválido: {maturity}")
        
        return errors
    
    def _validate_quality_score(self, score: float) -> List[str]:
        """Valida score de qualidade"""
        errors = []
        
        if not isinstance(score, (int, float)):
            errors.append("Quality score deve ser numérico")
        elif score < 0.0 or score > 1.0:
            errors.append("Quality score deve estar entre 0.0 e 1.0")
        
        return errors
    
    def _validate_content_quality(self, content: Dict[str, Any]) -> List[str]:
        """Valida qualidade do conteúdo"""
        warnings = []
        
        # Verifica se há seções suficientes
        sections = content.get('sections', [])
        if len(sections) < 2:
            warnings.append("Conteúdo tem poucas seções (recomendado: 2+)")
        
        # Verifica se há exemplos de código
        has_code = any(
            section.get('code_blocks', []) 
            for section in sections
        )
        if not has_code:
            warnings.append("Conteúdo não possui exemplos de código")
        
        # Verifica estimativa de tokens
        total_tokens = content.get('estimated_tokens', 0)
        if total_tokens < 200:
            warnings.append("Conteúdo muito curto (menos de 200 tokens estimados)")
        elif total_tokens > 4000:
            warnings.append("Conteúdo muito longo (mais de 4000 tokens estimados)")
        
        return warnings
    
    def _calculate_quality_score(self, content: Dict[str, Any], 
                               errors: List[str], warnings: List[str]) -> float:
        """Calcula score de qualidade baseado em múltiplos fatores"""
        base_score = 1.0
        
        # Penalidades por erros e warnings
        base_score -= len(errors) * 0.2
        base_score -= len(warnings) * 0.05
        
        # Bônus por qualidade do conteúdo
        sections = content.get('sections', [])
        
        # Bônus por ter múltiplas seções
        if len(sections) >= 3:
            base_score += 0.1
        
        # Bônus por ter código
        has_code = any(
            section.get('code_blocks', []) 
            for section in sections
        )
        if has_code:
            base_score += 0.1
        
        # Bônus por seções importantes
        important_sections = ['usage', 'examples', 'api']
        section_types = [s.get('section_type', '') for s in sections]
        for important in important_sections:
            if important in section_types:
                base_score += 0.05
        
        # Bônus por metadados completos
        metadata = content.get('metadata', {})
        if len(metadata) >= len(RAGConfig.REQUIRED_METADATA):
            base_score += 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _normalize_license(self, license_str: str) -> str:
        """Normaliza string de licença"""
        license_str = license_str.strip()
        
        for standard, variations in self.known_licenses.items():
            if license_str in variations:
                return standard
        
        return license_str
    
    def _generate_metadata_recommendations(self, metadata: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos metadados"""
        recommendations = []
        
        # Recomendação de licença
        license_str = metadata.get('license', '')
        if license_str and license_str not in RAGConfig.PREFERRED_LICENSES:
            recommendations.append(
                f"Considere usar uma licença preferida: {', '.join(RAGConfig.PREFERRED_LICENSES)}"
            )
        
        # Recomendação de maturidade
        maturity = metadata.get('maturity', '')
        if maturity == 'alpha':
            recommendations.append("Conteúdo em alpha - considere aguardar versão mais estável")
        
        # Recomendação de qualidade
        quality_score = metadata.get('quality_score', 0.0)
        if quality_score < 0.5:
            recommendations.append("Score de qualidade baixo - revisar conteúdo")
        
        return recommendations
    
    def validate_batch(self, contents: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Valida múltiplos conteúdos em lote"""
        results = []
        
        for i, content in enumerate(contents):
            try:
                result = self.validate_content(content)
                results.append(result)
                
                if not result.is_valid:
                    self.logger.warning(f"Conteúdo {i} inválido: {result.errors}")
                    
            except Exception as e:
                self.logger.error(f"Erro ao validar conteúdo {i}: {str(e)}")
                results.append(ValidationResult(
                    is_valid=False,
                    errors=[f"Erro de validação: {str(e)}"],
                    warnings=[],
                    quality_score=0.0,
                    recommendations=[]
                ))
        
        valid_count = sum(1 for r in results if r.is_valid)
        self.logger.info(f"Validação em lote: {valid_count}/{len(results)} válidos")
        
        return results