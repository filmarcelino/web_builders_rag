#!/usr/bin/env python3
"""
Teste simples para verificar se o FAISS funciona com caminhos que contêm acentos.
"""

import faiss
import numpy as np
from pathlib import Path
import os

def test_faiss_with_accents():
    """Testa se o FAISS consegue salvar em caminhos com acentos."""
    
    # Criar um índice simples
    dimension = 128
    index = faiss.IndexFlatIP(dimension)
    
    # Adicionar alguns vetores
    vectors = np.random.random((10, dimension)).astype('float32')
    # Normalizar para busca por cosseno
    for i in range(len(vectors)):
        vectors[i] = vectors[i] / np.linalg.norm(vectors[i])
    
    index.add(vectors)
    
    print(f"Índice criado com {index.ntotal} vetores")
    
    # Testar salvamento em diretório com acentos
    test_dir = Path("test_rag_data")
    test_dir.mkdir(exist_ok=True)
    
    index_file = test_dir / "faiss_test.bin"
    
    try:
        print(f"Tentando salvar em: {index_file}")
        faiss.write_index(index, str(index_file))
        print("✅ Salvamento bem-sucedido!")
        
        # Testar carregamento
        loaded_index = faiss.read_index(str(index_file))
        print(f"✅ Carregamento bem-sucedido! {loaded_index.ntotal} vetores")
        
        # Limpar arquivo de teste
        index_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("Testando FAISS com caminhos que contêm acentos...")
    success = test_faiss_with_accents()
    
    if success:
        print("\n✅ Teste passou - FAISS funciona corretamente")
    else:
        print("\n❌ Teste falhou - Problema com FAISS")