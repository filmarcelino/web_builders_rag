#!/usr/bin/env python3
"""
Teste simplificado para coleta de conteúdo comercial.
Testa apenas a funcionalidade de coleta sem processar o corpus completo.
"""

import asyncio
import logging
from commercial_content_pipeline import CommercialContentCollector, CommercialSource

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_single_source():
    """Testa coleta de uma única fonte para validação."""
    logger.info("=== TESTE DE COLETA COMERCIAL ===")
    
    # Criar coletor
    collector = CommercialContentCollector()
    
    # Definir fonte de teste (Supabase - mais simples e confiável)
    test_source = CommercialSource(
        name="supabase_test",
        category="backend_service",
        base_url="https://supabase.com",
        documentation_urls=[
            "https://supabase.com/docs/guides/getting-started",
            "https://supabase.com/docs/guides/database"
        ],
        api_docs_urls=[
            "https://supabase.com/docs/reference/javascript/introduction"
        ],
        tutorial_urls=[
            "https://supabase.com/docs/guides/auth"
        ],
        priority="high",
        rate_limit=2.0,
        headers={},
        content_selectors={
            "main_content": ".prose, .content, article, main",
            "code_blocks": "pre, code",
            "headings": "h1, h2, h3, h4"
        }
    )
    
    try:
        # Testar coleta
        logger.info(f"Testando coleta de: {test_source.name}")
        content = collector.collect_source_content(test_source)
        
        if content:
            logger.info(f"✅ Coleta bem-sucedida: {len(content)} itens coletados")
            
            # Mostrar estatísticas
            total_tokens = sum(item['token_count'] for item in content)
            logger.info(f"📊 Total de tokens: {total_tokens}")
            
            # Mostrar amostra do conteúdo
            for i, item in enumerate(content[:3]):  # Primeiros 3 itens
                logger.info(f"\n--- Item {i+1} ---")
                logger.info(f"Título: {item['title'][:100]}...")
                logger.info(f"URL: {item['url']}")
                logger.info(f"Tokens: {item['token_count']}")
                logger.info(f"Conteúdo (preview): {item['content'][:200]}...")
            
            # Salvar conteúdo
            collector.save_collected_content(test_source.name, content)
            logger.info(f"💾 Conteúdo salvo em: corpus/commercial_tools/{test_source.name}/")
            
        else:
            logger.warning("❌ Nenhum conteúdo foi coletado")
            
    except Exception as e:
        logger.error(f"❌ Erro durante coleta: {e}")
        raise
    
    logger.info("=== TESTE CONCLUÍDO ===")

async def test_multiple_sources():
    """Testa coleta de múltiplas fontes prioritárias."""
    logger.info("=== TESTE DE MÚLTIPLAS FONTES ===")
    
    collector = CommercialContentCollector()
    
    # Fontes de teste (limitadas para validação)
    test_sources = [
        CommercialSource(
            name="godot_docs",
            category="game_engine",
            base_url="https://docs.godotengine.org",
            documentation_urls=[
                "https://docs.godotengine.org/en/stable/getting_started/introduction/index.html"
            ],
            api_docs_urls=[],
            tutorial_urls=[
                "https://docs.godotengine.org/en/stable/getting_started/first_2d_game/index.html"
            ],
            priority="high",
            rate_limit=1.0,
            headers={},
            content_selectors={
                "main_content": ".document, .content, article",
                "code_blocks": "pre, code",
                "headings": "h1, h2, h3, h4"
            }
        ),
        
        CommercialSource(
            name="firebase_docs",
            category="backend_service",
            base_url="https://firebase.google.com",
            documentation_urls=[
                "https://firebase.google.com/docs/build"
            ],
            api_docs_urls=[],
            tutorial_urls=[
                "https://firebase.google.com/docs/web/setup"
            ],
            priority="high",
            rate_limit=1.0,
            headers={},
            content_selectors={
                "main_content": ".devsite-article-body, .content, article",
                "code_blocks": "pre, code",
                "headings": "h1, h2, h3, h4"
            }
        )
    ]
    
    total_collected = 0
    total_tokens = 0
    
    for source in test_sources:
        try:
            logger.info(f"\n🔄 Coletando: {source.name} ({source.category})")
            content = collector.collect_source_content(source)
            
            if content:
                source_tokens = sum(item['token_count'] for item in content)
                total_collected += len(content)
                total_tokens += source_tokens
                
                logger.info(f"✅ {source.name}: {len(content)} itens, {source_tokens} tokens")
                
                # Salvar
                collector.save_collected_content(source.name, content)
                
            else:
                logger.warning(f"⚠️ {source.name}: Nenhum conteúdo coletado")
                
        except Exception as e:
            logger.error(f"❌ Erro em {source.name}: {e}")
            continue
    
    logger.info(f"\n📊 RESUMO FINAL:")
    logger.info(f"Total de itens coletados: {total_collected}")
    logger.info(f"Total de tokens: {total_tokens}")
    logger.info(f"Fontes processadas: {len(test_sources)}")
    
    logger.info("=== TESTE DE MÚLTIPLAS FONTES CONCLUÍDO ===")

async def main():
    """Função principal de teste."""
    print("\n" + "="*60)
    print("TESTE DO SISTEMA DE COLETA DE CONTEÚDO COMERCIAL")
    print("="*60)
    
    try:
        # Teste 1: Fonte única
        await test_single_source()
        
        print("\n" + "-"*60)
        
        # Teste 2: Múltiplas fontes
        await test_multiple_sources()
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("📁 Verifique os arquivos em: corpus/commercial_tools/")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())