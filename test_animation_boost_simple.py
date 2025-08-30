#!/usr/bin/env python3
"""
Teste simplificado para validar o sistema de boost de animação
Testa apenas os componentes de detecção e boost sem depender da API OpenAI
"""

import json
import time
from typing import Dict, List, Any
from datetime import datetime

# Imports do sistema
from src.prompts.animation_prompt_enhancer import AnimationPromptEnhancer
from src.reranking.animation_reranker import AnimationReranker

class AnimationBoostTest:
    """Teste simplificado para validar boost de animação"""
    
    def __init__(self):
        self.animation_enhancer = AnimationPromptEnhancer()
        self.animation_reranker = AnimationReranker()
        
        # Dados de teste simulados
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
        
        # Chunks simulados
        self.sample_chunks = [
            {
                'content': '@keyframes fadeIn { 0% { opacity: 0; } 100% { opacity: 1; } }',
                'source': 'CSS Animation Guide',
                'similarity_score': 0.85,
                'metadata': {'type': 'animation', 'technique': 'keyframes'}
            },
            {
                'content': '.element { transition: all 0.3s ease-in-out; }',
                'source': 'CSS Transitions Tutorial',
                'similarity_score': 0.80,
                'metadata': {'type': 'animation', 'technique': 'transition'}
            },
            {
                'content': '.rotate { transform: rotate(45deg); }',
                'source': 'CSS Transform Examples',
                'similarity_score': 0.75,
                'metadata': {'type': 'animation', 'technique': 'transform'}
            },
            {
                'content': '.container { display: flex; justify-content: center; }',
                'source': 'Flexbox Guide',
                'similarity_score': 0.70,
                'metadata': {'type': 'layout'}
            },
            {
                'content': '.grid { display: grid; grid-template-columns: 1fr 1fr; }',
                'source': 'CSS Grid Tutorial',
                'similarity_score': 0.65,
                'metadata': {'type': 'layout'}
            }
        ]
        
        self.results = {
            'detection_tests': [],
            'boost_tests': [],
            'prompt_enhancement_tests': [],
            'summary': {}
        }
    
    def run_comprehensive_test(self):
        """Executa teste completo do sistema"""
        print("🚀 Iniciando teste de boost de animação (modo simplificado)...\n")
        
        # 1. Testar detecção de consultas de animação
        print("🔍 Testando DETECÇÃO de consultas de animação:")
        self._test_animation_detection()
        
        # 2. Testar boost de chunks
        print("\n📈 Testando BOOST de chunks de animação:")
        self._test_chunk_boosting()
        
        # 3. Testar aprimoramento de prompts
        print("\n✨ Testando APRIMORAMENTO de prompts:")
        self._test_prompt_enhancement()
        
        # 4. Calcular estatísticas
        self._calculate_statistics()
        
        # 5. Gerar relatório
        self._generate_report()
        
        print("\n🎯 Teste concluído! Verifique o relatório gerado.")
    
    def _test_animation_detection(self):
        """Testa detecção de consultas de animação"""
        for query_type, queries in self.test_queries.items():
            is_animation_expected = query_type == 'animation'
            
            for query in queries:
                is_detected = self.animation_enhancer.is_animation_query(query)
                
                result = {
                    'query': query,
                    'expected_animation': is_animation_expected,
                    'detected_animation': is_detected,
                    'correct_detection': is_detected == is_animation_expected
                }
                
                self.results['detection_tests'].append(result)
                
                status = "✅" if result['correct_detection'] else "❌"
                print(f"  {status} {query[:50]}... | Esperado: {is_animation_expected} | Detectado: {is_detected}")
    
    def _test_chunk_boosting(self):
        """Testa boost de chunks de animação"""
        for query_type, queries in self.test_queries.items():
            for query in queries[:2]:  # Testar apenas 2 consultas por tipo
                # Fazer cópia dos chunks originais para comparação
                original_chunks = [chunk.copy() for chunk in self.sample_chunks]
                
                # Aplicar boost
                boosted_chunks = self.animation_enhancer.get_animation_context_boost(
                    self.sample_chunks.copy()
                )
                
                # Calcular estatísticas de boost
                original_scores = [c['similarity_score'] for c in original_chunks]
                boosted_scores = [c['similarity_score'] for c in boosted_chunks]
                
                animation_chunks = [c for c in boosted_chunks if c.get('animation_boost_applied', False)]
                
                result = {
                    'query': query,
                    'query_type': query_type,
                    'original_avg_score': sum(original_scores) / len(original_scores),
                    'boosted_avg_score': sum(boosted_scores) / len(boosted_scores),
                    'animation_chunks_boosted': len(animation_chunks),
                    'total_chunks': len(boosted_chunks),
                    'boost_applied': len(animation_chunks) > 0
                }
                
                if result['original_avg_score'] > 0:
                    result['score_improvement_ratio'] = result['boosted_avg_score'] / result['original_avg_score']
                else:
                    result['score_improvement_ratio'] = 1.0
                
                self.results['boost_tests'].append(result)
                
                print(f"  📊 {query[:40]}... | Boost: {result['boost_applied']} | Ratio: {result['score_improvement_ratio']:.2f}x")
    
    def _test_prompt_enhancement(self):
        """Testa aprimoramento de prompts"""
        base_system_prompt = "Você é um assistente de desenvolvimento web."
        
        for query_type, queries in self.test_queries.items():
            for query in queries[:2]:  # Testar apenas 2 consultas por tipo
                is_animation = self.animation_enhancer.is_animation_query(query)
                
                if is_animation:
                    enhanced_system = self.animation_enhancer.enhance_system_prompt(base_system_prompt)
                    enhanced_user = self.animation_enhancer.enhance_user_prompt(query, "contexto de teste")
                else:
                    enhanced_system = base_system_prompt
                    enhanced_user = query
                
                result = {
                    'query': query,
                    'query_type': query_type,
                    'is_animation_query': is_animation,
                    'system_prompt_enhanced': enhanced_system != base_system_prompt,
                    'user_prompt_enhanced': enhanced_user != query,
                    'enhancement_applied': is_animation
                }
                
                self.results['prompt_enhancement_tests'].append(result)
                
                status = "✨" if result['enhancement_applied'] else "📝"
                print(f"  {status} {query[:40]}... | Enhanced: {result['enhancement_applied']}")
    
    def _calculate_statistics(self):
        """Calcula estatísticas dos testes"""
        # Estatísticas de detecção
        detection_correct = sum(1 for r in self.results['detection_tests'] if r['correct_detection'])
        detection_total = len(self.results['detection_tests'])
        detection_accuracy = detection_correct / detection_total if detection_total > 0 else 0
        
        # Estatísticas de boost
        boost_applied_count = sum(1 for r in self.results['boost_tests'] if r['boost_applied'])
        boost_total = len(self.results['boost_tests'])
        
        animation_boost_ratios = [
            r['score_improvement_ratio'] for r in self.results['boost_tests'] 
            if r['query_type'] == 'animation'
        ]
        non_animation_boost_ratios = [
            r['score_improvement_ratio'] for r in self.results['boost_tests'] 
            if r['query_type'] == 'non_animation'
        ]
        
        avg_animation_boost = sum(animation_boost_ratios) / len(animation_boost_ratios) if animation_boost_ratios else 1.0
        avg_non_animation_boost = sum(non_animation_boost_ratios) / len(non_animation_boost_ratios) if non_animation_boost_ratios else 1.0
        
        # Estatísticas de aprimoramento
        enhancement_applied_count = sum(1 for r in self.results['prompt_enhancement_tests'] if r['enhancement_applied'])
        enhancement_total = len(self.results['prompt_enhancement_tests'])
        
        self.results['summary'] = {
            'detection_accuracy': detection_accuracy,
            'detection_correct': detection_correct,
            'detection_total': detection_total,
            'boost_application_rate': boost_applied_count / boost_total if boost_total > 0 else 0,
            'avg_animation_boost_ratio': avg_animation_boost,
            'avg_non_animation_boost_ratio': avg_non_animation_boost,
            'boost_effectiveness': avg_animation_boost / avg_non_animation_boost if avg_non_animation_boost > 0 else 1.0,
            'enhancement_application_rate': enhancement_applied_count / enhancement_total if enhancement_total > 0 else 0,
            'target_achieved': avg_animation_boost >= 3.0  # Meta de triplicar
        }
    
    def _generate_report(self):
        """Gera relatório detalhado"""
        report = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'Animation Boost Simple Test',
                'objective': 'Validar componentes de detecção e boost de animação'
            },
            'results': self.results,
            'analysis': self._generate_analysis()
        }
        
        # Salvar relatório
        filename = f"animation_boost_simple_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Imprimir resumo
        self._print_summary()
        
        print(f"\n📄 Relatório completo salvo em: {filename}")
    
    def _generate_analysis(self) -> Dict[str, Any]:
        """Gera análise dos resultados"""
        summary = self.results['summary']
        
        analysis = {
            'detection_performance': {
                'accuracy': summary['detection_accuracy'],
                'interpretation': self._interpret_detection_accuracy(summary['detection_accuracy'])
            },
            'boost_performance': {
                'effectiveness': summary['boost_effectiveness'],
                'animation_boost': summary['avg_animation_boost_ratio'],
                'target_achieved': summary['target_achieved'],
                'interpretation': self._interpret_boost_effectiveness(summary)
            },
            'enhancement_performance': {
                'application_rate': summary['enhancement_application_rate'],
                'interpretation': self._interpret_enhancement_rate(summary['enhancement_application_rate'])
            },
            'overall_assessment': self._generate_overall_assessment(summary)
        }
        
        return analysis
    
    def _interpret_detection_accuracy(self, accuracy: float) -> str:
        """Interpreta precisão de detecção"""
        if accuracy >= 0.9:
            return "🎉 EXCELENTE! Detecção muito precisa."
        elif accuracy >= 0.8:
            return "✅ BOM! Detecção confiável."
        elif accuracy >= 0.7:
            return "⚠️ MODERADO. Detecção aceitável mas pode melhorar."
        else:
            return "❌ CRÍTICO. Detecção precisa de ajustes."
    
    def _interpret_boost_effectiveness(self, summary: Dict) -> str:
        """Interpreta efetividade do boost"""
        effectiveness = summary['boost_effectiveness']
        target_achieved = summary['target_achieved']
        
        if target_achieved:
            return "🎉 EXCELENTE! Meta de triplicar score foi ALCANÇADA!"
        elif effectiveness >= 2.0:
            return "✅ BOM! Score dobrou, próximo da meta."
        elif effectiveness >= 1.5:
            return "⚠️ MODERADO. Melhoria detectada mas insuficiente."
        else:
            return "❌ CRÍTICO. Boost não está funcionando adequadamente."
    
    def _interpret_enhancement_rate(self, rate: float) -> str:
        """Interpreta taxa de aprimoramento"""
        if rate >= 0.8:
            return "🎉 EXCELENTE! Aprimoramento aplicado consistentemente."
        elif rate >= 0.6:
            return "✅ BOM! Aprimoramento funcionando bem."
        elif rate >= 0.4:
            return "⚠️ MODERADO. Aprimoramento parcial."
        else:
            return "❌ CRÍTICO. Aprimoramento raramente aplicado."
    
    def _generate_overall_assessment(self, summary: Dict) -> str:
        """Gera avaliação geral do sistema"""
        detection_ok = summary['detection_accuracy'] >= 0.8
        boost_ok = summary['boost_effectiveness'] >= 2.0
        enhancement_ok = summary['enhancement_application_rate'] >= 0.6
        
        if detection_ok and boost_ok and enhancement_ok:
            return "🔥 SISTEMA FUNCIONANDO EXCELENTEMENTE!"
        elif detection_ok and (boost_ok or enhancement_ok):
            return "✅ SISTEMA FUNCIONANDO BEM com pequenos ajustes necessários."
        elif detection_ok:
            return "⚠️ SISTEMA PARCIALMENTE FUNCIONAL - boost/enhancement precisam de ajustes."
        else:
            return "❌ SISTEMA PRECISA DE REVISÃO COMPLETA."
    
    def _print_summary(self):
        """Imprime resumo dos resultados"""
        summary = self.results['summary']
        
        print("\n" + "="*60)
        print("📊 RESUMO DOS RESULTADOS")
        print("="*60)
        
        print(f"\n🎯 OBJETIVO: Validar sistema de boost de animação")
        
        print(f"\n🔍 DETECÇÃO DE CONSULTAS:")
        print(f"   • Precisão: {summary['detection_accuracy']:.1%}")
        print(f"   • Acertos: {summary['detection_correct']}/{summary['detection_total']}")
        
        print(f"\n📈 BOOST DE SCORES:")
        print(f"   • Boost médio (animação): {summary['avg_animation_boost_ratio']:.2f}x")
        print(f"   • Boost médio (não-animação): {summary['avg_non_animation_boost_ratio']:.2f}x")
        print(f"   • Efetividade: {summary['boost_effectiveness']:.2f}x")
        print(f"   • Meta alcançada: {'✅ SIM' if summary['target_achieved'] else '❌ NÃO'}")
        
        print(f"\n✨ APRIMORAMENTO DE PROMPTS:")
        print(f"   • Taxa de aplicação: {summary['enhancement_application_rate']:.1%}")

def main():
    """Função principal"""
    test = AnimationBoostTest()
    test.run_comprehensive_test()

if __name__ == "__main__":
    main()