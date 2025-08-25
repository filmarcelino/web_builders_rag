import json
import os
import faiss
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

def parse_log_file() -> Dict:
    """Analisa o arquivo de log para extrair métricas de velocidade"""
    log_file = 'rag_ingestion.log'
    
    if not os.path.exists(log_file):
        print("❌ Arquivo de log não encontrado")
        return {}
    
    print("📊 Analisando logs de ingestão...")
    
    # Tentar diferentes encodings
    encodings = ['utf-8', 'latin-1', 'cp1252']
    lines = []
    
    for encoding in encodings:
        try:
            with open(log_file, 'r', encoding=encoding) as f:
                lines = f.readlines()
            break
        except UnicodeDecodeError:
            continue
    
    if not lines:
        print("❌ Não foi possível ler o arquivo de log com nenhum encoding")
        return {}
    
    # Extrair timestamps e batches processados
    batch_times = []
    start_time = None
    
    for line in lines:
        # Procurar por linhas de processamento de batch
        if "Processando batch" in line:
            # Extrair timestamp
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            batch_match = re.search(r'batch (\d+)', line)
            
            if timestamp_match and batch_match:
                timestamp_str = timestamp_match.group(1)
                batch_num = int(batch_match.group(1))
                
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                if start_time is None:
                    start_time = timestamp
                
                batch_times.append((timestamp, batch_num))
    
    if not batch_times:
        print("❌ Nenhum dado de batch encontrado nos logs")
        return {}
    
    # Calcular velocidade
    latest_time, latest_batch = batch_times[-1]
    total_time = (latest_time - start_time).total_seconds()
    
    # Calcular velocidade média
    chunks_per_second = latest_batch / total_time if total_time > 0 else 0
    chunks_per_minute = chunks_per_second * 60
    chunks_per_hour = chunks_per_minute * 60
    
    return {
        'start_time': start_time,
        'latest_time': latest_time,
        'total_time_seconds': total_time,
        'total_batches': latest_batch,
        'chunks_per_second': chunks_per_second,
        'chunks_per_minute': chunks_per_minute,
        'chunks_per_hour': chunks_per_hour
    }

def analyze_data_sizes() -> Dict:
    """Analisa o tamanho dos dados processados"""
    print("📏 Analisando tamanhos dos dados...")
    
    sizes = {}
    
    # Tamanho do corpus processado
    processed_dir = Path('processed_corpus')
    if processed_dir.exists():
        total_size = 0
        file_count = 0
        
        for file_path in processed_dir.glob('*.json'):
            total_size += file_path.stat().st_size
            file_count += 1
        
        sizes['processed_corpus'] = {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'file_count': file_count,
            'avg_file_size_mb': (total_size / file_count / (1024 * 1024)) if file_count > 0 else 0
        }
    
    # Tamanho dos dados RAG
    rag_data_dir = Path('rag_data')
    if rag_data_dir.exists():
        faiss_file = rag_data_dir / 'faiss_index.bin'
        metadata_file = rag_data_dir / 'chunk_metadata.json'
        
        rag_sizes = {}
        
        if faiss_file.exists():
            faiss_size = faiss_file.stat().st_size
            rag_sizes['faiss_index'] = {
                'size_bytes': faiss_size,
                'size_mb': faiss_size / (1024 * 1024)
            }
            
            # Analisar índice FAISS
            try:
                index = faiss.read_index(str(faiss_file))
                rag_sizes['faiss_index']['vector_count'] = index.ntotal
                rag_sizes['faiss_index']['vector_dimension'] = index.d
                rag_sizes['faiss_index']['estimated_size_per_vector'] = faiss_size / index.ntotal if index.ntotal > 0 else 0
            except Exception as e:
                print(f"⚠️  Erro ao analisar índice FAISS: {e}")
        
        if metadata_file.exists():
            metadata_size = metadata_file.stat().st_size
            rag_sizes['metadata'] = {
                'size_bytes': metadata_size,
                'size_mb': metadata_size / (1024 * 1024)
            }
        
        sizes['rag_data'] = rag_sizes
    
    return sizes

