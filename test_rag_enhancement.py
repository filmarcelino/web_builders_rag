#!/usr/bin/env python3
"""
Script de teste para validar o aprimoramento do RAG.
Testa com dados de exemplo menores para validação rápida.
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import tempfile
import shutil
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGTestSuite:
    def __init__(self):# Diretórios de teste - usando caminho sem caracteres especiais
        self.base_dir = Path.cwd()
        self.test_corpus_dir = Path("C:/Users/luisf/test_corpus")
        self.test_processed_dir = Path("C:/Users/luisf/test_processed_corpus")
        self.test_rag_data_dir = Path("C:/Users/luisf/test_rag_data")
        
        # Usar caminhos absolutos para evitar problemas
        self.test_corpus_dir = self.test_corpus_dir.resolve()
        self.test_processed_dir = self.test_processed_dir.resolve()
        self.test_rag_data_dir = self.test_rag_data_dir.resolve()
        
        # Limpar diretórios de teste
        self.cleanup_test_dirs()
        
        # Pequena pausa para evitar problemas de timing
        import time
        time.sleep(0.1)
        
        # Criar diretórios de teste
        self.test_corpus_dir.mkdir(exist_ok=True)
        self.test_processed_dir.mkdir(exist_ok=True)
        self.test_rag_data_dir.mkdir(exist_ok=True)
        
        # Verificar se diretórios foram criados
        logger.info(f"Diretórios criados:")
        logger.info(f"  - Corpus: {self.test_corpus_dir.exists()}")
        logger.info(f"  - Processed: {self.test_processed_dir.exists()}")
        logger.info(f"  - RAG Data: {self.test_rag_data_dir.exists()}")
    
    def cleanup_test_dirs(self):
        """Remove diretórios de teste existentes."""
        for test_dir in [self.test_corpus_dir, self.test_processed_dir, self.test_rag_data_dir]:
            if test_dir.exists():
                shutil.rmtree(test_dir)
    
    def create_sample_corpus(self):
        """Cria um corpus de exemplo para teste."""
        logger.info("Criando corpus de exemplo...")
        
        # Dados de exemplo sobre desenvolvimento web
        sample_data = {
            "html_basics.md": """
# HTML Básico

HTML (HyperText Markup Language) é a linguagem de marcação padrão para criar páginas web.

## Estrutura Básica

```html
<!DOCTYPE html>
<html>
<head>
    <title>Título da Página</title>
</head>
<body>
    <h1>Meu Primeiro Cabeçalho</h1>
    <p>Meu primeiro parágrafo.</p>
</body>
</html>
```

## Tags Importantes

- `<h1>` a `<h6>`: Cabeçalhos
- `<p>`: Parágrafos
- `<div>`: Divisões
- `<span>`: Elementos inline
- `<a>`: Links
- `<img>`: Imagens
""",
            "css_fundamentals.md": """
# CSS Fundamentals

CSS (Cascading Style Sheets) é usado para estilizar elementos HTML.

## Seletores Básicos

```css
/* Seletor de elemento */
h1 {
    color: blue;
    font-size: 24px;
}

/* Seletor de classe */
.minha-classe {
    background-color: yellow;
}

/* Seletor de ID */
#meu-id {
    margin: 10px;
}
```

## Box Model

O modelo de caixa CSS consiste em:
- Content (conteúdo)
- Padding (preenchimento)
- Border (borda)
- Margin (margem)
""",
            "javascript_intro.md": """
# Introdução ao JavaScript

JavaScript é uma linguagem de programação que permite criar páginas web interativas.

## Variáveis

```javascript
// Declaração de variáveis
let nome = "João";
const idade = 25;
var cidade = "São Paulo";
```

## Funções

```javascript
// Função tradicional
function saudacao(nome) {
    return "Olá, " + nome + "!";
}

// Arrow function
const saudacaoArrow = (nome) => {
    return `Olá, ${nome}!`;
};
```

## DOM Manipulation

```javascript
// Selecionar elementos
const elemento = document.getElementById("meuId");
const elementos = document.querySelectorAll(".minhaClasse");

// Modificar conteúdo
elemento.textContent = "Novo texto";
elemento.innerHTML = "<strong>Texto em negrito</strong>";
```
""",
            "react_basics.md": """
# React Básico

