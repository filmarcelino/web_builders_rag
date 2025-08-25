#!/usr/bin/env python3
"""
Script de automação para aprimoramento do RAG.
Orquestra coleta, processamento e ingestão de dados.
"""

import os
import sys
import asyncio
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RAGAutomation:
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.corpus_dir = self.base_dir / "corpus"
        self.processed_dir = self.base_dir / "processed_corpus"
        self.rag_data_dir = self.base_dir / "rag_data"
        
        # Scripts
        self.collect_script = self.base_dir / "collect_corpus.py"
        self.process_script = self.base_dir / "process_corpus.py"
        self.ingest_script = self.base_dir / "ingest_to_rag.py"
        
        # Arquivo de configuração
        self.config_file = self.base_dir / "rag_automation_config.json"
        self.status_file = self.base_dir / "rag_automation_status.json"
        
        # Configurações padrão
        self.default_config = {
            "collection": {
                "enabled": True,
                "skip_existing": True,
                "max_retries": 3
            },
            "processing": {
                "enabled": True,
                "max_workers": 4,
                "chunk_size": 1000,
                "chunk_overlap": 200
            },
            "ingestion": {
                "enabled": True,
                "batch_size": 100,
                "force_reindex": False,
                "embedding_model": "text-embedding-3-small"
            },
            "automation": {
                "cleanup_temp_files": True,
                "backup_existing_data": True,
                "validate_dependencies": True
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo ou usa padrão."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("Configuração carregada do arquivo")
                return config
            except Exception as e:
                logger.warning(f"Erro ao carregar configuração: {e}")
        
        # Salvar configuração padrão
        self.save_config(self.default_config)
        return self.default_config
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Salva configuração no arquivo."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    def load_status(self) -> Dict[str, Any]:
        """Carrega status da última execução."""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Erro ao carregar status: {e}")
        
        return {
            "last_run": None,
            "last_successful_run": None,
            "collection_status": "pending",
            "processing_status": "pending",
            "ingestion_status": "pending",
            "total_chunks_indexed": 0,
            "errors": []
        }
    
    def save_status(self, status: Dict[str, Any]) -> None:
        """Salva status atual."""
        try:
            status["last_run"] = datetime.now().isoformat()
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar status: {e}")
    
    def validate_dependencies(self) -> bool:
        """Valida se todas as dependências estão instaladas."""
        logger.info("Validando dependências...")
        
        required_packages = [
            'openai',
            'faiss-cpu',
            'redis',
            'requests',
            'beautifulsoup4',
            'markdown',
            'tiktoken',
            'numpy'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Pacotes faltando: {', '.join(missing_packages)}")
            logger.error("Execute: pip install " + " ".join(missing_packages))
            return False
        
        logger.info("Todas as dependências estão instaladas")
        return True
    
    def validate_environment(self) -> bool:
        """Valida variáveis de ambiente necessárias."""
        logger.info("Validando variáveis de ambiente...")
        
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Variáveis de ambiente faltando: {', '.join(missing_vars)}")
            return False
        
        logger.info("Variáveis de ambiente configuradas")
        return True
    
    def validate_scripts(self) -> bool:
        """Valida se todos os scripts necessários existem."""
        logger.info("Validando scripts...")
        
        scripts = [self.collect_script, self.process_script, self.ingest_script]
        missing_scripts = []
        
        for script in scripts:
            if not script.exists():
                missing_scripts.append(script.name)
        
        if missing_scripts:
            logger.error(f"Scripts faltando: {', '.join(missing_scripts)}")
            return False
        
        logger.info("Todos os scripts estão disponíveis")
        return True
    
    def backup_existing_data(self) -> bool:
        """Faz backup dos dados existentes."""
        logger.info("Fazendo backup dos dados existentes...")
        
        try:
            backup_dir = self.base_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(exist_ok=True)
            
            # Backup de dados processados
            if self.processed_dir.exists():
                import shutil
                shutil.copytree(self.processed_dir, backup_dir / "processed_corpus")
                logger.info(f"Backup de dados processados criado em {backup_dir}")
            
            # Backup de dados do RAG
            if self.rag_data_dir.exists():
                import shutil
                shutil.copytree(self.rag_data_dir, backup_dir / "rag_data")
                logger.info(f"Backup de dados do RAG criado em {backup_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao fazer backup: {e}")
            return False
    
    def run_script(self, script_path: Path, args: list = None) -> bool:
        """Executa um script Python."""
        try:
            cmd = [sys.executable, str(script_path)]
            if args:
                cmd.extend(args)
            
            logger.info(f"Executando: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            if result.returncode == 0:
                logger.info(f"Script {script_path.name} executado com sucesso")
                if result.stdout:
                    logger.info(f"Saída: {result.stdout[-500:]}")
                return True
            else:
                logger.error(f"Erro ao executar {script_path.name}")
                logger.error(f"Código de saída: {result.returncode}")
                if result.stderr:
                    logger.error(f"Erro: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Exceção ao executar {script_path.name}: {e}")
            return False
    
    def run_collection(self, config: Dict[str, Any]) -> bool:
        """Executa coleta de dados."""
        if not config["collection"]["enabled"]:
            logger.info("Coleta desabilitada na configuração")
            return True
        
        logger.info("=== INICIANDO COLETA DE DADOS ===")
        
        args = []
        if config["collection"]["skip_existing"]:
            args.append("--skip-existing")
        
        success = self.run_script(self.collect_script, args)
        
        if success:
            logger.info("Coleta de dados concluída com sucesso")
        else:
            logger.error("Falha na coleta de dados")
        
        return success
    
    def run_processing(self, config: Dict[str, Any]) -> bool:
        """Executa processamento de dados."""
        if not config["processing"]["enabled"]:
            logger.info("Processamento desabilitado na configuração")
            return True
        
        logger.info("=== INICIANDO PROCESSAMENTO DE DADOS ===")
        
        success = self.run_script(self.process_script)
        
        if success:
            logger.info("Processamento de dados concluído com sucesso")
        else:
            logger.error("Falha no processamento de dados")
        
        return success
    
    def run_ingestion(self, config: Dict[str, Any]) -> bool:
        """Executa ingestão no RAG."""
        if not config["ingestion"]["enabled"]:
            logger.info("Ingestão desabilitada na configuração")
            return True
        
        logger.info("=== INICIANDO INGESTÃO NO RAG ===")
        
        args = []
        if config["ingestion"]["force_reindex"]:
            args.append("--force-reindex")
        
        success = self.run_script(self.ingest_script, args)
        
        if success:
            logger.info("Ingestão no RAG concluída com sucesso")
        else:
            logger.error("Falha na ingestão no RAG")
        
        return success
    
    def cleanup_temp_files(self) -> None:
        """Remove arquivos temporários."""
        logger.info("Limpando arquivos temporários...")
        
        try:
            # Remover arquivos de log antigos (manter últimos 10)
            log_files = list(self.base_dir.glob("*.log"))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for log_file in log_files[10:]:
                log_file.unlink()
                logger.info(f"Removido log antigo: {log_file.name}")
            
            # Remover backups antigos (manter últimos 5)
            backup_dirs = [d for d in self.base_dir.iterdir() 
                          if d.is_dir() and d.name.startswith("backup_")]
            backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for backup_dir in backup_dirs[5:]:
                import shutil
                shutil.rmtree(backup_dir)
                logger.info(f"Removido backup antigo: {backup_dir.name}")
                
        except Exception as e:
            logger.warning(f"Erro durante limpeza: {e}")
    
    def get_enhancement_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do aprimoramento."""
        stats = {
            "corpus_files": 0,
            "processed_chunks": 0,
            "indexed_chunks": 0,
            "total_size_mb": 0
        }
        
        try:
            # Estatísticas do corpus
            if self.corpus_dir.exists():
                corpus_files = list(self.corpus_dir.rglob("*"))
                stats["corpus_files"] = len([f for f in corpus_files if f.is_file()])
                
                total_size = sum(f.stat().st_size for f in corpus_files if f.is_file())
                stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # Estatísticas de processamento
            metadata_file = self.processed_dir / "processing_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    stats["processed_chunks"] = metadata.get("total_chunks", 0)
            
            # Estatísticas de ingestão
            rag_metadata_file = self.rag_data_dir / "chunk_metadata.json"
            if rag_metadata_file.exists():
                with open(rag_metadata_file, 'r', encoding='utf-8') as f:
                    rag_metadata = json.load(f)
                    stats["indexed_chunks"] = len(rag_metadata)
            
        except Exception as e:
            logger.warning(f"Erro ao obter estatísticas: {e}")
        
        return stats
    
    async def run_full_automation(self, force_reindex: bool = False) -> bool:
        """Executa automação completa do RAG."""
        logger.info("=== INICIANDO AUTOMAÇÃO COMPLETA DO RAG ===")
        
        start_time = time.time()
        
        # Carregar configuração e status
        config = self.load_config()
        status = self.load_status()
        
        # Atualizar configuração se necessário
        if force_reindex:
            config["ingestion"]["force_reindex"] = True
        
        try:
            # Validações
            if config["automation"]["validate_dependencies"]:
                if not self.validate_dependencies():
                    return False
            
            if not self.validate_environment():
                return False
            
            if not self.validate_scripts():
                return False
            
            # Backup
            if config["automation"]["backup_existing_data"]:
                if not self.backup_existing_data():
                    logger.warning("Falha no backup, continuando...")
            
            # Executar pipeline
            success = True
            
            # 1. Coleta
            if success:
                success = self.run_collection(config)
                status["collection_status"] = "completed" if success else "failed"
            
            # 2. Processamento
            if success:
                success = self.run_processing(config)
                status["processing_status"] = "completed" if success else "failed"
            
            # 3. Ingestão
            if success:
                success = self.run_ingestion(config)
                status["ingestion_status"] = "completed" if success else "failed"
            
            # Limpeza
            if success and config["automation"]["cleanup_temp_files"]:
                self.cleanup_temp_files()
            
            # Atualizar status
            if success:
                status["last_successful_run"] = datetime.now().isoformat()
                stats = self.get_enhancement_statistics()
                status["total_chunks_indexed"] = stats["indexed_chunks"]
            
            # Salvar status
            self.save_status(status)
            
            # Estatísticas finais
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info("=== AUTOMAÇÃO CONCLUÍDA ===")
            logger.info(f"Duração total: {duration:.1f} segundos")
            logger.info(f"Status: {'SUCESSO' if success else 'FALHA'}")
            
            if success:
                stats = self.get_enhancement_statistics()
                logger.info(f"Arquivos no corpus: {stats['corpus_files']:,}")
                logger.info(f"Chunks processados: {stats['processed_chunks']:,}")
                logger.info(f"Chunks indexados: {stats['indexed_chunks']:,}")
                logger.info(f"Tamanho total: {stats['total_size_mb']} MB")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro durante automação: {e}")
            status["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            self.save_status(status)
            return False

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automação do aprimoramento do RAG')
    parser.add_argument('--force-reindex', action='store_true',
                       help='Forçar reindexação completa')
    parser.add_argument('--config-only', action='store_true',
                       help='Apenas criar arquivo de configuração')
    parser.add_argument('--status', action='store_true',
                       help='Mostrar status atual')
    parser.add_argument('--stats', action='store_true',
                       help='Mostrar estatísticas')
    
    args = parser.parse_args()
    
    automation = RAGAutomation()
    
    if args.config_only:
        config = automation.load_config()
        print(f"Arquivo de configuração criado: {automation.config_file}")
        return
    
    if args.status:
        status = automation.load_status()
        print("=== STATUS ATUAL ===")
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return
    
    if args.stats:
        stats = automation.get_enhancement_statistics()
        print("=== ESTATÍSTICAS ===")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return
    
    # Executar automação
    success = asyncio.run(automation.run_full_automation(force_reindex=args.force_reindex))
    
    if success:
        print("\n✅ Automação concluída com sucesso!")
        print("O RAG foi aprimorado com os novos dados.")
    else:
        print("\n❌ Automação falhou.")
        print("Verifique os logs para mais detalhes.")
        sys.exit(1)

if __name__ == "__main__":
    main()