import json
import os
from pathlib import Path

def analyze_chunks():
    chunks_dir = Path("processed_corpus/animations")
    
    all_chunks = []
    for file_path in chunks_dir.glob("animation_chunks_batch_*.json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            chunks = data.get('chunks', [])
            all_chunks.extend(chunks)
    
    print(f"Total de chunks: {len(all_chunks)}")
    
    # Analisa tamanhos
    sizes = [len(chunk['text']) for chunk in all_chunks]
    sizes.sort(reverse=True)
    
    print(f"Maior chunk: {sizes[0]} caracteres")
    print(f"Top 10 maiores chunks: {sizes[:10]}")
    print(f"Média: {sum(sizes) / len(sizes):.1f} caracteres")
    
    # Chunks muito grandes (>6000 chars ≈ 1500 tokens)
    large_chunks = [chunk for chunk in all_chunks if len(chunk['text']) > 6000]
    print(f"Chunks > 6000 chars: {len(large_chunks)}")
    
    if large_chunks:
        print("\nExemplo de chunk muito grande:")
        print(f"Tamanho: {len(large_chunks[0]['text'])} chars")
        print(f"Fonte: {large_chunks[0]['metadata'].get('source', 'N/A')}")
        print(f"Tipo: {large_chunks[0]['metadata'].get('content_type', 'N/A')}")
        print(f"Primeiros 200 chars: {large_chunks[0]['text'][:200]}...")

if __name__ == "__main__":
    analyze_chunks()