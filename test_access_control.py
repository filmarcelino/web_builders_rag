#!/usr/bin/env python3
"""
Script para testar o sistema de controle de acesso do RAG
Testa se as informações sobre criação de agentes só são liberadas com 'vinapermitecriar'
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# Adicionar src ao path
sys.path.append('src')

from search.search_engine import SearchEngine, SearchRequest
from indexing.index_manager import IndexManager
from search.query_processor import QueryProcessor
from search.search_cache import SearchCache
from reranking.animation_reranker import AnimationReranker
from prompts.animation_prompt_enhancer import AnimationPromptEnhancer
from response.rag_response_generator import RAGResponseGenerator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_access_control():
    """Testa o sistema de controle de acesso"""
    
    logger.info("🔍 Iniciando teste do sistema de controle de acesso")
    
    # Inicializar componentes do RAG
    try:
        # Usar API key de demonstração como nos outros testes
        api_key = "demo-api-key"
        
        search_engine = SearchEngine(api_key=api_key)
        
        logger.info("✅ Componentes do RAG inicializados com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar componentes: {e}")
        return False
    
    # Casos de teste
    test_cases = [
        {
            "name": "Consulta sem palavra-chave - deve ser bloqueada",
            "query": "Como criar um agente AI usando LangGraph?",
            "should_have_access": False,
            "expected_restricted_count": "> 0"
        },
        {
            "name": "Consulta com palavra-chave - deve ter acesso",
            "query": "vinapermitecriar Como criar um agente AI usando LangGraph?",
            "should_have_access": True,
            "expected_restricted_count": "0"
        },
        {
            "name": "Consulta sobre animação - não deve ser afetada",
            "query": "Como criar animações CSS com keyframes?",
            "should_have_access": True,
            "expected_restricted_count": "0"
        },
        {
            "name": "Consulta sobre frameworks sem palavra-chave",
            "query": "Quais são os melhores frameworks para agentes AI?",
            "should_have_access": False,
            "expected_restricted_count": "> 0"
        },
        {
            "name": "Consulta sobre frameworks com palavra-chave",
            "query": "vinapermitecriar Quais são os melhores frameworks para agentes AI?",
            "should_have_access": True,
            "expected_restricted_count": "0"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n🧪 Teste {i}: {test_case['name']}")
        logger.info(f"📝 Query: {test_case['query']}")
        
        try:
            # Criar requisição de busca
            search_request = SearchRequest(
                query=test_case['query'],
                top_k=10,
                include_rationale=True
            )
            
            # Executar busca
            search_response = await search_engine.search(search_request)
            
            # Verificar estatísticas de controle de acesso
            access_stats = search_response.search_stats.get('access_control', {})
            
            access_granted = access_stats.get('access_granted', False)
            restricted_count = access_stats.get('restricted_items_count', 0)
            auth_found = access_stats.get('authorization_found', False)
            access_message = access_stats.get('message', 'N/A')
            
            # Verificar se o resultado está correto
            test_passed = access_granted == test_case['should_have_access']
            
            if test_case['expected_restricted_count'] == '0':
                test_passed = test_passed and (restricted_count == 0)
            elif test_case['expected_restricted_count'] == '> 0':
                test_passed = test_passed and (restricted_count > 0)
            
            # Log dos resultados
            logger.info(f"🔐 Acesso concedido: {access_granted}")
            logger.info(f"🔑 Autorização encontrada: {auth_found}")
            logger.info(f"🚫 Itens restritos: {restricted_count}")
            logger.info(f"💬 Mensagem: {access_message}")
            logger.info(f"📊 Resultados retornados: {len(search_response.results)}")
            
            if test_passed:
                logger.info(f"✅ Teste {i} PASSOU")
            else:
                logger.error(f"❌ Teste {i} FALHOU")
                logger.error(f"   Esperado acesso: {test_case['should_have_access']}, Obtido: {access_granted}")
                logger.error(f"   Esperado restritos: {test_case['expected_restricted_count']}, Obtido: {restricted_count}")
            
            # Salvar resultado
            results.append({
                "test_number": i,
                "test_name": test_case['name'],
                "query": test_case['query'],
                "expected_access": test_case['should_have_access'],
                "actual_access": access_granted,
                "authorization_found": auth_found,
                "restricted_count": restricted_count,
                "results_count": len(search_response.results),
                "access_message": access_message,
                "test_passed": test_passed
            })
            
        except Exception as e:
            logger.error(f"❌ Erro no teste {i}: {e}")
            results.append({
                "test_number": i,
                "test_name": test_case['name'],
                "query": test_case['query'],
                "error": str(e),
                "test_passed": False
            })
    
    # Resumo dos resultados
    passed_tests = sum(1 for r in results if r.get('test_passed', False))
    total_tests = len(results)
    
    logger.info(f"\n📊 RESUMO DOS TESTES")
    logger.info(f"✅ Testes aprovados: {passed_tests}/{total_tests}")
    logger.info(f"📈 Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
    
    # Salvar relatório detalhado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"access_control_test_report_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests/total_tests)*100
        },
        "test_results": results
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"📄 Relatório salvo em: {report_file}")
    
    if passed_tests == total_tests:
        logger.info("🎉 TODOS OS TESTES PASSARAM! Sistema de controle de acesso funcionando corretamente.")
        return True
    else:
        logger.error(f"⚠️  {total_tests - passed_tests} teste(s) falharam. Verifique o sistema de controle de acesso.")
        return False

async def main():
    """Função principal"""
    logger.info("🚀 Iniciando teste do sistema de controle de acesso do RAG")
    
    success = await test_access_control()
    
    if success:
        logger.info("\n🎯 Sistema de controle de acesso validado com sucesso!")
        logger.info("🔒 Informações sobre criação de agentes estão protegidas pela palavra-chave 'vinapermitecriar'")
    else:
        logger.error("\n❌ Sistema de controle de acesso apresentou problemas")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())