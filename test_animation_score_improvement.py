#!/usr/bin/env python3
"""
Script de teste para validar melhorias no score de animação
Testa se o sistema consegue triplicar o score para consultas de animação
"""

import asyncio
import json
import time
from typing import Dict, List, Any
from datetime import datetime

# Imports do sistema
from src.search.search_engine import SearchEngine, SearchRequest
from src.response.rag_response_generator import RAGResponseGenerator
from config.config import RAGConfig

class AnimationScoreTest:
    """Classe para testar melhorias no score de animação"""
    
    def __init__(self):
        # Inicializar SearchEngine com API key
        api_key = RAGConfig.OPENAI_API_KEY or "your-openai-api-key-here"
        self.search_engine = SearchEngine(api_key)
        self.test_queries = {
            'animation': [
                "Como criar animações CSS com keyframes?",
                "Exemplos de transitions suaves em CSS",
                "Como fazer animações de transform rotate?",
                "Animação de fade in e fade out CSS",
                "Como criar hover effects com animação?"
            ],
            'non_animation': [
                "Como criar um layout responsivo?",
                "Melhores práticas de CSS Grid",
                "Como usar Flexbox para centralizar elementos?",
                "Cores e tipografia em CSS",
                "Como fazer um menu dropdown?"
            ]
        }
        
        self.results = {
            'animation_queries': [],
            'non_animation_queries': [],
            'score_improvements': {},
            'summary': {}
        }
    
    async def run_comprehensive_test(self):
        """Executa teste completo do sistema"""
        print("🚀 Iniciando teste de melhoria de score para animações...\n")
        
        # 1. Testar consultas de animação
        print("📊 Testando consultas de ANIMAÇÃO:")
        for query in self.test_queries['animation']:
            result = await self._test_single_query(query, is_animation=True)
            self.results['animation_queries'].append(result)
            print(f"  ✅ {query[:50]}... | Score: {result['avg_score']:.3f} | Boost: {result['animation_boost_applied']}")
        
        print("\n📊 Testando consultas NÃO-ANIMAÇÃO:")
        # 2. Testar consultas não-animação
        for query in self.test_queries['non_animation']:
            result = await self._test_single_query(query, is_animation=False)
            self.results['non_animation_queries'].append(result)
            print(f"  ✅ {query[:50]}... | Score: {result['avg_score']:.3f} | Boost: {result['animation_boost_applied']}")
        
        # 3. Calcular melhorias
        self._calculate_improvements()
        
        # 4. Gerar relatório
        self._generate_report()
        
        print("\n🎯 Teste concluído! Verifique o relatório gerado.")
    
    async def _test_single_query(self, query: str, is_animation: bool) -> Dict[str, Any]:
        """Testa uma única consulta"""
        start_time = time.time()
        
        try:
            # Fazer busca
            search_request = SearchRequest(
                query=query,
                top_k=10,
                filters={}
            )
            
            search_response = await self.search_engine.search(search_request)
            
            # Gerar resposta RAG completa
            rag_response = self.search_engine.generate_rag_response(query)
            
            # Calcular métricas
            scores = [result.score for result in search_response.results]
            avg_score = sum(scores) / len(scores) if scores else 0.0
            max_score = max(scores) if scores else 0.0
            
            # Verificar boost de animação
            animation_boost_applied = any(
                hasattr(result, 'animation_boost') and result.animation_boost > 1.0
                for result in search_response.results
            )
            
            processing_time = time.time() - start_time
            
            return {
                'query': query,
                'is_animation_expected': is_animation,
                'total_results': search_response.total_results,
                'avg_score': avg_score,
                'max_score': max_score,
                'scores': scores,
                'animation_boost_applied': animation_boost_applied,
                'rag_confidence': rag_response.confidence_score,
                'rag_enhanced_prompt': rag_response.enhanced_prompt_used,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'query': query,
                'is_animation_expected': is_animation,
                'error': str(e),
                'avg_score': 0.0,
                'max_score': 0.0,
                'scores': [],
                'animation_boost_applied': False,
                'rag_confidence': 0.0,
                'rag_enhanced_prompt': False,
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_improvements(self):
        """Calcula melhorias de score"""
        # Scores médios
        animation_scores = [r['avg_score'] for r in self.results['animation_queries'] if 'error' not in r]
        non_animation_scores = [r['avg_score'] for r in self.results['non_animation_queries'] if 'error' not in r]
        
        if animation_scores and non_animation_scores:
            avg_animation_score = sum(animation_scores) / len(animation_scores)
            avg_non_animation_score = sum(non_animation_scores) / len(non_animation_scores)
            
            # Calcular melhoria
            if avg_non_animation_score > 0:
                improvement_ratio = avg_animation_score / avg_non_animation_score
                improvement_percentage = ((avg_animation_score - avg_non_animation_score) / avg_non_animation_score) * 100
            else:
                improvement_ratio = 0
                improvement_percentage = 0
            
            self.results['score_improvements'] = {
                'avg_animation_score': avg_animation_score,
                'avg_non_animation_score': avg_non_animation_score,
                'improvement_ratio': improvement_ratio,
                'improvement_percentage': improvement_percentage,
                'target_achieved': improvement_ratio >= 3.0  # Meta de triplicar
            }
        
        # Estatísticas de boost
        animation_boost_count = sum(
            1 for r in self.results['animation_queries'] 
            if r.get('animation_boost_applied', False)
        )
        
        rag_enhancement_count = sum(
            1 for r in self.results['animation_queries'] 
            if r.get('rag_enhanced_prompt', False)
        )
        
        self.results['summary'] = {
            'total_animation_queries': len(self.results['animation_queries']),
            'total_non_animation_queries': len(self.results['non_animation_queries']),
            'animation_boost_applied_count': animation_boost_count,
            'rag_enhancement_applied_count': rag_enhancement_count,
            'animation_boost_rate': animation_boost_count / max(len(self.results['animation_queries']), 1),
            'rag_enhancement_rate': rag_enhancement_count / max(len(self.results['animation_queries']), 1)
        }
    
    def _generate_report(self):
        """Gera relatório detalhado"""
        report = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'Animation Score Improvement Test',
                'objective': 'Validar se o sistema consegue triplicar o score para consultas de animação'
            },
            'results': self.results,
            'analysis': self._generate_analysis()
        }
        
        # Salvar relatório
        filename = f"animation_score_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Imprimir resumo
        self._print_summary()
        
        print(f"\n📄 Relatório completo salvo em: {filename}")
    
    def _generate_analysis(self) -> Dict[str, Any]:
        """Gera análise dos resultados"""
        improvements = self.results.get('score_improvements', {})
        summary = self.results.get('summary', {})
        
        analysis = {
            'score_analysis': {
                'target_achieved': improvements.get('target_achieved', False),
                'improvement_ratio': improvements.get('improvement_ratio', 0),
                'improvement_percentage': improvements.get('improvement_percentage', 0),
                'interpretation': self._interpret_score_improvement(improvements)
            },
            'system_performance': {
                'animation_detection_rate': summary.get('animation_boost_rate', 0),
                'prompt_enhancement_rate': summary.get('rag_enhancement_rate', 0),
                'system_effectiveness': self._evaluate_system_effectiveness(summary)
            },
            'recommendations': self._generate_recommendations(improvements, summary)
        }
        
        return analysis
    
    def _interpret_score_improvement(self, improvements: Dict) -> str:
        """Interpreta melhoria de score"""
        ratio = improvements.get('improvement_ratio', 0)
        
        if ratio >= 3.0:
            return "🎉 EXCELENTE! Meta de triplicar o score foi ALCANÇADA!"
        elif ratio >= 2.0:
            return "✅ BOM! Score dobrou, próximo da meta de triplicar."
        elif ratio >= 1.5:
            return "⚠️ MODERADO. Score melhorou 50%, mas ainda longe da meta."
        elif ratio >= 1.1:
            return "⚠️ BAIXO. Pequena melhoria detectada."
        else:
            return "❌ CRÍTICO. Nenhuma melhoria significativa detectada."
    
    def _evaluate_system_effectiveness(self, summary: Dict) -> str:
        """Avalia efetividade do sistema"""
        boost_rate = summary.get('animation_boost_rate', 0)
        enhancement_rate = summary.get('rag_enhancement_rate', 0)
        
        if boost_rate >= 0.8 and enhancement_rate >= 0.8:
            return "🔥 SISTEMA ALTAMENTE EFETIVO"
        elif boost_rate >= 0.6 and enhancement_rate >= 0.6:
            return "✅ SISTEMA EFETIVO"
        elif boost_rate >= 0.4 or enhancement_rate >= 0.4:
            return "⚠️ SISTEMA PARCIALMENTE EFETIVO"
        else:
            return "❌ SISTEMA PRECISA DE AJUSTES"
    
    def _generate_recommendations(self, improvements: Dict, summary: Dict) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        ratio = improvements.get('improvement_ratio', 0)
        boost_rate = summary.get('animation_boost_rate', 0)
        enhancement_rate = summary.get('rag_enhancement_rate', 0)
        
        if ratio < 3.0:
            recommendations.append("Aumentar o fator de boost para chunks de animação")
            recommendations.append("Melhorar detecção de palavras-chave de animação")
        
        if boost_rate < 0.8:
            recommendations.append("Refinar algoritmo de detecção de consultas de animação")
            recommendations.append("Expandir lista de termos relacionados a animação")
        
        if enhancement_rate < 0.8:
            recommendations.append("Aprimorar prompt especializado para animações")
            recommendations.append("Adicionar mais contexto específico de animação")
        
        if not recommendations:
            recommendations.append("Sistema funcionando bem! Considerar otimizações de performance.")
        
        return recommendations
    
    def _print_summary(self):
        """Imprime resumo dos resultados"""
        improvements = self.results.get('score_improvements', {})
        summary = self.results.get('summary', {})
        
        print("\n" + "="*60)
        print("📊 RESUMO DOS RESULTADOS")
        print("="*60)
        
        print(f"\n🎯 OBJETIVO: Triplicar score para consultas de animação")
        print(f"\n📈 RESULTADOS DE SCORE:")
        print(f"   • Score médio (animação): {improvements.get('avg_animation_score', 0):.3f}")
        print(f"   • Score médio (não-animação): {improvements.get('avg_non_animation_score', 0):.3f}")
        print(f"   • Razão de melhoria: {improvements.get('improvement_ratio', 0):.2f}x")
        print(f"   • Melhoria percentual: {improvements.get('improvement_percentage', 0):.1f}%")
        print(f"   • Meta alcançada: {'✅ SIM' if improvements.get('target_achieved', False) else '❌ NÃO'}")
        
        print(f"\n🔧 PERFORMANCE DO SISTEMA:")
        print(f"   • Taxa de boost aplicado: {summary.get('animation_boost_rate', 0):.1%}")
        print(f"   • Taxa de prompt aprimorado: {summary.get('rag_enhancement_rate', 0):.1%}")
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   • Consultas de animação testadas: {summary.get('total_animation_queries', 0)}")
        print(f"   • Consultas não-animação testadas: {summary.get('total_non_animation_queries', 0)}")
        print(f"   • Boosts aplicados: {summary.get('animation_boost_applied_count', 0)}")
        print(f"   • Prompts aprimorados: {summary.get('rag_enhancement_applied_count', 0)}")

async def main():
    """Função principal"""
    test = AnimationScoreTest()
    await test.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())