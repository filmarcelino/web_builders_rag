"""Seed Pack para Animações Web e Mobile

Este módulo contém fontes curadas para animações em aplicações web e mobile,
organizadas por categoria e com metadados completos para facilitar a busca
e implementação.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class AnimationSource:
    """Fonte de animação com metadados completos"""
    name: str
    url: str
    license: str
    category: str
    description: str
    use_cases: List[str]
    common_issues: List[str]
    installation: str
    examples: List[str]
    tags: List[str]
    last_updated: str
    bundle_size: str = "N/A"
    performance_notes: str = ""
    accessibility_notes: str = ""

class AnimationSeedPack:
    """Gerenciador do Seed Pack de Animações"""
    
    def __init__(self):
        self.sources = self._initialize_sources()
        self.categories = {
            "react_js": "React/JS Animations",
            "3d_webgl": "3D / WebGL", 
            "interactive_assets": "Assets Interativos",
            "micro_interactions": "Micro-interações / SVG / CSS",
            "accessibility": "Accessibility & Motion"
        }
    
    def _initialize_sources(self) -> List[AnimationSource]:
        """Inicializa todas as fontes de animação"""
        return [
            # React/JS Animations
            AnimationSource(
                name="Framer Motion",
                url="https://www.framer.com/motion/",
                license="MIT",
                category="react_js",
                description="Biblioteca de animações declarativas para React com suporte a gestures e layout animations",
                use_cases=[
                    "Animações de componentes React",
                    "Transitions entre páginas", 
                    "Gestures e drag interactions",
                    "Layout animations automáticas",
                    "Scroll-triggered animations"
                ],
                common_issues=[
                    "Performance degradada em listas grandes",
                    "Nuances com Server-Side Rendering (SSR)",
                    "Bundle size considerável (~50kb)",
                    "Conflitos com outras bibliotecas de animação"
                ],
                installation="npm install framer-motion",
                examples=[
                    "<motion.div animate={{x: 100}} />",
                    "<AnimatePresence><motion.div exit={{opacity: 0}} /></AnimatePresence>",
                    "const controls = useAnimation(); controls.start({scale: 1.2})"
                ],
                tags=["react", "animation", "gestures", "layout", "ui"],
                last_updated="2024-01-15",
                bundle_size="~50kb gzipped",
                performance_notes="Otimizar com layoutId para shared element transitions",
                accessibility_notes="Respeita prefers-reduced-motion automaticamente"
            ),
            
            AnimationSource(
                name="GSAP (GreenSock)",
                url="https://greensock.com/gsap/",
                license="Dual (GreenSock free, extras comerciais)",
                category="react_js",
                description="Biblioteca de animação de alta performance com timeline avançada",
                use_cases=[
                    "Animações complexas com timelines",
                    "Efeitos visuais avançados",
                    "Animações de alta performance",
                    "Morphing de SVG",
                    "Scroll-triggered animations (ScrollTrigger)"
                ],
                common_issues=[
                    "Bundle size grande para recursos completos",
                    "Curva de aprendizado íngreme",
                    "Licença comercial para alguns plugins",
                    "Conflitos com React strict mode"
                ],
                installation="npm install gsap",
                examples=[
                    "gsap.to('.box', {duration: 2, x: 100, rotation: 360})",
                    "const tl = gsap.timeline(); tl.to('.item1', {x: 100}).to('.item2', {y: 50})",
                    "gsap.registerPlugin(ScrollTrigger); gsap.to('.element', {scrollTrigger: '.trigger', x: 100})"
                ],
                tags=["animation", "timeline", "performance", "svg", "scroll"],
                last_updated="2024-01-10",
                bundle_size="~35kb core, ~100kb+ com plugins",
                performance_notes="Usa requestAnimationFrame e otimizações de GPU",
                accessibility_notes="Configurar manualmente prefers-reduced-motion"
            ),
            
            AnimationSource(
                name="React Spring",
                url="https://react-spring.dev/",
                license="MIT",
                category="react_js",
                description="Animações baseadas em física/springs para interfaces naturais",
                use_cases=[
                    "Animações com física natural",
                    "Micro-interações suaves",
                    "Animações de lista (useTransition)",
                    "Parallax effects",
                    "Drag and drop animations"
                ],
                common_issues=[
                    "Tuning de parâmetros de spring pode ser difícil",
                    "Performance em animações simultâneas",
                    "Documentação pode ser confusa",
                    "Debugging de animações complexas"
                ],
                installation="npm install @react-spring/web",
                examples=[
                    "const springs = useSpring({from: {opacity: 0}, to: {opacity: 1}})",
                    "const transitions = useTransition(items, {from: {opacity: 0}, enter: {opacity: 1}})",
                    "const [springs, api] = useSpring(() => ({x: 0})); api.start({x: 100})"
                ],
                tags=["react", "physics", "spring", "natural", "ui"],
                last_updated="2024-01-08",
                bundle_size="~25kb gzipped",
                performance_notes="Otimizar com config presets para performance",
                accessibility_notes="Suporte a prefers-reduced-motion via config"
            ),
            
            AnimationSource(
                name="Motion One",
                url="https://motion.dev/",
                license="MIT",
                category="react_js",
                description="API moderna sobre Web Animations, leve e fácil de usar",
                use_cases=[
                    "Animações simples e rápidas",
                    "Keyframe animations",
                    "Scroll-driven animations",
                    "Timeline sequences",
                    "CSS-in-JS animations"
                ],
                common_issues=[
                    "Cobertura menor que GSAP/Framer Motion",
                    "Menos recursos avançados",
                    "Comunidade menor",
                    "Limitações em browsers antigos"
                ],
                installation="npm install motion",
                examples=[
                    "animate('.box', {x: 100}, {duration: 1})",
                    "timeline([['#item1', {x: 100}], ['#item2', {y: 50}]])",
                    "scroll(animate('.element', {opacity: [0, 1]}))"
                ],
                tags=["animation", "web-animations", "lightweight", "modern"],
                last_updated="2024-01-12",
                bundle_size="~12kb gzipped",
                performance_notes="Usa Web Animations API nativa",
                accessibility_notes="Respeita prefers-reduced-motion por padrão"
            ),
            
            # 3D / WebGL
            AnimationSource(
                name="Three.js",
                url="https://threejs.org/",
                license="MIT",
                category="3d_webgl",
                description="Motor 3D/WebGL completo para web",
                use_cases=[
                    "Cenas 3D complexas",
                    "Visualizações de dados 3D",
                    "Jogos web",
                    "Product showcases 3D",
                    "Realidade virtual (WebXR)"
                ],
                common_issues=[
                    "Curva de aprendizado muito alta",
                    "Performance limitada em mobile",
                    "Bundle size grande",
                    "Complexidade de setup inicial",
                    "Debugging de shaders"
                ],
                installation="npm install three",
                examples=[
                    "const scene = new THREE.Scene(); const camera = new THREE.PerspectiveCamera()",
                    "const geometry = new THREE.BoxGeometry(); const material = new THREE.MeshBasicMaterial()",
                    "const mesh = new THREE.Mesh(geometry, material); scene.add(mesh)"
                ],
                tags=["3d", "webgl", "graphics", "visualization", "vr"],
                last_updated="2024-01-20",
                bundle_size="~600kb+ dependendo dos módulos",
                performance_notes="Otimizar geometrias, usar instancing, LOD",
                accessibility_notes="Fornecer alternativas para usuários com limitações visuais"
            ),
            
            AnimationSource(
                name="React Three Fiber (R3F)",
                url="https://docs.pmnd.rs/react-three-fiber",
                license="MIT",
                category="3d_webgl",
                description="Binding React para Three.js com componetização de cenas",
                use_cases=[
                    "Integração 3D em apps React",
                    "Componentes 3D reutilizáveis",
                    "Animações 3D declarativas",
                    "Interactive 3D UIs",
                    "3D data visualization"
                ],
                common_issues=[
                    "Integração complexa com UI/estado externo",
                    "Performance em re-renders",
                    "Debugging de componentes 3D",
                    "Sincronização com React lifecycle"
                ],
                installation="npm install @react-three/fiber three",
                examples=[
                    "<Canvas><mesh><boxGeometry /><meshStandardMaterial /></mesh></Canvas>",
                    "const meshRef = useRef(); useFrame(() => meshRef.current.rotation.x += 0.01)",
                    "<animated.mesh {...springs}><sphereGeometry /></animated.mesh>"
                ],
                tags=["react", "3d", "three.js", "declarative", "components"],
                last_updated="2024-01-18",
                bundle_size="~50kb + Three.js",
                performance_notes="Usar useFrame com cuidado, otimizar re-renders",
                accessibility_notes="Implementar controles de teclado para navegação 3D"
            ),
            
            AnimationSource(
                name="@react-three/drei",
                url="https://github.com/pmndrs/drei",
                license="MIT",
                category="3d_webgl",
                description="Helpers e primitives para React Three Fiber",
                use_cases=[
                    "OrbitControls para navegação 3D",
                    "Loaders para modelos 3D",
                    "Text 3D components",
                    "Environment e lighting helpers",
                    "Post-processing effects"
                ],
                common_issues=[
                    "Dependência total do R3F",
                    "Alguns helpers podem impactar performance",
                    "Documentação esparsa para alguns componentes",
                    "Versionamento acoplado ao R3F"
                ],
                installation="npm install @react-three/drei",
                examples=[
                    "<OrbitControls enablePan={false} />",
                    "<Text3D font='/fonts/helvetiker.json'>Hello World</Text3D>",
                    "<Environment preset='sunset' />"
                ],
                tags=["react", "three.js", "helpers", "controls", "effects"],
                last_updated="2024-01-15",
                bundle_size="~30kb + componentes usados",
                performance_notes="Importar apenas componentes necessários",
                accessibility_notes="OrbitControls suporta navegação por teclado"
            ),
            
            # Assets Interativos
            AnimationSource(
                name="Lottie",
                url="https://airbnb.io/lottie/#/",
                license="Apache-2.0",
                category="interactive_assets",
                description="Animações em JSON exportadas do After Effects",
                use_cases=[
                    "Animações complexas de designers",
                    "Loading animations",
                    "Micro-interactions elaboradas",
                    "Ilustrações animadas",
                    "Onboarding animations"
                ],
                common_issues=[
                    "Limitações de recursos complexos do AE",
                    "Performance com SVG muito complexo",
                    "Tamanho de arquivo pode ser grande",
                    "Debugging de animações quebradas",
                    "Compatibilidade entre versões AE/Lottie"
                ],
                installation="npm install lottie-web lottie-react",
                examples=[
                    "<Lottie animationData={animationData} loop={true} />",
                    "const lottie = Lottie.loadAnimation({container, animationData})",
                    "lottie.setSpeed(0.5); lottie.goToAndStop(30, true)"
                ],
                tags=["animation", "after-effects", "json", "svg", "interactive"],
                last_updated="2024-01-10",
                bundle_size="~150kb + animation files",
                performance_notes="Otimizar animações no AE, usar renderer canvas para performance",
                accessibility_notes="Fornecer controles de play/pause, respeitar prefers-reduced-motion"
            ),
            
            AnimationSource(
                name="Rive",
                url="https://rive.app/",
                license="Free tier (Runtime open source, editor SaaS)",
                category="interactive_assets",
                description="Animações vetoriais interativas com state machines",
                use_cases=[
                    "Animações interativas complexas",
                    "Character animations",
                    "Game UI animations",
                    "Interactive illustrations",
                    "State-driven animations"
                ],
                common_issues=[
                    "Lock-in no editor proprietário",
                    "Curva de aprendizado do editor",
                    "Runtime ainda em evolução",
                    "Limitações na versão gratuita",
                    "Debugging de state machines"
                ],
                installation="npm install @rive-app/react-canvas",
                examples=[
                    "<Rive src='animation.riv' stateMachines='State Machine 1' />",
                    "const rive = useRive({src: 'animation.riv', autoplay: true})",
                    "rive.setTextRunValue('textRun', 'New Text')"
                ],
                tags=["animation", "interactive", "state-machine", "vector", "game"],
                last_updated="2024-01-05",
                bundle_size="~200kb runtime + animation files",
                performance_notes="Usar canvas renderer para melhor performance",
                accessibility_notes="Implementar controles customizados para acessibilidade"
            ),
            
            # Micro-interações / SVG / CSS
            AnimationSource(
                name="Anime.js",
                url="https://animejs.com/",
                license="MIT",
                category="micro_interactions",
                description="Biblioteca leve para animações em SVG, DOM e CSS",
                use_cases=[
                    "Micro-interações simples",
                    "Animações de SVG",
                    "Hover effects",
                    "Loading animations",
                    "Morphing de paths SVG"
                ],
                common_issues=[
                    "Desenvolvimento menos ativo",
                    "Recursos limitados comparado a GSAP",
                    "Performance em animações complexas",
                    "Documentação pode estar desatualizada"
                ],
                installation="npm install animejs",
                examples=[
                    "anime({targets: '.element', translateX: 250, duration: 800})",
                    "anime({targets: 'path', d: [{value: 'M10 10L90 90'}, {value: 'M10 90L90 10'}]})",
                    "anime.timeline().add({targets: '.item1', opacity: 1}).add({targets: '.item2', scale: 1.2})"
                ],
                tags=["animation", "svg", "lightweight", "micro-interactions", "css"],
                last_updated="2023-12-15",
                bundle_size="~17kb gzipped",
                performance_notes="Otimizar seletores, evitar animações simultâneas excessivas",
                accessibility_notes="Implementar prefers-reduced-motion manualmente"
            ),
            
            AnimationSource(
                name="Micro-interactions Guidelines",
                url="https://material.io/design/interaction/micro-interactions.html",
                license="Creative Commons",
                category="micro_interactions",
                description="Diretrizes e patterns para micro-interações em UX",
                use_cases=[
                    "Design de hover states",
                    "Button feedback animations",
                    "Form validation feedback",
                    "Loading states",
                    "Navigation transitions"
                ],
                common_issues=[
                    "Over-animation prejudica UX",
                    "Inconsistência entre componentes",
                    "Ignorar contexto de acessibilidade",
                    "Performance em dispositivos lentos"
                ],
                installation="Referência de design - não requer instalação",
                examples=[
                    "Button: scale(0.95) on press, bounce back on release",
                    "Input focus: border-color transition + subtle glow",
                    "Card hover: translateY(-2px) + box-shadow increase"
                ],
                tags=["ux", "design", "patterns", "guidelines", "best-practices"],
                last_updated="2024-01-01",
                bundle_size="N/A",
                performance_notes="Usar transform e opacity para animações performáticas",
                accessibility_notes="Sempre considerar usuários com sensibilidade a movimento"
            ),
            
            AnimationSource(
                name="Accessibility & Motion",
                url="https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html",
                license="W3C",
                category="accessibility",
                description="Diretrizes de acessibilidade para animações e movimento",
                use_cases=[
                    "Implementação de prefers-reduced-motion",
                    "Animações acessíveis",
                    "Feedback visual inclusivo",
                    "Controles de animação",
                    "Alternativas para usuários com limitações"
                ],
                common_issues=[
                    "Ignorar preferências de movimento reduzido",
                    "Animações que causam vertigem",
                    "Falta de controles de pausa",
                    "Animações essenciais sem alternativas"
                ],
                installation="CSS: @media (prefers-reduced-motion: reduce)",
                examples=[
                    "@media (prefers-reduced-motion: reduce) { * { animation-duration: 0.01ms !important; } }",
                    "const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches",
                    "<button onClick={toggleAnimations}>Pausar Animações</button>"
                ],
                tags=["accessibility", "a11y", "reduced-motion", "inclusive", "wcag"],
                last_updated="2024-01-01",
                bundle_size="N/A",
                performance_notes="Animações reduzidas melhoram performance em dispositivos lentos",
                accessibility_notes="Essencial para usuários com vestibular disorders e epilepsia"
            )
        ]
    
    def get_sources_by_category(self, category: str) -> List[AnimationSource]:
        """Retorna fontes filtradas por categoria"""
        return [source for source in self.sources if source.category == category]
    
    def search_sources(self, query: str) -> List[AnimationSource]:
        """Busca fontes por termo"""
        query_lower = query.lower()
        results = []
        
        for source in self.sources:
            # Busca no nome, descrição, tags e casos de uso
            if (query_lower in source.name.lower() or 
                query_lower in source.description.lower() or
                any(query_lower in tag.lower() for tag in source.tags) or
                any(query_lower in use_case.lower() for use_case in source.use_cases)):
                results.append(source)
        
        return results
    
    def get_sources_by_tags(self, tags: List[str]) -> List[AnimationSource]:
        """Retorna fontes que contêm pelo menos uma das tags"""
        results = []
        tags_lower = [tag.lower() for tag in tags]
        
        for source in self.sources:
            if any(tag.lower() in tags_lower for tag in source.tags):
                results.append(source)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do seed pack"""
        category_counts = {}
        for source in self.sources:
            category_counts[source.category] = category_counts.get(source.category, 0) + 1
        
        return {
            "total_sources": len(self.sources),
            "categories": category_counts,
            "category_names": self.categories,
            "last_updated": datetime.now().isoformat(),
            "coverage": {
                "react_js": 4,
                "3d_webgl": 3, 
                "interactive_assets": 2,
                "micro_interactions": 2,
                "accessibility": 1
            }
        }
    
    def export_markdown_documentation(self) -> str:
        """Exporta documentação completa em Markdown"""
        md_content = ["# 🎬 Animation Seed Pack\n"]
        md_content.append("Fontes curadas para animações em aplicações web e mobile.\n")
        
        stats = self.get_statistics()
        md_content.append(f"**Total de fontes:** {stats['total_sources']}\n")
        
        for category_key, category_name in self.categories.items():
            sources = self.get_sources_by_category(category_key)
            if not sources:
                continue
                
            md_content.append(f"## {category_name}\n")
            
            for source in sources:
                md_content.append(f"### {source.name}\n")
                md_content.append(f"**URL:** {source.url}\n")
                md_content.append(f"**Licença:** {source.license}\n")
                md_content.append(f"**Instalação:** `{source.installation}`\n")
                md_content.append(f"**Bundle Size:** {source.bundle_size}\n\n")
                
                md_content.append(f"**Descrição:** {source.description}\n\n")
                
                md_content.append("**Casos de uso:**\n")
                for use_case in source.use_cases:
                    md_content.append(f"- {use_case}\n")
                md_content.append("\n")
                
                md_content.append("**Problemas comuns:**\n")
                for issue in source.common_issues:
                    md_content.append(f"- {issue}\n")
                md_content.append("\n")
                
                md_content.append("**Exemplos:**\n")
                for example in source.examples:
                    md_content.append(f"```javascript\n{example}\n```\n")
                md_content.append("\n")
                
                if source.performance_notes:
                    md_content.append(f"**Performance:** {source.performance_notes}\n\n")
                
                if source.accessibility_notes:
                    md_content.append(f"**Acessibilidade:** {source.accessibility_notes}\n\n")
                
                md_content.append(f"**Tags:** {', '.join(source.tags)}\n")
                md_content.append(f"**Última atualização:** {source.last_updated}\n\n")
                md_content.append("---\n\n")
        
        return "".join(md_content)

