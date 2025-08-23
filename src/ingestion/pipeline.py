import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass

from .collector import SourceCollector, SourceInfo
from .normalizer import ContentNormalizer
from .validator import MetadataValidator, ValidationResult
from config.config import RAGConfig

@dataclass
class IngestionStats:
    """Estatísticas do processo de ingestão"""
    total_sources: int
    collected_sources: int
    normalized_sources: int
    valid_sources: int
    failed_sources: int
    total_sections: int
    total_tokens: int
    processing_time_seconds: float
    errors: List[str]
    warnings: List[str]

class IngestionPipeline:
    """Pipeline completo de ingestão do sistema RAG"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.collector = None
        self.normalizer = ContentNormalizer()
        self.validator = MetadataValidator()
        
        # Estatísticas
        self.stats = None
        
        # Resultados intermediários
        self.raw_contents = []
        self.normalized_contents = []
        self.validated_contents = []
    
    async def run_full_pipeline(self, custom_sources: Optional[List[SourceInfo]] = None) -> IngestionStats:
        """Executa pipeline completo de ingestão"""
        start_time = datetime.now()
        
        try:
            self.logger.info("Iniciando pipeline de ingestão completo")
            
            # Fase 1: Coleta
            await self._run_collection_phase(custom_sources)
            
            # Fase 2: Normalização
            await self._run_normalization_phase()
            
            # Fase 3: Validação
            await self._run_validation_phase()
            
            # Fase 4: Persistência
            await self._run_persistence_phase()
            
            # Calcula estatísticas finais
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            self.stats = self._calculate_stats(processing_time)
            
            # Gera relatório
            await self._generate_report()
            
            self.logger.info(f"Pipeline concluído em {processing_time:.2f}s")
            return self.stats
            
        except Exception as e:
            self.logger.error(f"Erro no pipeline de ingestão: {str(e)}")
            raise
    
    async def _run_collection_phase(self, custom_sources: Optional[List[SourceInfo]] = None):
        """Fase 1: Coleta de fontes"""
        self.logger.info("Fase 1: Iniciando coleta de fontes")
        
        async with SourceCollector() as collector:
            self.collector = collector
            
            if custom_sources:
                self.logger.info(f"Usando {len(custom_sources)} fontes customizadas")
                sources = custom_sources
            else:
                self.logger.info("Usando fontes seed padrão")
                sources = collector.get_seed_sources()
            
            # Coleta todas as fontes
            collected_contents = []
            for source in sources:
                try:
                    content = await collector.collect_source(source)
                    if content:
                        collected_contents.append(content)
                        self.logger.info(f"Coletado: {source.url}")
                    else:
                        self.logger.warning(f"Falha na coleta: {source.url}")
                        
                except Exception as e:
                    self.logger.error(f"Erro ao coletar {source.url}: {str(e)}")
            
            self.raw_contents = collected_contents
            self.logger.info(f"Fase 1 concluída: {len(collected_contents)} fontes coletadas")
    
    async def _run_normalization_phase(self):
        """Fase 2: Normalização de conteúdo"""
        self.logger.info("Fase 2: Iniciando normalização de conteúdo")
        
        if not self.raw_contents:
            self.logger.warning("Nenhum conteúdo bruto para normalizar")
            return
        
        # Normaliza todos os conteúdos
        normalized_contents = []
        for i, raw_content in enumerate(self.raw_contents):
            try:
                normalized = self.normalizer.normalize_content(raw_content)
                if normalized:
                    normalized_contents.append(normalized)
                    self.logger.debug(f"Normalizado {i+1}/{len(self.raw_contents)}")
                else:
                    self.logger.warning(f"Falha na normalização do item {i+1}")
                    
            except Exception as e:
                self.logger.error(f"Erro ao normalizar item {i+1}: {str(e)}")
        
        self.normalized_contents = normalized_contents
        self.logger.info(f"Fase 2 concluída: {len(normalized_contents)} conteúdos normalizados")
    
    async def _run_validation_phase(self):
        """Fase 3: Validação de metadados e qualidade"""
        self.logger.info("Fase 3: Iniciando validação")
        
        if not self.normalized_contents:
            self.logger.warning("Nenhum conteúdo normalizado para validar")
            return
        
        # Valida todos os conteúdos
        validation_results = self.validator.validate_batch(self.normalized_contents)
        
        validated_contents = []
        for i, (content, result) in enumerate(zip(self.normalized_contents, validation_results)):
            if result.is_valid:
                # Atualiza quality_score nos metadados
                content['metadata']['quality_score'] = result.quality_score
                validated_contents.append(content)
                self.logger.debug(f"Validado {i+1}/{len(self.normalized_contents)} (score: {result.quality_score:.2f})")
            else:
                self.logger.warning(f"Item {i+1} inválido: {result.errors}")
        
        self.validated_contents = validated_contents
        self.logger.info(f"Fase 3 concluída: {len(validated_contents)} conteúdos válidos")
    
    async def _run_persistence_phase(self):
        """Fase 4: Persistência dos dados processados"""
        self.logger.info("Fase 4: Iniciando persistência")
        
        if not self.validated_contents:
            self.logger.warning("Nenhum conteúdo válido para persistir")
            return
        
        # Salva conteúdos processados
        processed_dir = RAGConfig.PROCESSED_DATA_DIR
        os.makedirs(processed_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salva cada conteúdo individualmente
        for i, content in enumerate(self.validated_contents):
            try:
                # Cria nome de arquivo baseado na URL e timestamp
                url_hash = str(hash(content['url']))[-8:]
                filename = f"content_{url_hash}_{timestamp}.json"
                filepath = os.path.join(processed_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
                
                self.logger.debug(f"Salvo: {filepath}")
                
            except Exception as e:
                self.logger.error(f"Erro ao salvar conteúdo {i+1}: {str(e)}")
        
        # Salva índice consolidado
        index_file = os.path.join(processed_dir, f"index_{timestamp}.json")
        index_data = {
            "timestamp": timestamp,
            "total_contents": len(self.validated_contents),
            "contents": [
                {
                    "title": content['title'],
                    "url": content['url'],
                    "stack": content['metadata']['stack'],
                    "category": content['metadata']['category'],
                    "quality_score": content['metadata']['quality_score'],
                    "sections_count": len(content['sections']),
                    "estimated_tokens": content.get('estimated_tokens', 0)
                }
                for content in self.validated_contents
            ]
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Fase 4 concluída: {len(self.validated_contents)} conteúdos persistidos")
    
    def _calculate_stats(self, processing_time: float) -> IngestionStats:
        """Calcula estatísticas do processo"""
        total_sections = sum(
            len(content.get('sections', [])) 
            for content in self.validated_contents
        )
        
        total_tokens = sum(
            content.get('estimated_tokens', 0) 
            for content in self.validated_contents
        )
        
        return IngestionStats(
            total_sources=len(self.raw_contents) if self.raw_contents else 0,
            collected_sources=len(self.raw_contents) if self.raw_contents else 0,
            normalized_sources=len(self.normalized_contents) if self.normalized_contents else 0,
            valid_sources=len(self.validated_contents) if self.validated_contents else 0,
            failed_sources=len(self.raw_contents) - len(self.validated_contents) if self.raw_contents and self.validated_contents else 0,
            total_sections=total_sections,
            total_tokens=total_tokens,
            processing_time_seconds=processing_time,
            errors=[],  # Coletar de logs se necessário
            warnings=[]  # Coletar de logs se necessário
        )
    
    async def _generate_report(self):
        """Gera relatório de ingestão"""
        if not self.stats:
            return
        
        report = {
            "ingestion_report": {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_sources": self.stats.total_sources,
                    "successful_sources": self.stats.valid_sources,
                    "failed_sources": self.stats.failed_sources,
                    "success_rate": (self.stats.valid_sources / self.stats.total_sources * 100) if self.stats.total_sources > 0 else 0,
                    "total_sections": self.stats.total_sections,
                    "total_tokens": self.stats.total_tokens,
                    "processing_time_seconds": self.stats.processing_time_seconds
                },
                "breakdown_by_category": self._get_category_breakdown(),
                "breakdown_by_stack": self._get_stack_breakdown(),
                "breakdown_by_license": self._get_license_breakdown(),
                "quality_distribution": self._get_quality_distribution(),
                "recommendations": self._get_recommendations()
            }
        }
        
        # Salva relatório
        report_file = os.path.join(
            RAGConfig.PROCESSED_DATA_DIR, 
            f"ingestion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Relatório salvo: {report_file}")
    
    def _get_category_breakdown(self) -> Dict[str, int]:
        """Breakdown por categoria"""
        breakdown = {}
        for content in self.validated_contents:
            category = content['metadata'].get('category', 'unknown')
            breakdown[category] = breakdown.get(category, 0) + 1
        return breakdown
    
    def _get_stack_breakdown(self) -> Dict[str, int]:
        """Breakdown por stack"""
        breakdown = {}
        for content in self.validated_contents:
            stack = content['metadata'].get('stack', 'unknown')
            breakdown[stack] = breakdown.get(stack, 0) + 1
        return breakdown
    
    def _get_license_breakdown(self) -> Dict[str, int]:
        """Breakdown por licença"""
        breakdown = {}
        for content in self.validated_contents:
            license_str = content['metadata'].get('license', 'unknown')
            breakdown[license_str] = breakdown.get(license_str, 0) + 1
        return breakdown
    
    def _get_quality_distribution(self) -> Dict[str, int]:
        """Distribuição de qualidade"""
        distribution = {
            "high (0.8-1.0)": 0,
            "medium (0.6-0.8)": 0,
            "low (0.4-0.6)": 0,
            "very_low (0.0-0.4)": 0
        }
        
        for content in self.validated_contents:
            score = content['metadata'].get('quality_score', 0.0)
            if score >= 0.8:
                distribution["high (0.8-1.0)"] += 1
            elif score >= 0.6:
                distribution["medium (0.6-0.8)"] += 1
            elif score >= 0.4:
                distribution["low (0.4-0.6)"] += 1
            else:
                distribution["very_low (0.0-0.4)"] += 1
        
        return distribution
    
    def _get_recommendations(self) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        if self.stats.failed_sources > 0:
            recommendations.append(
                f"Revisar {self.stats.failed_sources} fontes que falharam na ingestão"
            )
        
        # Verifica qualidade média
        if self.validated_contents:
            avg_quality = sum(
                content['metadata'].get('quality_score', 0.0) 
                for content in self.validated_contents
            ) / len(self.validated_contents)
            
            if avg_quality < 0.7:
                recommendations.append(
                    f"Qualidade média baixa ({avg_quality:.2f}) - considerar curadoria adicional"
                )
        
        # Verifica cobertura de categorias
        categories = self._get_category_breakdown()
        missing_categories = set(RAGConfig.CONTENT_CATEGORIES.keys()) - set(categories.keys())
        if missing_categories:
            recommendations.append(
                f"Categorias sem conteúdo: {', '.join(missing_categories)}"
            )
        
        return recommendations
    
    async def run_incremental_update(self, new_sources: List[SourceInfo]) -> IngestionStats:
        """Executa atualização incremental com novas fontes"""
        self.logger.info(f"Iniciando atualização incremental com {len(new_sources)} fontes")
        return await self.run_full_pipeline(new_sources)
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Retorna resumo do processamento atual"""
        if not self.stats:
            return {"status": "not_processed"}
        
        return {
            "status": "completed",
            "stats": {
                "total_sources": self.stats.total_sources,
                "valid_sources": self.stats.valid_sources,
                "total_sections": self.stats.total_sections,
                "total_tokens": self.stats.total_tokens,
                "processing_time": self.stats.processing_time_seconds
            },
            "quality_summary": self._get_quality_distribution(),
            "category_coverage": self._get_category_breakdown()
        }