React é uma biblioteca JavaScript para construir interfaces de usuário.

## Componentes

```jsx
// Componente funcional
function MeuComponente(props) {
    return (
        <div>
            <h1>Olá, {props.nome}!</h1>
        </div>
    );
}

// Componente com hooks
import React, { useState } from 'react';

function Contador() {
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <p>Você clicou {count} vezes</p>
            <button onClick={() => setCount(count + 1)}>
                Clique aqui
            </button>
        </div>
    );
}
```

## Props e State

- **Props**: Dados passados de componente pai para filho
- **State**: Dados internos do componente que podem mudar
""",
            "web_accessibility.md": """
# Acessibilidade Web

A acessibilidade web garante que sites sejam usáveis por pessoas com deficiências.

## Princípios WCAG

1. **Perceptível**: Informação deve ser apresentada de forma que usuários possam perceber
2. **Operável**: Interface deve ser operável por todos os usuários
3. **Compreensível**: Informação e operação da interface devem ser compreensíveis
4. **Robusto**: Conteúdo deve ser robusto o suficiente para ser interpretado por tecnologias assistivas

## Boas Práticas

```html
<!-- Use alt text em imagens -->
<img src="logo.png" alt="Logo da empresa">

<!-- Use labels em formulários -->
<label for="email">Email:</label>
<input type="email" id="email" name="email">

<!-- Use headings hierárquicos -->
<h1>Título Principal</h1>
<h2>Subtítulo</h2>
<h3>Sub-subtítulo</h3>
```

## ARIA

ARIA (Accessible Rich Internet Applications) fornece semântica adicional:

