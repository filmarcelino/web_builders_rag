#!/usr/bin/env python3
"""
Teste simplificado do sistema de controle de acesso
Testa apenas a lógica de detecção da palavra-chave sem dependências externas
"""

import sys
import logging
from datetime import datetime

# Adicionar src ao path
sys.path.append('src')

from search.access_control import AccessController

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_access_control_logic():
    """Testa a lógica básica do controle de acesso"""
    
    logger.info("🔍 Testando lógica do sistema de controle de acesso")
    
    # Inicializar controlador de acesso
    access_controller = AccessController()
    
    # Casos de teste
    test_cases = [
        {
            "name": "Consulta sem palavra-chave",
            "query": "Como criar um agente AI usando LangGraph?",
            "expected_authorized": False
        },
        {
            "name": "Consulta com palavra-chave no início",
            "query": "vinapermitecriar Como criar um agente AI?",
            "expected_authorized": True
        },
        {
            "name": "Consulta com palavra-chave no meio",
            "query": "Como vinapermitecriar criar agentes?",
            "expected_authorized": True
        },
        {
            "name": "Consulta com palavra-chave no final",
            "query": "Como criar agentes AI vinapermitecriar",
            "expected_authorized": True
        },
        {
            "name": "Consulta sobre animação - não precisa de autorização",
            "query": "Como criar animações CSS?",
            "expected_authorized": False  # Não precisa de autorização para animações
        },
        {
            "name": "Palavra-chave parcial - não deve autorizar",
            "query": "Como usar vinapermite para criar agentes?",
            "expected_authorized": False
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n🧪 Teste {i}: {test_case['name']}")
        logger.info(f"📝 Query: {test_case['query']}")
        
        # Testar detecção de autorização
        is_authorized = access_controller._check_authorization(test_case['query'])
        
        # Verificar se o resultado está correto
        test_passed = is_authorized == test_case['expected_authorized']
        
        logger.info(f"🔐 Autorização detectada: {is_authorized}")
        logger.info(f"🎯 Esperado: {test_case['expected_authorized']}")
        
        if test_passed:
            logger.info(f"✅ Teste {i} PASSOU")
        else:
            logger.error(f"❌ Teste {i} FALHOU")
        
        results.append({
            "test_number": i,
            "test_name": test_case['name'],
            "query": test_case['query'],
            "expected_authorized": test_case['expected_authorized'],
            "actual_authorized": is_authorized,
            "test_passed": test_passed
        })
    
    # Testar classificação de chunks
    logger.info("\n🔍 Testando classificação de chunks restritos")
    
    # Chunks de teste
    test_chunks = [
        {
            "content": "Como criar animações CSS com keyframes",
            "metadata": {"category": "animation"},
            "expected_restricted": False
        },
        {
            "content": "Guia para criar agentes AI com LangGraph",
            "metadata": {"restricted": True, "access_level": "agent_builder"},
            "expected_restricted": True
        },
        {
            "content": "Tutorial sobre React hooks",
            "metadata": {"category": "react"},
            "expected_restricted": False
        },
        {
            "content": "Framework AutoAgent para criação de agentes",
            "metadata": {"restricted": True, "access_level": "agent_builder"},
            "expected_restricted": True
        }
    ]
    
    chunk_results = []
    
    for i, chunk in enumerate(test_chunks, 1):
        is_restricted = access_controller._is_restricted_content(chunk)
        expected = chunk['expected_restricted']
        test_passed = is_restricted == expected
        
        logger.info(f"📄 Chunk {i}: {chunk['content'][:50]}...")
        logger.info(f"🔒 Restrito: {is_restricted} (esperado: {expected})")
        
        if test_passed:
            logger.info(f"✅ Classificação {i} CORRETA")
        else:
            logger.error(f"❌ Classificação {i} INCORRETA")
        
        chunk_results.append({
            "chunk_number": i,
            "content_preview": chunk['content'][:50],
            "expected_restricted": expected,
            "actual_restricted": is_restricted,
            "test_passed": test_passed
        })
    
    # Resumo dos resultados
    auth_passed = sum(1 for r in results if r['test_passed'])
    chunk_passed = sum(1 for r in chunk_results if r['test_passed'])
    total_auth_tests = len(results)
    total_chunk_tests = len(chunk_results)
    
    logger.info(f"\n📊 RESUMO DOS TESTES")
    logger.info(f"🔐 Testes de autorização: {auth_passed}/{total_auth_tests} ({(auth_passed/total_auth_tests)*100:.1f}%)")
    logger.info(f"📄 Testes de classificação: {chunk_passed}/{total_chunk_tests} ({(chunk_passed/total_chunk_tests)*100:.1f}%)")
    
    total_passed = auth_passed + chunk_passed
    total_tests = total_auth_tests + total_chunk_tests
    
    logger.info(f"🎯 Total geral: {total_passed}/{total_tests} ({(total_passed/total_tests)*100:.1f}%)")
    
    if total_passed == total_tests:
        logger.info("🎉 TODOS OS TESTES PASSARAM! Lógica de controle de acesso funcionando corretamente.")
        return True
    else:
        logger.error(f"⚠️  {total_tests - total_passed} teste(s) falharam.")
        return False

def main():
    """Função principal"""
    logger.info("🚀 Iniciando teste simplificado do controle de acesso")
    
    success = test_access_control_logic()
    
    if success:
        logger.info("\n🎯 Lógica de controle de acesso validada com sucesso!")
        logger.info("🔒 Sistema detecta corretamente a palavra-chave 'vinapermitecriar'")
        logger.info("📄 Sistema classifica corretamente conteúdo restrito")
    else:
        logger.error("\n❌ Problemas encontrados na lógica de controle de acesso")
        sys.exit(1)

if __name__ == "__main__":
    main()