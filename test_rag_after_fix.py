#!/usr/bin/env python3
"""
Teste do RAG após remoção do sistema de controle de acesso
Verifica se a base de conhecimento está retornando resultados normalmente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.search.search_engine import SearchEngine, SearchRequest
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

async def test_rag_functionality():
    """Testa funcionalidade básica do RAG"""
    print("🔍 Testando funcionalidade do RAG após remoção do controle de acesso...\n")
    
    try:
        # Inicializar motor de busca
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY não encontrada no ambiente")
            return False
        
        # Usar o diretório correto onde estão os dados
        index_dir = "rag_data"
        search_engine = SearchEngine(api_key, index_dir)
        
        # Queries de teste variadas
        test_queries = [
            "CSS animations",
            "JavaScript functions",
            "HTML elements",
            "React components",
            "web development",
            "responsive design",
            "accessibility",
            "flexbox layout"
        ]
        
        results_summary = {
            'total_queries': len(test_queries),
            'successful_queries': 0,
            'failed_queries': 0,
            'total_results_found': 0,
            'queries_with_results': 0,
            'test_details': []
        }
        
        for i, query in enumerate(test_queries, 1):
            print(f"📝 Teste {i}/{len(test_queries)}: '{query}'")
            
            try:
                # Criar request de busca
                request = SearchRequest(
                    query=query,
                    top_k=5,
                    rerank=True,
                    use_cache=False
                )
                
                # Executar busca
                response = await search_engine.search(request)
                
                # Analisar resultados
                num_results = len(response.results)
                has_content = any(result.get('content', '').strip() for result in response.results)
                
                test_detail = {
                    'query': query,
                    'num_results': num_results,
                    'has_content': has_content,
                    'processing_time': response.processing_time,
                    'access_control': response.search_stats.get('access_control', {}),
                    'status': 'SUCCESS' if num_results > 0 and has_content else 'NO_RESULTS'
                }
                
                results_summary['test_details'].append(test_detail)
                results_summary['total_results_found'] += num_results
                
                if num_results > 0 and has_content:
                    results_summary['successful_queries'] += 1
                    results_summary['queries_with_results'] += 1
                    print(f"   ✅ {num_results} resultados encontrados ({response.processing_time:.3f}s)")
                    
                    # Mostrar primeiro resultado como exemplo
                    if response.results:
                        first_result = response.results[0]
                        content_preview = first_result.get('content', '')[:100] + '...' if len(first_result.get('content', '')) > 100 else first_result.get('content', '')
                        print(f"   📄 Exemplo: {content_preview}")
                else:
                    print(f"   ❌ Nenhum resultado com conteúdo encontrado")
                    
            except Exception as e:
                print(f"   💥 Erro na busca: {str(e)}")
                results_summary['failed_queries'] += 1
                results_summary['test_details'].append({
                    'query': query,
                    'error': str(e),
                    'status': 'ERROR'
                })
            
            print()
        
        # Relatório final
        print("📊 RELATÓRIO FINAL:")
        print(f"   • Total de queries testadas: {results_summary['total_queries']}")
        print(f"   • Queries com sucesso: {results_summary['successful_queries']}")
        print(f"   • Queries com falha: {results_summary['failed_queries']}")
        print(f"   • Total de resultados encontrados: {results_summary['total_results_found']}")
        print(f"   • Taxa de sucesso: {(results_summary['successful_queries']/results_summary['total_queries']*100):.1f}%")
        
        # Verificar se o problema foi resolvido
        if results_summary['successful_queries'] > 0:
            print("\n🎉 SUCESSO: O RAG está funcionando! Base de conhecimento não está mais vazia.")
            print("✅ Sistema de controle de acesso removido com sucesso.")
        else:
            print("\n⚠️  PROBLEMA PERSISTE: RAG ainda não está retornando resultados.")
            print("❌ Pode haver outros problemas além do controle de acesso.")
        
        # Salvar relatório detalhado
        report_filename = f"rag_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório detalhado salvo em: {report_filename}")
        
        return results_summary['successful_queries'] > 0
        
    except Exception as e:
        print(f"💥 Erro crítico no teste: {str(e)}")
        return False
    
    finally:
        try:
            search_engine.close()
        except:
            pass

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_rag_functionality())
    sys.exit(0 if success else 1)