```html
<button aria-label="Fechar modal" onclick="closeModal()">
    ×
</button>

<div role="alert" aria-live="polite">
    Mensagem de sucesso
</div>
```
"""
        }
        
        # Criar arquivos de exemplo
        for filename, content in sample_data.items():
            file_path = self.test_corpus_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Criados {len(sample_data)} arquivos de exemplo")
    
    def test_processing_pipeline(self):
        """Testa o pipeline de processamento."""
        logger.info("Testando pipeline de processamento...")
        
        try:
            # Importar e usar o processador
            import sys
            sys.path.append(str(self.base_dir))
            
            from process_corpus import CorpusProcessor
            
            # Criar processador com diretórios de teste
            processor = CorpusProcessor(
                corpus_dir=str(self.test_corpus_dir),
                output_dir=str(self.test_processed_dir)
            )
            
            # Executar processamento
            processor.run_processing()
            
            # Verificar se arquivos foram criados
            batch_files = list(self.test_processed_dir.glob("chunks_batch_*.json"))
            metadata_file = self.test_processed_dir / "processing_metadata.json"
            
            if batch_files and metadata_file.exists():
                logger.info("✅ Pipeline de processamento funcionando")
                
                # Mostrar estatísticas
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    logger.info(f"Chunks processados: {metadata['total_chunks']}")
                    logger.info(f"Estatísticas: {metadata['statistics']}")
                
                return True
            else:
                logger.error("❌ Pipeline de processamento falhou")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no pipeline de processamento: {e}")
            return False
    
    async def test_ingestion_pipeline(self):
        """Testa o pipeline de ingestão."""
        logger.info("Testando pipeline de ingestão...")
        
        try:
            # Verificar se OPENAI_API_KEY está configurada
            if not os.getenv('OPENAI_API_KEY'):
                logger.error("❌ OPENAI_API_KEY não configurada")
                return False
            
            # Importar e usar o ingestor
            import sys
            sys.path.append(str(self.base_dir))
            
            from ingest_to_rag import RAGIngestor
            
            # Criar ingestor com diretórios de teste
            ingestor = RAGIngestor(
                processed_corpus_dir=str(self.test_processed_dir),
                rag_data_dir=str(self.test_rag_data_dir)
            )
            
            # Executar ingestão
            await ingestor.run_ingestion()
            
            # Verificar se índice foi criado
            index_file = self.test_rag_data_dir / "faiss_index.bin"
            metadata_file = self.test_rag_data_dir / "chunk_metadata.json"
            
            if index_file.exists() and metadata_file.exists():
                logger.info("✅ Pipeline de ingestão funcionando")
                
                # Testar busca
                results = ingestor.test_search("Como criar um componente React?", top_k=3)
                
                if results:
                    logger.info(f"✅ Busca funcionando - {len(results)} resultados encontrados")
                    for i, result in enumerate(results, 1):
                        logger.info(f"  {i}. {result['title']} (Score: {result['similarity_score']:.3f})")
                    return True
                else:
                    logger.error("❌ Busca não retornou resultados")
                    return False
            else:
                logger.error("❌ Pipeline de ingestão falhou")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no pipeline de ingestão: {e}")
            return False
    
    def test_search_quality(self):
        """Testa a qualidade das buscas."""
        logger.info("Testando qualidade das buscas...")
        
        try:
            import sys
            sys.path.append(str(self.base_dir))
            
            from ingest_to_rag import RAGIngestor
            
            ingestor = RAGIngestor(
                processed_corpus_dir=str(self.test_processed_dir),
                rag_data_dir=str(self.test_rag_data_dir)
            )
            
            # Carregar índice existente
            if not ingestor.load_existing_index():
                logger.error("❌ Não foi possível carregar índice para teste")
                return False
            
            # Queries de teste
            test_queries = [
                "Como criar um componente React?",
                "O que é o box model do CSS?",
                "Como manipular o DOM com JavaScript?",
                "Quais são os princípios de acessibilidade web?",
                "Como declarar variáveis em JavaScript?"
            ]
            
            all_passed = True
            
            for query in test_queries:
                results = ingestor.test_search(query, top_k=2)
                
                if results and len(results) > 0:
                    best_score = results[0]['similarity_score']
                    logger.info(f"✅ '{query}' - Score: {best_score:.3f}")
                    
                    # Verificar se o score é razoável (> 0.5 para dados relacionados)
                    if best_score < 0.3:
                        logger.warning(f"⚠️  Score baixo para: {query}")
                else:
                    logger.error(f"❌ Nenhum resultado para: {query}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de qualidade: {e}")
            return False
    
    async def run_full_test_suite(self):
        """Executa suite completa de testes."""
        logger.info("=== INICIANDO SUITE DE TESTES DO RAG ===")
        
        test_results = {
            "corpus_creation": False,
            "processing_pipeline": False,
            "ingestion_pipeline": False,
            "search_quality": False
        }
        
        try:
            # 1. Criar corpus de exemplo
            self.create_sample_corpus()
            test_results["corpus_creation"] = True
            
            # 2. Testar processamento
            test_results["processing_pipeline"] = self.test_processing_pipeline()
            
            # 3. Testar ingestão
            if test_results["processing_pipeline"]:
                test_results["ingestion_pipeline"] = await self.test_ingestion_pipeline()
            
            # 4. Testar qualidade da busca
            if test_results["ingestion_pipeline"]:
                test_results["search_quality"] = self.test_search_quality()
            
            # Resultados finais
            logger.info("=== RESULTADOS DOS TESTES ===")
            
            for test_name, passed in test_results.items():
                status = "✅ PASSOU" if passed else "❌ FALHOU"
                logger.info(f"{test_name}: {status}")
            
            all_passed = all(test_results.values())
            
            if all_passed:
                logger.info("🎉 TODOS OS TESTES PASSARAM!")
                logger.info("O sistema RAG está funcionando corretamente.")
            else:
                logger.error("❌ ALGUNS TESTES FALHARAM")
                logger.error("Verifique os logs acima para detalhes.")
            
            return all_passed
            
        except Exception as e:
            logger.error(f"❌ Erro durante execução dos testes: {e}")
            return False
        
        finally:
            # Limpeza (opcional)
            # self.cleanup_test_dirs()
            pass

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste do sistema RAG')
    parser.add_argument('--keep-test-data', action='store_true',
                       help='Manter dados de teste após execução')
    
    args = parser.parse_args()
    
    # Executar testes
    test_suite = RAGTestSuite()
    
    success = asyncio.run(test_suite.run_full_test_suite())
    
    if not args.keep_test_data:
        test_suite.cleanup_test_dirs()
        logger.info("Dados de teste removidos")
    
    if success:
        print("\n✅ Sistema RAG validado com sucesso!")
        print("Pronto para processar dados reais.")
    else:
        print("\n❌ Validação do sistema RAG falhou.")
        print("Verifique os logs para detalhes.")
        exit(1)

if __name__ == "__main__":
    main()