def estimate_completion() -> Dict:
    """Estima tempo para conclusão baseado na velocidade atual"""
    print("⏱️  Calculando estimativas de conclusão...")
    
    # Contar total de chunks disponíveis
    processed_dir = Path('processed_corpus')
    total_chunks = 0
    
    if processed_dir.exists():
        for file_path in processed_dir.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_chunks += len(data)
            except Exception as e:
                print(f"⚠️  Erro ao ler {file_path}: {e}")
    
    # Verificar chunks já processados
    processed_chunks = 0
    rag_data_dir = Path('rag_data')
    faiss_file = rag_data_dir / 'faiss_index.bin'
    
    if faiss_file.exists():
        try:
            index = faiss.read_index(str(faiss_file))
            processed_chunks = index.ntotal
        except Exception as e:
            print(f"⚠️  Erro ao ler índice: {e}")
    
    remaining_chunks = total_chunks - processed_chunks
    
    return {
        'total_chunks': total_chunks,
        'processed_chunks': processed_chunks,
        'remaining_chunks': remaining_chunks,
        'progress_percentage': (processed_chunks / total_chunks * 100) if total_chunks > 0 else 0
    }

def main():
    """Função principal para calcular métricas de ingestão"""
    print("🔍 Calculando Métricas de Ingestão do RAG")
    print("=" * 50)
    
    # Analisar velocidade
    speed_metrics = parse_log_file()
    
    # Analisar tamanhos
    size_metrics = analyze_data_sizes()
    
    # Estimar conclusão
    completion_metrics = estimate_completion()
    
    print("\n📈 MÉTRICAS DE VELOCIDADE")
    print("-" * 30)
    
    if speed_metrics:
        print(f"⏰ Tempo total de processamento: {speed_metrics['total_time_seconds']:.0f} segundos ({speed_metrics['total_time_seconds']/3600:.1f} horas)")
        print(f"📦 Batches processados: {speed_metrics['total_batches']:,}")
        print(f"🚀 Velocidade atual:")
        print(f"   • {speed_metrics['chunks_per_second']:.2f} chunks/segundo")
        print(f"   • {speed_metrics['chunks_per_minute']:.1f} chunks/minuto")
        print(f"   • {speed_metrics['chunks_per_hour']:.0f} chunks/hora")
    else:
        print("❌ Não foi possível calcular métricas de velocidade")
    
    print("\n📊 MÉTRICAS DE TAMANHO")
    print("-" * 30)
    
    if 'processed_corpus' in size_metrics:
        corpus = size_metrics['processed_corpus']
        print(f"📁 Corpus Processado:")
        print(f"   • Tamanho total: {corpus['total_size_mb']:.1f} MB")
        print(f"   • Arquivos: {corpus['file_count']}")
        print(f"   • Tamanho médio por arquivo: {corpus['avg_file_size_mb']:.1f} MB")
    
    if 'rag_data' in size_metrics:
        rag = size_metrics['rag_data']
        print(f"\n🗃️  Dados RAG:")
        
        if 'faiss_index' in rag:
            faiss_data = rag['faiss_index']
            print(f"   • Índice FAISS: {faiss_data['size_mb']:.1f} MB")
            if 'vector_count' in faiss_data:
                print(f"   • Vetores indexados: {faiss_data['vector_count']:,}")
                print(f"   • Dimensão dos vetores: {faiss_data['vector_dimension']}")
                print(f"   • Tamanho por vetor: {faiss_data['estimated_size_per_vector']:.0f} bytes")
        
        if 'metadata' in rag:
            print(f"   • Metadados: {rag['metadata']['size_mb']:.1f} MB")
    
    print("\n🎯 PROGRESSO E ESTIMATIVAS")
    print("-" * 30)
    
    if completion_metrics:
        print(f"📈 Progresso atual: {completion_metrics['progress_percentage']:.1f}%")
        print(f"✅ Chunks processados: {completion_metrics['processed_chunks']:,}")
        print(f"⏳ Chunks restantes: {completion_metrics['remaining_chunks']:,}")
        print(f"📊 Total de chunks: {completion_metrics['total_chunks']:,}")
        
        # Estimar tempo restante
        if speed_metrics and completion_metrics['remaining_chunks'] > 0:
            remaining_hours = completion_metrics['remaining_chunks'] / speed_metrics['chunks_per_hour']
            print(f"⏱️  Tempo estimado para conclusão: {remaining_hours:.1f} horas")
            
            # Estimar tamanho final
            if 'rag_data' in size_metrics and 'faiss_index' in size_metrics['rag_data']:
                current_size_mb = size_metrics['rag_data']['faiss_index']['size_mb']
                estimated_final_size = current_size_mb * (completion_metrics['total_chunks'] / completion_metrics['processed_chunks'])
                print(f"📏 Tamanho final estimado do índice: {estimated_final_size:.1f} MB")
    
    print("\n" + "=" * 50)
    print("✅ Análise concluída!")

if __name__ == "__main__":
    main()