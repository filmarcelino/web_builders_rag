#!/usr/bin/env python3
"""
Obsolescence Detector - Detector de Obsolescência

Este módulo detecta automaticamente conteúdo obsoleto e desatualizado
no sistema RAG, usando padrões de tecnologia e análise temporal.
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict, Counter
import requests
from packaging import version

logger = logging.getLogger(__name__)

@dataclass
class ObsolescenceRule:
    """Regra para detectar obsolescência"""
    name: str
    patterns: List[str]
    severity: str  # low, medium, high, critical
    description: str
    replacement_suggestion: Optional[str] = None
    deprecation_date: Optional[str] = None
    end_of_life_date: Optional[str] = None
    
@dataclass
class ObsolescenceDetection:
    """Detecção de obsolescência em uma fonte"""
    source_id: str
    rule_name: str
    severity: str
    description: str
    matched_content: str
    line_number: Optional[int] = None
    replacement_suggestion: Optional[str] = None
    confidence: float = 0.0
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
@dataclass
class ObsolescenceReport:
    """Relatório de obsolescência"""
    generated_at: str
    total_sources_scanned: int
    sources_with_issues: int
    total_detections: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    detections: List[ObsolescenceDetection]
    summary_by_rule: Dict[str, int]
    recommendations: List[str] = field(default_factory=list)
    
class ObsolescenceDetector:
    """Detector automático de obsolescência"""
    
    def __init__(self, data_dir: str = "data/governance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Regras de obsolescência
        self.rules: Dict[str, ObsolescenceRule] = {}
        self.detections: List[ObsolescenceDetection] = []
        
        # Cache de versões atuais
        self.version_cache: Dict[str, str] = {}
        self.cache_expiry = timedelta(hours=24)
        self.last_cache_update: Optional[datetime] = None
        
        self._initialize_rules()
        self._load_detection_data()
    
    def _initialize_rules(self) -> None:
        """Inicializa regras de detecção de obsolescência"""
        
        # JavaScript/Node.js
        self.rules["node_old_versions"] = ObsolescenceRule(
            name="node_old_versions",
            patterns=[
                r"node\s*[v]?([0-9]+)\.([0-9]+)",
                r"nodejs\s*[v]?([0-9]+)\.([0-9]+)",
                r"engines.*node.*([0-9]+)\.([0-9]+)"
            ],
            severity="high",
            description="Versão antiga do Node.js detectada",
            replacement_suggestion="Atualizar para Node.js 18+ (LTS)",
            end_of_life_date="2023-04-30"  # Node 14 EOL
        )
        
        self.rules["npm_old_versions"] = ObsolescenceRule(
            name="npm_old_versions",
            patterns=[
                r"npm\s*[v]?([0-9]+)\.([0-9]+)",
                r"npm.*([0-9]+)\.([0-9]+)"
            ],
            severity="medium",
            description="Versão antiga do npm detectada",
            replacement_suggestion="Atualizar para npm 9+ ou considerar pnpm/yarn"
        )
        
        # React
        self.rules["react_old_versions"] = ObsolescenceRule(
            name="react_old_versions",
            patterns=[
                r"react.*([0-9]+)\.([0-9]+)",
                r"from.*react",
                r"React\.([A-Z][a-zA-Z]+)",  # React.Component, etc.
                r"componentDidMount|componentWillMount|componentWillReceiveProps"
            ],
            severity="high",
            description="Versão antiga do React ou padrões obsoletos detectados",
            replacement_suggestion="Atualizar para React 18+ e usar hooks"
        )
        
        self.rules["react_class_components"] = ObsolescenceRule(
            name="react_class_components",
            patterns=[
                r"class\s+\w+\s+extends\s+React\.Component",
                r"class\s+\w+\s+extends\s+Component",
                r"componentDidMount\s*\(",
                r"componentWillMount\s*\(",
                r"componentWillReceiveProps\s*\(",
                r"componentWillUpdate\s*\("
            ],
            severity="medium",
            description="Componentes de classe React (padrão obsoleto)",
            replacement_suggestion="Migrar para componentes funcionais com hooks"
        )
        
        # Next.js
        self.rules["nextjs_old_versions"] = ObsolescenceRule(
            name="nextjs_old_versions",
            patterns=[
                r"next.*([0-9]+)\.([0-9]+)",
                r"from.*next/",
                r"getServerSideProps|getStaticProps",
                r"pages/api/",
                r"_app\.js|_document\.js"
            ],
            severity="high",
            description="Versão antiga do Next.js ou padrões obsoletos",
            replacement_suggestion="Atualizar para Next.js 13+ com App Router"
        )
        
        # CSS/Styling
        self.rules["css_obsolete_properties"] = ObsolescenceRule(
            name="css_obsolete_properties",
            patterns=[
                r"-webkit-box-orient",
                r"-webkit-line-clamp",
                r"filter:\s*progid",
                r"-ms-filter",
                r"zoom:\s*[0-9.]+"
            ],
            severity="medium",
            description="Propriedades CSS obsoletas detectadas",
            replacement_suggestion="Usar propriedades CSS modernas e flexbox/grid"
        )
        
        # Build Tools
        self.rules["webpack_old_versions"] = ObsolescenceRule(
            name="webpack_old_versions",
            patterns=[
                r"webpack.*([0-9]+)\.([0-9]+)",
                r"babel-loader.*([0-9]+)\.([0-9]+)",
                r"css-loader.*([0-9]+)\.([0-9]+)",
                r"webpack\.config\.js",
                r"module\.exports\s*=\s*{"
            ],
            severity="high",
            description="Versão antiga do Webpack detectada",
            replacement_suggestion="Atualizar para Webpack 5+ ou considerar Vite"
        )
        
        self.rules["babel_old_versions"] = ObsolescenceRule(
            name="babel_old_versions",
            patterns=[
                r"babel-core.*([1-6])\.([0-9]+)",
                r"@babel/core.*([1-6])\.([0-9]+)",
                r"babel-preset-env",
                r"babel-preset-react"
            ],
            severity="medium",
            description="Versão antiga do Babel ou presets obsoletos",
            replacement_suggestion="Atualizar para @babel/core 7+ e presets modernos"
        )
        
        # Testing
        self.rules["jest_old_versions"] = ObsolescenceRule(
            name="jest_old_versions",
            patterns=[
                r"jest.*([0-9]+)\.([0-9]+)",
                r"@testing-library/react.*([0-9]+)\.([0-9]+)",
                r"enzyme.*([0-9]+)\.([0-9]+)",
                r"shallow|mount|render",
                r"jest\.fn\(\)"
            ],
            severity="medium",
            description="Versão antiga do Jest ou ferramentas de teste obsoletas",
            replacement_suggestion="Atualizar para Jest 29+ e React Testing Library"
        )
        
        # Database
        self.rules["mongodb_old_versions"] = ObsolescenceRule(
            name="mongodb_old_versions",
            patterns=[
                r"mysql.*([0-9]+)\.([0-9]+)",
                r"mongodb.*([0-9]+)\.([0-9]+)",
                r"mongoose.*([0-9]+)\.([0-9]+)",
                r"SELECT\s+\*\s+FROM",
                r"mysql_"
            ],
            severity="medium",
            description="Versão antiga do MongoDB/Mongoose detectada",
            replacement_suggestion="Atualizar para versões mais recentes"
        )
        
        # Security
        self.rules["security_vulnerabilities"] = ObsolescenceRule(
            name="security_vulnerabilities",
            patterns=[
                r"bcrypt.*([0-9]+)\.([0-9]+)",
                r"jsonwebtoken.*([0-9]+)\.([0-9]+)",
                r"passport.*([0-9]+)\.([0-9]+)",
                r"md5|sha1",
                r"eval\("
            ],
            severity="critical",
            description="Pacotes com vulnerabilidades conhecidas",
            replacement_suggestion="Substituir por alternativas seguras (date-fns, axios, sass)"
        )
        
        # Python
        self.rules["python_old_versions"] = ObsolescenceRule(
            name="python_old_versions",
            patterns=[
                r"python.*([0-9]+)\.([0-9]+)",
                r"django.*([0-9]+)\.([0-9]+)",
                r"flask.*([0-9]+)\.([0-9]+)",
                r"import\s+urllib2",
                r"print\s+\w+"
            ],
            severity="critical",
            description="Versão antiga do Python ou sintaxe obsoleta",
            replacement_suggestion="Atualizar para Python 3.8+",
            end_of_life_date="2020-01-01"  # Python 2 EOL
        )
        
        # Docker
        self.rules["docker_old_practices"] = ObsolescenceRule(
            name="docker_old_practices",
            patterns=[
                r"docker.*([0-9]+)\.([0-9]+)",
                r"FROM\s+ubuntu:14\.04",
                r"FROM\s+node:10",
                r"MAINTAINER",
                r"ADD\s+\."
            ],
            severity="medium",
            description="Práticas obsoletas do Docker detectadas",
            replacement_suggestion="Usar imagens base atuais e LABEL ao invés de MAINTAINER"
        )
        
        # General deprecated APIs
        self.rules["deprecated_apis"] = ObsolescenceRule(
            name="deprecated_apis",
            patterns=[
                r"componentWillMount",
                r"componentWillReceiveProps",
                r"componentWillUpdate",
                r"UNSAFE_componentWillMount",
                r"findDOMNode",
                r"ReactDOM\.render",
                r"String\.prototype\.substr",
                r"new Date\(\)\.getYear\(\)"
            ],
            severity="high",
            description="APIs depreciadas detectadas",
            replacement_suggestion="Usar APIs modernas recomendadas"
        )
        
        logger.info(f"Inicializadas {len(self.rules)} regras de obsolescência")
    
    def scan_source(self, source_id: str, content: str, metadata: Dict[str, Any]) -> List[ObsolescenceDetection]:
        """Escaneia uma fonte em busca de obsolescência"""
        detections = []
        
        try:
            lines = content.split('\n')
            
            for rule_name, rule in self.rules.items():
                for pattern in rule.patterns:
                    try:
                        # Busca no conteúdo completo
                        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                        
                        for match in matches:
                            # Encontra número da linha
                            line_number = content[:match.start()].count('\n') + 1
                            
                            # Extrai contexto
                            matched_content = match.group(0)
                            if line_number <= len(lines):
                                matched_content = lines[line_number - 1].strip()
                            
                            # Calcula confiança baseada no padrão
                            confidence = self._calculate_confidence(rule, match, content)
                            
                            # Verifica se é realmente obsoleto (para versões)
                            if self._is_version_obsolete(rule_name, match, content):
                                detection = ObsolescenceDetection(
                                    source_id=source_id,
                                    rule_name=rule_name,
                                    severity=rule.severity,
                                    description=rule.description,
                                    matched_content=matched_content,
                                    line_number=line_number,
                                    replacement_suggestion=rule.replacement_suggestion,
                                    confidence=confidence
                                )
                                detections.append(detection)
                    
                    except re.error as e:
                        logger.warning(f"Erro no padrão regex '{pattern}': {e}")
                        continue
            
            # Adiciona detecções à lista global
            self.detections.extend(detections)
            
            if detections:
                logger.info(f"Detectadas {len(detections)} obsolescências em {source_id}")
            
            return detections
            
        except Exception as e:
            logger.error(f"Erro ao escanear fonte {source_id}: {e}")
            return []
    
    def scan_multiple_sources(self, sources: Dict[str, Dict[str, Any]]) -> Dict[str, List[ObsolescenceDetection]]:
        """Escaneia múltiplas fontes"""
        results = {}
        
        try:
            for source_id, source_data in sources.items():
                content = source_data.get('content', '')
                metadata = source_data.get('metadata', {})
                
                detections = self.scan_source(source_id, content, metadata)
                if detections:
                    results[source_id] = detections
            
            logger.info(f"Escaneadas {len(sources)} fontes, {len(results)} com problemas")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao escanear múltiplas fontes: {e}")
            return {}
    
    def generate_obsolescence_report(self) -> ObsolescenceReport:
        """Gera relatório de obsolescência"""
        try:
            # Conta detecções por severidade
            severity_counts = Counter(d.severity for d in self.detections)
            
            # Conta fontes únicas com problemas
            sources_with_issues = len(set(d.source_id for d in self.detections))
            
            # Conta detecções por regra
            rule_counts = Counter(d.rule_name for d in self.detections)
            
            # Gera recomendações
            recommendations = self._generate_obsolescence_recommendations()
            
            report = ObsolescenceReport(
                generated_at=datetime.now().isoformat(),
                total_sources_scanned=len(set(d.source_id for d in self.detections)),
                sources_with_issues=sources_with_issues,
                total_detections=len(self.detections),
                critical_issues=severity_counts.get('critical', 0),
                high_issues=severity_counts.get('high', 0),
                medium_issues=severity_counts.get('medium', 0),
                low_issues=severity_counts.get('low', 0),
                detections=self.detections.copy(),
                summary_by_rule=dict(rule_counts),
                recommendations=recommendations
            )
            
            # Salva relatório
            self._save_obsolescence_report(report)
            
            logger.info(f"Relatório de obsolescência gerado: {len(self.detections)} detecções")
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de obsolescência: {e}")
            raise
    
    def get_critical_issues(self) -> List[ObsolescenceDetection]:
        """Retorna apenas problemas críticos"""
        return [d for d in self.detections if d.severity == 'critical']
    
    def get_issues_by_source(self, source_id: str) -> List[ObsolescenceDetection]:
        """Retorna problemas de uma fonte específica"""
        return [d for d in self.detections if d.source_id == source_id]
    
    def get_issues_by_rule(self, rule_name: str) -> List[ObsolescenceDetection]:
        """Retorna problemas de uma regra específica"""
        return [d for d in self.detections if d.rule_name == rule_name]
    
    def add_custom_rule(self, rule: ObsolescenceRule) -> None:
        """Adiciona regra customizada"""
        self.rules[rule.name] = rule
        logger.info(f"Regra customizada adicionada: {rule.name}")
    
    def update_version_cache(self) -> None:
        """Atualiza cache de versões atuais"""
        try:
            # Simula busca de versões atuais (em produção, usar APIs reais)
            current_versions = {
                "node": "18.17.0",
                "npm": "9.6.7",
                "react": "18.2.0",
                "nextjs": "13.4.0",
                "webpack": "5.88.0",
                "jest": "29.5.0",
                "python": "3.11.0"
            }
            
            self.version_cache.update(current_versions)
            self.last_cache_update = datetime.now()
            
            logger.info("Cache de versões atualizado")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar cache de versões: {e}")
    
    def _calculate_confidence(self, rule: ObsolescenceRule, match: re.Match, content: str) -> float:
        """Calcula confiança da detecção"""
        confidence = 0.5  # Base
        
        try:
            # Aumenta confiança para padrões específicos
            if rule.severity == 'critical':
                confidence += 0.3
            elif rule.severity == 'high':
                confidence += 0.2
            elif rule.severity == 'medium':
                confidence += 0.1
            
            # Aumenta confiança se há contexto claro
            matched_text = match.group(0).lower()
            
            # Padrões que aumentam confiança
            high_confidence_patterns = [
                'package.json', 'dependencies', 'devdependencies',
                'import', 'require', 'from', 'dockerfile'
            ]
            
            for pattern in high_confidence_patterns:
                if pattern in content.lower():
                    confidence += 0.1
                    break
            
            # Diminui confiança para comentários
            if '//' in matched_text or '/*' in matched_text or '#' in matched_text:
                confidence -= 0.2
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Erro ao calcular confiança: {e}")
            return 0.5
    
    def _is_version_obsolete(self, rule_name: str, match: re.Match, content: str) -> bool:
        """Verifica se uma versão é realmente obsoleta"""
        try:
            # Para regras de versão, extrai e compara versões
            if 'version' in rule_name:
                version_match = re.search(r'([0-9]+)\.([0-9]+)', match.group(0))
                if version_match:
                    major, minor = int(version_match.group(1)), int(version_match.group(2))
                    
                    # Define versões mínimas aceitáveis
                    min_versions = {
                        'node_old_versions': (16, 0),
                        'react_old_versions': (17, 0),
                        'nextjs_old_versions': (12, 0),
                        'webpack_old_versions': (5, 0),
                        'python_old_versions': (3, 8)
                    }
                    
                    if rule_name in min_versions:
                        min_major, min_minor = min_versions[rule_name]
                        return major < min_major or (major == min_major and minor < min_minor)
            
            # Para outras regras, sempre considera obsoleto se encontrado
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar obsolescência de versão: {e}")
            return True
    
    def _generate_obsolescence_recommendations(self) -> List[str]:
        """Gera recomendações baseadas nas detecções"""
        recommendations = []
        
        try:
            # Analisa problemas críticos
            critical_issues = self.get_critical_issues()
            if critical_issues:
                recommendations.append(
                    f"URGENTE: Corrigir {len(critical_issues)} problemas críticos de segurança"
                )
            
            # Analisa por regra
            rule_counts = Counter(d.rule_name for d in self.detections)
            
            for rule_name, count in rule_counts.most_common(5):
                rule = self.rules.get(rule_name)
                if rule and rule.replacement_suggestion:
                    recommendations.append(
                        f"{rule.description}: {count} ocorrências - {rule.replacement_suggestion}"
                    )
            
            # Recomendações gerais
            if len(self.detections) > 50:
                recommendations.append(
                    "Considerar auditoria completa do código para modernização"
                )
            
            # Analisa fontes mais problemáticas
            source_counts = Counter(d.source_id for d in self.detections)
            problematic_sources = [s for s, c in source_counts.items() if c > 5]
            
            if problematic_sources:
                recommendations.append(
                    f"Priorizar atualização de {len(problematic_sources)} fontes com múltiplos problemas"
                )
            
            return recommendations[:10]  # Limita a 10 recomendações
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            return []
    
    def _save_obsolescence_report(self, report: ObsolescenceReport) -> None:
        """Salva relatório de obsolescência"""
        try:
            report_file = self.data_dir / f"obsolescence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Converte para dict serializável
            report_dict = {
                "generated_at": report.generated_at,
                "total_sources_scanned": report.total_sources_scanned,
                "sources_with_issues": report.sources_with_issues,
                "total_detections": report.total_detections,
                "critical_issues": report.critical_issues,
                "high_issues": report.high_issues,
                "medium_issues": report.medium_issues,
                "low_issues": report.low_issues,
                "summary_by_rule": report.summary_by_rule,
                "recommendations": report.recommendations,
                "detections": [
                    {
                        "source_id": d.source_id,
                        "rule_name": d.rule_name,
                        "severity": d.severity,
                        "description": d.description,
                        "matched_content": d.matched_content,
                        "line_number": d.line_number,
                        "replacement_suggestion": d.replacement_suggestion,
                        "confidence": d.confidence,
                        "detected_at": d.detected_at
                    }
                    for d in report.detections
                ]
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Relatório de obsolescência salvo: {report_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")
    
    def _load_detection_data(self) -> None:
        """Carrega dados de detecção salvos"""
        try:
            detection_file = self.data_dir / "obsolescence_data.json"
            
            if detection_file.exists():
                with open(detection_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Carrega detecções (apenas as recentes)
                cutoff_date = datetime.now() - timedelta(days=7)
                
                for detection_data in data.get("detections", []):
                    detected_at = datetime.fromisoformat(detection_data["detected_at"])
                    if detected_at > cutoff_date:
                        detection = ObsolescenceDetection(**detection_data)
                        self.detections.append(detection)
                
                # Carrega cache de versões
                self.version_cache = data.get("version_cache", {})
                
                cache_update_str = data.get("last_cache_update")
                if cache_update_str:
                    self.last_cache_update = datetime.fromisoformat(cache_update_str)
                
                logger.info(f"Dados de detecção carregados: {len(self.detections)} detecções")
                
        except Exception as e:
            logger.warning(f"Erro ao carregar dados de detecção: {e}")
    
    def save_detection_data(self) -> None:
        """Salva dados de detecção"""
        try:
            detection_file = self.data_dir / "obsolescence_data.json"
            
            data = {
                "saved_at": datetime.now().isoformat(),
                "last_cache_update": self.last_cache_update.isoformat() if self.last_cache_update else None,
                "version_cache": self.version_cache,
                "detections": [
                    {
                        "source_id": d.source_id,
                        "rule_name": d.rule_name,
                        "severity": d.severity,
                        "description": d.description,
                        "matched_content": d.matched_content,
                        "line_number": d.line_number,
                        "replacement_suggestion": d.replacement_suggestion,
                        "confidence": d.confidence,
                        "detected_at": d.detected_at
                    }
                    for d in self.detections
                ]
            }
            
            with open(detection_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Dados de detecção salvos: {detection_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados de detecção: {e}")
    
    def clear_old_detections(self, days: int = 30) -> None:
        """Remove detecções antigas"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            old_count = len(self.detections)
            self.detections = [
                d for d in self.detections
                if datetime.fromisoformat(d.detected_at) > cutoff_date
            ]
            
            removed_count = old_count - len(self.detections)
            if removed_count > 0:
                logger.info(f"Removidas {removed_count} detecções antigas")
                
        except Exception as e:
            logger.error(f"Erro ao limpar detecções antigas: {e}")