# Instância global do seed pack
animation_seed_pack = AnimationSeedPack()

# Funções de conveniência para importação
def get_react_animation_sources() -> List[AnimationSource]:
    """Retorna fontes de animação para React/JS"""
    return animation_seed_pack.get_sources_by_category("react_js")

def get_3d_sources() -> List[AnimationSource]:
    """Retorna fontes para 3D/WebGL"""
    return animation_seed_pack.get_sources_by_category("3d_webgl")

def get_interactive_asset_sources() -> List[AnimationSource]:
    """Retorna fontes para assets interativos"""
    return animation_seed_pack.get_sources_by_category("interactive_assets")

def get_micro_interaction_sources() -> List[AnimationSource]:
    """Retorna fontes para micro-interações"""
    return animation_seed_pack.get_sources_by_category("micro_interactions")

def get_accessibility_sources() -> List[AnimationSource]:
    """Retorna fontes sobre acessibilidade em animações"""
    return animation_seed_pack.get_sources_by_category("accessibility")

def search_animation_sources(query: str) -> List[AnimationSource]:
    """Busca fontes de animação por termo"""
    return animation_seed_pack.search_sources(query)

def get_sources_for_performance() -> List[AnimationSource]:
    """Retorna fontes otimizadas para performance"""
    return animation_seed_pack.get_sources_by_tags(["performance", "lightweight"])

def get_accessible_animation_sources() -> List[AnimationSource]:
    """Retorna fontes com foco em acessibilidade"""
    return animation_seed_pack.get_sources_by_tags(["accessibility", "a11y", "reduced-motion"])