#!/usr/bin/env python3
"""
Sistema de Ciclo de Atualização Automática
Configura atualizações semanais incrementais e revisões mensais
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path
import json

from ..ingestion.collector import SourceCollector
from ..indexing.index_manager import IndexManager
from ..governance.source_analyzer import SourceAnalyzer
from ..governance.obsolescence_detector import ObsolescenceDetector
from ..governance.coverage_monitor import CoverageMonitor
from ..observability.metrics_collector import MetricsCollector
from ..observability.logging_manager import LoggingManager

class UpdateScheduler:
    """Gerenciador de ciclos de atualização automática"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/update_schedule.json"
        self.logger = LoggingManager().get_logger("update_scheduler")
        
        # Componentes do sistema
        self.data_collector = SourceCollector()
        self.index_manager = IndexManager(api_key="demo-key")
        self.source_analyzer = SourceAnalyzer()
        self.obsolescence_detector = ObsolescenceDetector()
        self.coverage_monitor = CoverageMonitor()
        self.metrics_collector = MetricsCollector()
        
        # Estado do scheduler
        self.is_running = False
        self.last_weekly_update = None
        self.last_monthly_review = None
        
        # Configurações padrão
        self.config = {
            "weekly_update": {
                "enabled": True,
                "day": "sunday",
                "time": "02:00",
                "max_sources_per_run": 50,
                "timeout_minutes": 120
            },
            "monthly_review": {
                "enabled": True,
                "day_of_month": 1,
                "time": "01:00",
                "full_reindex": True,
                "cleanup_old_data": True
            },
            "emergency_update": {
                "enabled": True,
                "trigger_threshold": 0.1,  # 10% de fontes obsoletas
                "max_frequency_hours": 24
            }
        }
        
        self._load_config()
        self._setup_schedules()
    
    def _load_config(self):
        """Carrega configurações do arquivo"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    self.logger.info(f"Configurações carregadas de {self.config_path}")
        except Exception as e:
            self.logger.warning(f"Erro ao carregar configurações: {e}. Usando padrões.")
    
    def _save_config(self):
        """Salva configurações no arquivo"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Configurações salvas em {self.config_path}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
    
    def _setup_schedules(self):
        """Configura os agendamentos"""
        # Atualização semanal
        if self.config["weekly_update"]["enabled"]:
            day = self.config["weekly_update"]["day"]
            time_str = self.config["weekly_update"]["time"]
            
            getattr(schedule.every(), day).at(time_str).do(self._run_weekly_update)
            self.logger.info(f"Atualização semanal agendada para {day} às {time_str}")
        
        # Revisão mensal
        if self.config["monthly_review"]["enabled"]:
            # Agendamento mensal é mais complexo, verificamos diariamente
            schedule.every().day.at("00:30").do(self._check_monthly_review)
            self.logger.info("Verificação de revisão mensal agendada")
    
    async def _run_weekly_update(self):
        """Executa atualização semanal incremental"""
        self.logger.info("🔄 Iniciando atualização semanal incremental")
        
        try:
            start_time = datetime.now()
            
            # 1. Verificar fontes que precisam de atualização
            outdated_sources = await self._identify_outdated_sources()
            
            if not outdated_sources:
                self.logger.info("✅ Nenhuma fonte precisa de atualização")
                return
            
            # 2. Limitar número de fontes por execução
            max_sources = self.config["weekly_update"]["max_sources_per_run"]
            sources_to_update = outdated_sources[:max_sources]
            
            self.logger.info(f"📊 Atualizando {len(sources_to_update)} de {len(outdated_sources)} fontes")
            
            # 3. Coletar dados atualizados
            async with self.data_collector as collector:
                updated_data = await collector.collect_all_seeds()
            
            # 4. Atualizar índices
            if updated_data:
                await self.index_manager.update_incremental(updated_data)
            
            # 5. Verificar qualidade das atualizações
            quality_report = await self._validate_updates(updated_data)
            
            # 6. Registrar métricas
            duration = (datetime.now() - start_time).total_seconds()
            await self._record_update_metrics("weekly", len(sources_to_update), duration, quality_report)
            
            self.last_weekly_update = datetime.now()
            self.logger.info(f"✅ Atualização semanal concluída em {duration:.1f}s")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na atualização semanal: {e}")
            await self._handle_update_error("weekly", e)
    
    async def _check_monthly_review(self):
        """Verifica se é hora da revisão mensal"""
        now = datetime.now()
        target_day = self.config["monthly_review"]["day_of_month"]
        
        # Verificar se é o dia correto e se não foi executada este mês
        if (now.day == target_day and 
            (self.last_monthly_review is None or 
             self.last_monthly_review.month != now.month)):
            
            await self._run_monthly_review()
    
    async def _run_monthly_review(self):
        """Executa revisão mensal completa"""
        self.logger.info("🔍 Iniciando revisão mensal completa")
        
        try:
            start_time = datetime.now()
            
            # 1. Análise completa de cobertura
            coverage_report = await self.coverage_monitor.generate_comprehensive_report()
            
            # 2. Detecção de obsolescência
            obsolescence_report = await self.obsolescence_detector.full_scan()
            
            # 3. Análise de qualidade das fontes
            quality_report = await self.source_analyzer.analyze_all_sources()
            
            # 4. Reindexação completa (se configurado)
            if self.config["monthly_review"]["full_reindex"]:
                await self.index_manager.full_reindex()
            
            # 5. Limpeza de dados antigos
            if self.config["monthly_review"]["cleanup_old_data"]:
                await self._cleanup_old_data()
            
            # 6. Gerar relatório consolidado
            monthly_report = {
                "timestamp": datetime.now().isoformat(),
                "coverage": coverage_report,
                "obsolescence": obsolescence_report,
                "quality": quality_report,
                "actions_taken": {
                    "full_reindex": self.config["monthly_review"]["full_reindex"],
                    "cleanup_performed": self.config["monthly_review"]["cleanup_old_data"]
                }
            }
            
            # 7. Salvar relatório
            await self._save_monthly_report(monthly_report)
            
            # 8. Registrar métricas
            duration = (datetime.now() - start_time).total_seconds()
            await self._record_update_metrics("monthly", 0, duration, monthly_report)
            
            self.last_monthly_review = datetime.now()
            self.logger.info(f"✅ Revisão mensal concluída em {duration:.1f}s")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na revisão mensal: {e}")
            await self._handle_update_error("monthly", e)
    
    async def _identify_outdated_sources(self) -> List[Dict]:
        """Identifica fontes que precisam de atualização"""
        try:
            # Usar o detector de obsolescência para identificar fontes
            obsolete_sources = await self.obsolescence_detector.detect_obsolete_sources()
            
            # Filtrar por critérios de atualização
            outdated = []
            for source in obsolete_sources:
                if self._should_update_source(source):
                    outdated.append(source)
            
            return outdated
            
        except Exception as e:
            self.logger.error(f"Erro ao identificar fontes desatualizadas: {e}")
            return []
    
    def _should_update_source(self, source: Dict) -> bool:
        """Determina se uma fonte deve ser atualizada"""
        # Critérios para atualização:
        # 1. Última atualização > 7 dias
        # 2. Score de obsolescência > threshold
        # 3. Fonte marcada como crítica
        
        last_update = source.get("last_updated")
        if last_update:
            days_since_update = (datetime.now() - datetime.fromisoformat(last_update)).days
            if days_since_update > 7:
                return True
        
        obsolescence_score = source.get("obsolescence_score", 0)
        if obsolescence_score > 0.3:  # 30% de obsolescência
            return True
        
        is_critical = source.get("is_critical", False)
        if is_critical:
            return True
        
        return False
    
    async def _validate_updates(self, updated_data: List[Dict]) -> Dict:
        """Valida a qualidade das atualizações"""
        validation_report = {
            "total_updated": len(updated_data),
            "successful": 0,
            "failed": 0,
            "quality_scores": []
        }
        
        for data in updated_data:
            try:
                # Validar estrutura dos dados
                if self._validate_data_structure(data):
                    validation_report["successful"] += 1
                    
                    # Calcular score de qualidade
                    quality_score = await self._calculate_quality_score(data)
                    validation_report["quality_scores"].append(quality_score)
                else:
                    validation_report["failed"] += 1
                    
            except Exception as e:
                self.logger.warning(f"Erro na validação de dados: {e}")
                validation_report["failed"] += 1
        
        # Calcular score médio
        if validation_report["quality_scores"]:
            validation_report["average_quality"] = sum(validation_report["quality_scores"]) / len(validation_report["quality_scores"])
        else:
            validation_report["average_quality"] = 0
        
        return validation_report
    
    def _validate_data_structure(self, data: Dict) -> bool:
        """Valida se os dados têm a estrutura esperada"""
        required_fields = ["source_id", "content", "metadata", "timestamp"]
        return all(field in data for field in required_fields)
    
    async def _calculate_quality_score(self, data: Dict) -> float:
        """Calcula score de qualidade dos dados"""
        score = 0.0
        
        # Completude dos metadados (30%)
        metadata = data.get("metadata", {})
        required_metadata = ["title", "description", "tags", "category"]
        completeness = sum(1 for field in required_metadata if field in metadata) / len(required_metadata)
        score += completeness * 0.3
        
        # Tamanho do conteúdo (20%)
        content = data.get("content", "")
        if len(content) > 100:  # Conteúdo mínimo
            score += 0.2
        
        # Atualidade (25%)
        timestamp = data.get("timestamp")
        if timestamp:
            age_hours = (datetime.now() - datetime.fromisoformat(timestamp)).total_seconds() / 3600
            if age_hours < 24:  # Menos de 24h
                score += 0.25
            elif age_hours < 168:  # Menos de 1 semana
                score += 0.15
        
        # Validação de links (25%)
        links_valid = await self._validate_links(data)
        score += links_valid * 0.25
        
        return min(score, 1.0)
    
    async def _validate_links(self, data: Dict) -> float:
        """Valida links no conteúdo (simplificado)"""
        # Implementação simplificada - em produção usaria requests
        return 0.8  # Assumir 80% dos links válidos
    
    async def _cleanup_old_data(self):
        """Remove dados antigos e desnecessários"""
        try:
            # Remover índices antigos (> 3 meses)
            cutoff_date = datetime.now() - timedelta(days=90)
            await self.index_manager.cleanup_old_indices(cutoff_date)
            
            # Limpar logs antigos
            log_dir = Path("src/logs")
            if log_dir.exists():
                for log_file in log_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
            
            # Limpar cache antigo
            cache_dir = Path("data/index/cache")
            if cache_dir.exists():
                for cache_file in cache_dir.glob("*"):
                    if cache_file.stat().st_mtime < cutoff_date.timestamp():
                        cache_file.unlink()
            
            self.logger.info("🧹 Limpeza de dados antigos concluída")
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de dados: {e}")
    
    async def _save_monthly_report(self, report: Dict):
        """Salva relatório mensal"""
        try:
            reports_dir = Path("data/governance/monthly_reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y-%m")
            report_file = reports_dir / f"monthly_report_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📊 Relatório mensal salvo: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório mensal: {e}")
    
    async def _record_update_metrics(self, update_type: str, sources_count: int, duration: float, report: Dict):
        """Registra métricas da atualização"""
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "update_type": update_type,
                "sources_processed": sources_count,
                "duration_seconds": duration,
                "success_rate": report.get("successful", 0) / max(report.get("total_updated", 1), 1),
                "average_quality": report.get("average_quality", 0)
            }
            
            await self.metrics_collector.record_update_metrics(metrics)
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar métricas: {e}")
    
    async def _handle_update_error(self, update_type: str, error: Exception):
        """Trata erros durante atualizações"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "update_type": update_type,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        # Log do erro
        self.logger.error(f"Erro em {update_type}: {error}")
        
        # Salvar detalhes do erro
        error_file = Path(f"data/governance/errors/update_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        error_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_info, f, indent=2, ensure_ascii=False)
    
    async def check_emergency_update(self):
        """Verifica se é necessária uma atualização de emergência"""
        if not self.config["emergency_update"]["enabled"]:
            return
        
        try:
            # Verificar taxa de obsolescência
            obsolescence_rate = await self.obsolescence_detector.get_obsolescence_rate()
            threshold = self.config["emergency_update"]["trigger_threshold"]
            
            if obsolescence_rate > threshold:
                self.logger.warning(f"🚨 Taxa de obsolescência alta: {obsolescence_rate:.2%}")
                
                # Verificar se não foi executada recentemente
                max_freq_hours = self.config["emergency_update"]["max_frequency_hours"]
                if (self.last_weekly_update is None or 
                    (datetime.now() - self.last_weekly_update).total_seconds() > max_freq_hours * 3600):
                    
                    self.logger.info("🚨 Iniciando atualização de emergência")
                    await self._run_weekly_update()
                    
        except Exception as e:
            self.logger.error(f"Erro na verificação de emergência: {e}")
    
    def start(self):
        """Inicia o scheduler"""
        if self.is_running:
            self.logger.warning("Scheduler já está em execução")
            return
        
        self.is_running = True
        self.logger.info("🚀 Scheduler de atualizações iniciado")
        
        # Loop principal
        while self.is_running:
            try:
                schedule.run_pending()
                
                # Verificar atualização de emergência a cada hora
                asyncio.run(self.check_emergency_update())
                
                time.sleep(60)  # Verificar a cada minuto
                
            except KeyboardInterrupt:
                self.logger.info("⏹️ Scheduler interrompido pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"Erro no loop principal: {e}")
                time.sleep(300)  # Aguardar 5 minutos antes de tentar novamente
    
    def stop(self):
        """Para o scheduler"""
        self.is_running = False
        self.logger.info("⏹️ Scheduler de atualizações parado")
    
    def get_status(self) -> Dict:
        """Retorna status atual do scheduler"""
        return {
            "is_running": self.is_running,
            "last_weekly_update": self.last_weekly_update.isoformat() if self.last_weekly_update else None,
            "last_monthly_review": self.last_monthly_review.isoformat() if self.last_monthly_review else None,
            "next_weekly_update": schedule.next_run().isoformat() if schedule.jobs else None,
            "config": self.config
        }
    
    def update_config(self, new_config: Dict):
        """Atualiza configurações"""
        self.config.update(new_config)
        self._save_config()
        
        # Reconfigurar agendamentos
        schedule.clear()
        self._setup_schedules()
        
        self.logger.info("⚙️ Configurações atualizadas")

# Instância global
update_scheduler = UpdateScheduler()

if __name__ == "__main__":
    # Executar scheduler
    update_scheduler.start()