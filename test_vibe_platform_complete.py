#!/usr/bin/env python3
"""
Teste Completo da Vibe Creation Platform

Script de demonstração que testa todo o workflow:
1. Coleta de conteúdo especializado
2. Integração de backends modernos
3. Sistema de edição visual
4. Hub de IA generativa
5. Plataforma unificada
6. IA sensível ao contexto
7. Preview perfeito

Workflow: Vibe → Design → Code → Deploy → Analytics
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import sys

# Importar todos os sistemas da plataforma
try:
    from vibe_content_collector import VibeContentCollector
    from modern_backend_integrator import ModernBackendIntegrator
    from visual_editor_system import VisualEditorSystem
    from ai_generation_hub import AIGenerationHub
    from vibe_creation_platform import VibeCreationPlatform
    from context_aware_ai_system import ContextAwareAISystem
    from perfect_preview_system import PerfectPreviewSystem
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Certifique-se de que todos os arquivos estão no mesmo diretório.")
    sys.exit(1)

class VibeCreationPlatformTester:
    """Testador completo da Vibe Creation Platform"""
    
    def __init__(self):
        self.project_dir = Path(".")
        self.test_results = []
        self.start_time = None
        
        # Sistemas da plataforma
        self.content_collector = None
        self.backend_integrator = None
        self.visual_editor = None
        self.ai_hub = None
        self.vibe_platform = None
        self.context_ai = None
        self.preview_system = None
    
    async def initialize_all_systems(self):
        """Inicializa todos os sistemas da plataforma"""
        print("🚀 Inicializando Vibe Creation Platform...\n")
        
        try:
            # 1. Content Collector
            print("📚 Inicializando Content Collector...")
            self.content_collector = VibeContentCollector()
            await self.content_collector.initialize()
            self._log_test("Content Collector", True, "Sistema inicializado")
            
            # 2. Backend Integrator
            print("🔧 Inicializando Backend Integrator...")
            self.backend_integrator = ModernBackendIntegrator()
            await self.backend_integrator.initialize()
            self._log_test("Backend Integrator", True, "Backends configurados")
            
            # 3. Visual Editor
            print("🎨 Inicializando Visual Editor...")
            self.visual_editor = VisualEditorSystem()
            await self.visual_editor.initialize()
            self._log_test("Visual Editor", True, "Editor visual pronto")
            
            # 4. AI Generation Hub
            print("🤖 Inicializando AI Generation Hub...")
            self.ai_hub = AIGenerationHub()
            await self.ai_hub.initialize()
            self._log_test("AI Generation Hub", True, "IA generativa configurada")
            
            # 5. Context-Aware AI
            print("🧠 Inicializando Context-Aware AI...")
            self.context_ai = ContextAwareAISystem()
            await self.context_ai.initialize()
            self._log_test("Context-Aware AI", True, "IA contextual ativa")
            
            # 6. Perfect Preview System
            print("📱 Inicializando Perfect Preview...")
            self.preview_system = PerfectPreviewSystem()
            await self.preview_system.initialize()
            self._log_test("Perfect Preview", True, "Preview system rodando")
            
            # 7. Vibe Creation Platform (Unificada)
            print("🌟 Inicializando Vibe Creation Platform...")
            self.vibe_platform = VibeCreationPlatform(
                project_dir="."
            )
            await self.vibe_platform.initialize_platform()
            self._log_test("Vibe Platform", True, "Plataforma unificada ativa")
            
            print("\n✅ Todos os sistemas inicializados com sucesso!\n")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            self._log_test("Inicialização", False, str(e))
            return False
    
    async def test_complete_workflow(self):
        """Testa o workflow completo da plataforma"""
        print("🎯 Iniciando teste do workflow completo...\n")
        
        # Dados do projeto de teste
        project_data = {
            'name': 'AI Startup Landing Page',
            'description': 'Modern landing page for innovative AI startup',
            'vibe_description': 'Cutting-edge, trustworthy, innovative, professional',
            'target_audience': 'tech entrepreneurs and investors',
            'brand_style': 'modern minimalist',
            'color_palette': ['#007bff', '#28a745', '#ffffff', '#f8f9fa'],
            'project_type': 'landing_page',
            'industry': 'artificial_intelligence'
        }
        
        user_id = 'test_user_001'
        
        try:
            # FASE 1: Criar projeto na plataforma
            print("📋 FASE 1: Criando projeto...")
            project = await self.vibe_platform.create_project(
                name=project_data['name'],
                description=project_data['description'],
                project_type=project_data['project_type'],
                user_id=user_id
            )
            print(f"   ✅ Projeto criado: {project.id}")
            self._log_test("Criar Projeto", True, f"ID: {project.id}")
            
            # FASE 2: Iniciar sessão de design
            print("\n🎨 FASE 2: Iniciando sessão de design...")
            design_session = await self.vibe_platform.start_design_session(
                project_id=project.id,
                user_id=user_id,
                vibe_description=project_data['vibe_description']
            )
            print(f"   ✅ Sessão iniciada: {design_session.id}")
            self._log_test("Sessão Design", True, f"ID: {design_session.id}")
            
            # FASE 3: Gerar conteúdo com IA
            print("\n🤖 FASE 3: Gerando conteúdo com IA...")
            
            # 3.1 Gerar imagem hero com DALL-E
            hero_image = await self.vibe_platform.generate_ai_content(
                project_id=project.id,
                content_type='image',
                prompt='Modern hero image for AI startup landing page',
                ai_provider='dalle3',
                style_context=project_data
            )
            print(f"   ✅ Imagem hero gerada: {hero_image.get('url', 'N/A')}")
            
            # 3.2 Gerar vídeo promocional com HeyGen
            promo_video = await self.vibe_platform.generate_ai_content(
                project_id=project.id,
                content_type='video',
                prompt='Professional AI startup introduction video',
                ai_provider='heygen',
                style_context=project_data
            )
            print(f"   ✅ Vídeo promocional gerado: {promo_video.get('url', 'N/A')}")
            
            # 3.3 Gerar copy com Leonardo AI
            marketing_copy = await self.vibe_platform.generate_ai_content(
                project_id=project.id,
                content_type='text',
                prompt='Compelling marketing copy for AI startup',
                ai_provider='leonardo',
                style_context=project_data
            )
            print(f"   ✅ Copy de marketing gerado: {len(marketing_copy.get('content', ''))} caracteres")
            
            self._log_test("Geração IA", True, "Hero, vídeo e copy gerados")
            
            # FASE 4: Edição visual e design
            print("\n🎨 FASE 4: Aplicando edição visual...")
            
            # Simular edição visual
            visual_changes = {
                'layout': 'hero_with_video',
                'components': [
                    {'type': 'hero_section', 'image': hero_image},
                    {'type': 'video_section', 'video': promo_video},
                    {'type': 'features_section', 'copy': marketing_copy}
                ],
                'theme': {
                    'colors': project_data['color_palette'],
                    'typography': 'Inter, sans-serif',
                    'spacing': 'comfortable'
                }
            }
            
            design_result = await self.visual_editor.apply_design_changes(
                project.id, visual_changes
            )
            print(f"   ✅ Design aplicado: {len(visual_changes['components'])} componentes")
            self._log_test("Edição Visual", True, "Layout e componentes aplicados")
            
            # FASE 5: Configurar backend e deploy
            print("\n🔧 FASE 5: Configurando backend e deploy...")
            
            # Configurar Supabase
            backend_config = await self.backend_integrator.setup_supabase_project(
                project_name=project_data['name'].lower().replace(' ', '-'),
                features=['auth', 'database', 'storage', 'realtime']
            )
            print(f"   ✅ Supabase configurado: {backend_config.get('project_url', 'N/A')}")
            
            # Deploy no Vercel
            deploy_result = await self.backend_integrator.deploy_to_vercel(
                project_path=str(self.project_dir),
                project_name=project_data['name'].lower().replace(' ', '-'),
                environment_vars={
                    'SUPABASE_URL': backend_config.get('project_url', ''),
                    'SUPABASE_ANON_KEY': backend_config.get('anon_key', '')
                }
            )
            print(f"   ✅ Deploy realizado: {deploy_result.get('url', 'N/A')}")
            self._log_test("Backend & Deploy", True, "Supabase + Vercel configurados")
            
            # FASE 6: Preview multi-device
            print("\n📱 FASE 6: Configurando preview multi-device...")
            
            preview_session = await self.preview_system.create_preview_session(
                project_id=project.id,
                user_id=user_id,
                device_ids=['desktop_1920', 'iphone_14_pro', 'ipad_pro', 'samsung_s23'],
                collaborative=True
            )
            print(f"   ✅ Preview configurado: {len(preview_session.devices)} dispositivos")
            print(f"   🌐 URL: http://localhost:3000/preview/{project.id}")
            self._log_test("Preview Multi-Device", True, f"{len(preview_session.devices)} dispositivos")
            
            # FASE 7: Analytics e Context-Aware AI
            print("\n📊 FASE 7: Coletando analytics e insights...")
            
            # Simular interações do usuário
            interactions = [
                {
                    'user_id': user_id,
                    'project_id': project.id,
                    'type': 'ai_generation',
                    'action': 'generate_hero_image',
                    'context': {'ai_type': 'dalle3', 'style': 'modern'},
                    'result': 'success',
                    'satisfaction': 0.9,
                    'duration': 45
                },
                {
                    'user_id': user_id,
                    'project_id': project.id,
                    'type': 'visual_editing',
                    'action': 'apply_layout',
                    'context': {'layout': 'hero_with_video'},
                    'result': 'success',
                    'satisfaction': 0.85,
                    'duration': 120
                },
                {
                    'user_id': user_id,
                    'project_id': project.id,
                    'type': 'preview',
                    'action': 'multi_device_test',
                    'context': {'devices': 4},
                    'result': 'success',
                    'satisfaction': 0.95,
                    'duration': 180
                }
            ]
            
            for interaction in interactions:
                await self.context_ai.learn_from_interaction(interaction)
            
            # Gerar recomendações contextuais
            recommendations = await self.context_ai.analyze_project_and_generate_recommendations(
                project_data, user_id
            )
            print(f"   ✅ Recomendações geradas: {len(recommendations)}")
            
            # Analytics da plataforma
            platform_analytics = await self.vibe_platform.get_analytics()
            print(f"   📈 Projetos totais: {platform_analytics.get('total_projects', 0)}")
            print(f"   👥 Usuários ativos: {platform_analytics.get('active_users', 0)}")
            
            self._log_test("Analytics & AI", True, f"{len(recommendations)} recomendações")
            
            # FASE 8: Teste de performance
            print("\n⚡ FASE 8: Testando performance...")
            
            session_analytics = await self.preview_system.get_session_analytics(preview_session.id)
            performance_data = session_analytics.get('performance', {})
            
            print(f"   📊 Tempo médio de carregamento: {performance_data.get('avg_load_time', 0):.3f}s")
            print(f"   📦 Tamanho médio do bundle: {performance_data.get('avg_bundle_size', 0)} bytes")
            print(f"   🎯 Dispositivos testados: {performance_data.get('devices_tested', 0)}")
            
            self._log_test("Performance", True, "Métricas coletadas")
            
            print("\n🎉 WORKFLOW COMPLETO EXECUTADO COM SUCESSO!")
            return True
            
        except Exception as e:
            print(f"❌ Erro no workflow: {e}")
            self._log_test("Workflow Completo", False, str(e))
            return False
    
    async def test_ai_integration(self):
        """Testa integração específica das IAs"""
        print("🤖 Testando integração das IAs generativas...\n")
        
        ai_tests = [
            {
                'name': 'DALL-E 3',
                'provider': 'dalle3',
                'type': 'image',
                'prompt': 'Modern tech startup office space'
            },
            {
                'name': 'Leonardo AI',
                'provider': 'leonardo',
                'type': 'image',
                'prompt': 'Professional business illustration'
            },
            {
                'name': 'Kling AI',
                'provider': 'kling',
                'type': 'video',
                'prompt': 'Product demonstration animation'
            },
            {
                'name': 'Veo 3',
                'provider': 'veo3',
                'type': 'video',
                'prompt': 'Corporate presentation intro'
            },
            {
                'name': 'HeyGen',
                'provider': 'heygen',
                'type': 'video',
                'prompt': 'AI avatar welcome message'
            }
        ]
        
        for test in ai_tests:
            try:
                print(f"   🎯 Testando {test['name']}...")
                
                result = await self.ai_hub.generate_content(
                    content_type=test['type'],
                    prompt=test['prompt'],
                    provider=test['provider']
                )
                
                success = result.get('status') == 'success'
                print(f"   {'✅' if success else '❌'} {test['name']}: {'OK' if success else 'ERRO'}")
                self._log_test(f"AI - {test['name']}", success, result.get('message', ''))
                
            except Exception as e:
                print(f"   ❌ {test['name']}: {e}")
                self._log_test(f"AI - {test['name']}", False, str(e))
    
    async def test_collaboration_features(self):
        """Testa recursos de colaboração"""
        print("👥 Testando recursos de colaboração...\n")
        
        try:
            # Criar sessão colaborativa
            project_id = 'test_collab_project'
            users = ['user_001', 'user_002', 'user_003']
            
            # Simular múltiplos usuários
            for user_id in users:
                session = await self.preview_system.create_preview_session(
                    project_id=project_id,
                    user_id=user_id,
                    collaborative=True
                )
                print(f"   👤 Usuário {user_id} entrou na sessão {session.id}")
            
            print(f"   ✅ Colaboração testada com {len(users)} usuários")
            self._log_test("Colaboração", True, f"{len(users)} usuários simultâneos")
            
        except Exception as e:
            print(f"   ❌ Erro na colaboração: {e}")
            self._log_test("Colaboração", False, str(e))
    
    def _log_test(self, test_name: str, success: bool, details: str = ""):
        """Registra resultado de teste"""
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def generate_test_report(self):
        """Gera relatório final dos testes"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        print("\n" + "="*60)
        print("📊 RELATÓRIO FINAL DOS TESTES")
        print("="*60)
        print(f"⏱️  Duração total: {duration:.2f}s")
        print(f"🎯 Testes executados: {total_tests}")
        print(f"✅ Testes bem-sucedidos: {successful_tests}")
        print(f"❌ Testes falharam: {total_tests - successful_tests}")
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        print("\n📋 DETALHES DOS TESTES:")
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}: {result['details']}")
        
        print("\n🎉 VIBE CREATION PLATFORM - STATUS:")
        if success_rate >= 90:
            print("   🚀 EXCELENTE! Plataforma pronta para produção")
        elif success_rate >= 75:
            print("   👍 BOM! Alguns ajustes necessários")
        elif success_rate >= 50:
            print("   ⚠️  REGULAR! Melhorias importantes necessárias")
        else:
            print("   🔧 CRÍTICO! Revisão completa necessária")
        
        print("\n" + "="*60)
        
        # Salvar relatório em arquivo
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': success_rate,
            'test_results': self.test_results
        }
        
        report_file = self.project_dir / 'vibe_platform_test_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Relatório salvo em: {report_file}")
    
    async def run_complete_test_suite(self):
        """Executa suite completa de testes"""
        self.start_time = time.time()
        
        print("🎯 INICIANDO TESTE COMPLETO DA VIBE CREATION PLATFORM")
        print("="*60)
        
        # 1. Inicializar sistemas
        if not await self.initialize_all_systems():
            print("❌ Falha na inicialização. Abortando testes.")
            return
        
        # 2. Teste do workflow completo
        await self.test_complete_workflow()
        
        # 3. Teste de integração das IAs
        await self.test_ai_integration()
        
        # 4. Teste de colaboração
        await self.test_collaboration_features()
        
        # 5. Gerar relatório final
        self.generate_test_report()

# Função principal
async def main():
    """Função principal de teste"""
    tester = VibeCreationPlatformTester()
    await tester.run_complete_test_suite()

if __name__ == "__main__":
    print("🚀 Vibe Creation Platform - Teste Completo")
    print("Testando todos os sistemas integrados...\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
    
    print("\n👋 Teste finalizado!")