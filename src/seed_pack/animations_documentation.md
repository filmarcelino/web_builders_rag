# 🎬 Animation Seed Pack

Fontes curadas para animações em aplicações web e mobile.

**Total de fontes:** 12

## React/JS Animations

### Framer Motion
**URL:** https://www.framer.com/motion/
**Licença:** MIT
**Instalação:** `npm install framer-motion`
**Bundle Size:** ~50kb gzipped

**Descrição:** Biblioteca de animações declarativas para React com suporte a gestures e layout animations

**Casos de uso:**
- Animações de componentes React
- Transitions entre páginas
- Gestures e drag interactions
- Layout animations automáticas
- Scroll-triggered animations

**Problemas comuns:**
- Performance degradada em listas grandes
- Nuances com Server-Side Rendering (SSR)
- Bundle size considerável (~50kb)
- Conflitos com outras bibliotecas de animação

**Exemplos:**
```javascript
<motion.div animate={{x: 100}} />
```
```javascript
<AnimatePresence><motion.div exit={{opacity: 0}} /></AnimatePresence>
```
```javascript
const controls = useAnimation(); controls.start({scale: 1.2})
```

**Performance:** Otimizar com layoutId para shared element transitions

**Acessibilidade:** Respeita prefers-reduced-motion automaticamente

**Tags:** react, animation, gestures, layout, ui
**Última atualização:** 2024-01-15

---

### GSAP (GreenSock)
**URL:** https://greensock.com/gsap/
**Licença:** Dual (GreenSock free, extras comerciais)
**Instalação:** `npm install gsap`
**Bundle Size:** ~35kb core, ~100kb+ com plugins

**Descrição:** Biblioteca de animação de alta performance com timeline avançada

**Casos de uso:**
- Animações complexas com timelines
- Efeitos visuais avançados
- Animações de alta performance
- Morphing de SVG
- Scroll-triggered animations (ScrollTrigger)

**Problemas comuns:**
- Bundle size grande para recursos completos
- Curva de aprendizado íngreme
- Licença comercial para alguns plugins
- Conflitos com React strict mode

**Exemplos:**
```javascript
gsap.to('.box', {duration: 2, x: 100, rotation: 360})
```
```javascript
const tl = gsap.timeline(); tl.to('.item1', {x: 100}).to('.item2', {y: 50})
```
```javascript
gsap.registerPlugin(ScrollTrigger); gsap.to('.element', {scrollTrigger: '.trigger', x: 100})
```

**Performance:** Usa requestAnimationFrame e otimizações de GPU

**Acessibilidade:** Configurar manualmente prefers-reduced-motion

**Tags:** animation, timeline, performance, svg, scroll
**Última atualização:** 2024-01-10

---

### React Spring
**URL:** https://react-spring.dev/
**Licença:** MIT
**Instalação:** `npm install @react-spring/web`
**Bundle Size:** ~25kb gzipped

**Descrição:** Animações baseadas em física/springs para interfaces naturais

**Casos de uso:**
- Animações com física natural
- Micro-interações suaves
- Animações de lista (useTransition)
- Parallax effects
- Drag and drop animations

**Problemas comuns:**
- Tuning de parâmetros de spring pode ser difícil
- Performance em animações simultâneas
- Documentação pode ser confusa
- Debugging de animações complexas

**Exemplos:**
```javascript
const springs = useSpring({from: {opacity: 0}, to: {opacity: 1}})
```
```javascript
const transitions = useTransition(items, {from: {opacity: 0}, enter: {opacity: 1}})
```
```javascript
const [springs, api] = useSpring(() => ({x: 0})); api.start({x: 100})
```

**Performance:** Otimizar com config presets para performance

**Acessibilidade:** Suporte a prefers-reduced-motion via config

**Tags:** react, physics, spring, natural, ui
**Última atualização:** 2024-01-08

---

### Motion One
**URL:** https://motion.dev/
**Licença:** MIT
**Instalação:** `npm install motion`
**Bundle Size:** ~12kb gzipped

**Descrição:** API moderna sobre Web Animations, leve e fácil de usar

**Casos de uso:**
- Animações simples e rápidas
- Keyframe animations
- Scroll-driven animations
- Timeline sequences
- CSS-in-JS animations

**Problemas comuns:**
- Cobertura menor que GSAP/Framer Motion
- Menos recursos avançados
- Comunidade menor
- Limitações em browsers antigos

**Exemplos:**
```javascript
animate('.box', {x: 100}, {duration: 1})
```
```javascript
timeline([['#item1', {x: 100}], ['#item2', {y: 50}]])
```
```javascript
scroll(animate('.element', {opacity: [0, 1]}))
```

**Performance:** Usa Web Animations API nativa

**Acessibilidade:** Respeita prefers-reduced-motion por padrão

**Tags:** animation, web-animations, lightweight, modern
**Última atualização:** 2024-01-12

---

## 3D / WebGL

### Three.js
**URL:** https://threejs.org/
**Licença:** MIT
**Instalação:** `npm install three`
**Bundle Size:** ~600kb+ dependendo dos módulos

**Descrição:** Motor 3D/WebGL completo para web

**Casos de uso:**
- Cenas 3D complexas
- Visualizações de dados 3D
- Jogos web
- Product showcases 3D
- Realidade virtual (WebXR)

**Problemas comuns:**
- Curva de aprendizado muito alta
- Performance limitada em mobile
- Bundle size grande
- Complexidade de setup inicial
- Debugging de shaders

**Exemplos:**
```javascript
const scene = new THREE.Scene(); const camera = new THREE.PerspectiveCamera()
```
```javascript
const geometry = new THREE.BoxGeometry(); const material = new THREE.MeshBasicMaterial()
```
```javascript
const mesh = new THREE.Mesh(geometry, material); scene.add(mesh)
```

**Performance:** Otimizar geometrias, usar instancing, LOD

**Acessibilidade:** Fornecer alternativas para usuários com limitações visuais

**Tags:** 3d, webgl, graphics, visualization, vr
**Última atualização:** 2024-01-20

---

### React Three Fiber (R3F)
**URL:** https://docs.pmnd.rs/react-three-fiber
**Licença:** MIT
**Instalação:** `npm install @react-three/fiber three`
**Bundle Size:** ~50kb + Three.js

**Descrição:** Binding React para Three.js com componetização de cenas

**Casos de uso:**
- Integração 3D em apps React
- Componentes 3D reutilizáveis
- Animações 3D declarativas
- Interactive 3D UIs
- 3D data visualization

**Problemas comuns:**
- Integração complexa com UI/estado externo
- Performance em re-renders
- Debugging de componentes 3D
- Sincronização com React lifecycle

**Exemplos:**
```javascript
<Canvas><mesh><boxGeometry /><meshStandardMaterial /></mesh></Canvas>
```
```javascript
const meshRef = useRef(); useFrame(() => meshRef.current.rotation.x += 0.01)
```
```javascript
<animated.mesh {...springs}><sphereGeometry /></animated.mesh>
```

**Performance:** Usar useFrame com cuidado, otimizar re-renders

**Acessibilidade:** Implementar controles de teclado para navegação 3D

**Tags:** react, 3d, three.js, declarative, components
**Última atualização:** 2024-01-18

---

### @react-three/drei
**URL:** https://github.com/pmndrs/drei
**Licença:** MIT
**Instalação:** `npm install @react-three/drei`
**Bundle Size:** ~30kb + componentes usados

**Descrição:** Helpers e primitives para React Three Fiber

**Casos de uso:**
- OrbitControls para navegação 3D
- Loaders para modelos 3D
- Text 3D components
- Environment e lighting helpers
- Post-processing effects

**Problemas comuns:**
- Dependência total do R3F
- Alguns helpers podem impactar performance
- Documentação esparsa para alguns componentes
- Versionamento acoplado ao R3F

**Exemplos:**
```javascript
<OrbitControls enablePan={false} />
```
```javascript
<Text3D font='/fonts/helvetiker.json'>Hello World</Text3D>
```
```javascript
<Environment preset='sunset' />
```

**Performance:** Importar apenas componentes necessários

**Acessibilidade:** OrbitControls suporta navegação por teclado

**Tags:** react, three.js, helpers, controls, effects
**Última atualização:** 2024-01-15

---

## Assets Interativos

### Lottie
**URL:** https://airbnb.io/lottie/#/
**Licença:** Apache-2.0
**Instalação:** `npm install lottie-web lottie-react`
**Bundle Size:** ~150kb + animation files

**Descrição:** Animações em JSON exportadas do After Effects

**Casos de uso:**
- Animações complexas de designers
- Loading animations
- Micro-interactions elaboradas
- Ilustrações animadas
- Onboarding animations

**Problemas comuns:**
- Limitações de recursos complexos do AE
- Performance com SVG muito complexo
- Tamanho de arquivo pode ser grande
- Debugging de animações quebradas
- Compatibilidade entre versões AE/Lottie

**Exemplos:**
```javascript
<Lottie animationData={animationData} loop={true} />
```
```javascript
const lottie = Lottie.loadAnimation({container, animationData})
```
```javascript
lottie.setSpeed(0.5); lottie.goToAndStop(30, true)
```

**Performance:** Otimizar animações no AE, usar renderer canvas para performance

**Acessibilidade:** Fornecer controles de play/pause, respeitar prefers-reduced-motion

**Tags:** animation, after-effects, json, svg, interactive
**Última atualização:** 2024-01-10

---

### Rive
**URL:** https://rive.app/
**Licença:** Free tier (Runtime open source, editor SaaS)
**Instalação:** `npm install @rive-app/react-canvas`
**Bundle Size:** ~200kb runtime + animation files

**Descrição:** Animações vetoriais interativas com state machines

**Casos de uso:**
- Animações interativas complexas
- Character animations
- Game UI animations
- Interactive illustrations
- State-driven animations

**Problemas comuns:**
- Lock-in no editor proprietário
- Curva de aprendizado do editor
- Runtime ainda em evolução
- Limitações na versão gratuita
- Debugging de state machines

**Exemplos:**
```javascript
<Rive src='animation.riv' stateMachines='State Machine 1' />
```
```javascript
const rive = useRive({src: 'animation.riv', autoplay: true})
```
```javascript
rive.setTextRunValue('textRun', 'New Text')
```

**Performance:** Usar canvas renderer para melhor performance

**Acessibilidade:** Implementar controles customizados para acessibilidade

**Tags:** animation, interactive, state-machine, vector, game
**Última atualização:** 2024-01-05

---

## Micro-interações / SVG / CSS

### Anime.js
**URL:** https://animejs.com/
**Licença:** MIT
**Instalação:** `npm install animejs`
**Bundle Size:** ~17kb gzipped

**Descrição:** Biblioteca leve para animações em SVG, DOM e CSS

**Casos de uso:**
- Micro-interações simples
- Animações de SVG
- Hover effects
- Loading animations
- Morphing de paths SVG

**Problemas comuns:**
- Desenvolvimento menos ativo
- Recursos limitados comparado a GSAP
- Performance em animações complexas
- Documentação pode estar desatualizada

**Exemplos:**
```javascript
anime({targets: '.element', translateX: 250, duration: 800})
```
```javascript
anime({targets: 'path', d: [{value: 'M10 10L90 90'}, {value: 'M10 90L90 10'}]})
```
```javascript
anime.timeline().add({targets: '.item1', opacity: 1}).add({targets: '.item2', scale: 1.2})
```

**Performance:** Otimizar seletores, evitar animações simultâneas excessivas

**Acessibilidade:** Implementar prefers-reduced-motion manualmente

**Tags:** animation, svg, lightweight, micro-interactions, css
**Última atualização:** 2023-12-15

---

### Micro-interactions Guidelines
**URL:** https://material.io/design/interaction/micro-interactions.html
**Licença:** Creative Commons
**Instalação:** `Referência de design - não requer instalação`
**Bundle Size:** N/A

**Descrição:** Diretrizes e patterns para micro-interações em UX

**Casos de uso:**
- Design de hover states
- Button feedback animations
- Form validation feedback
- Loading states
- Navigation transitions

**Problemas comuns:**
- Over-animation prejudica UX
- Inconsistência entre componentes
- Ignorar contexto de acessibilidade
- Performance em dispositivos lentos

**Exemplos:**
```javascript
Button: scale(0.95) on press, bounce back on release
```
```javascript
Input focus: border-color transition + subtle glow
```
```javascript
Card hover: translateY(-2px) + box-shadow increase
```

**Performance:** Usar transform e opacity para animações performáticas

**Acessibilidade:** Sempre considerar usuários com sensibilidade a movimento

**Tags:** ux, design, patterns, guidelines, best-practices
**Última atualização:** 2024-01-01

---

## Accessibility & Motion

### Accessibility & Motion
**URL:** https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html
**Licença:** W3C
**Instalação:** `CSS: @media (prefers-reduced-motion: reduce)`
**Bundle Size:** N/A

**Descrição:** Diretrizes de acessibilidade para animações e movimento

**Casos de uso:**
- Implementação de prefers-reduced-motion
- Animações acessíveis
- Feedback visual inclusivo
- Controles de animação
- Alternativas para usuários com limitações

**Problemas comuns:**
- Ignorar preferências de movimento reduzido
- Animações que causam vertigem
- Falta de controles de pausa
- Animações essenciais sem alternativas

**Exemplos:**
```javascript
@media (prefers-reduced-motion: reduce) { * { animation-duration: 0.01ms !important; } }
```
```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
```
```javascript
<button onClick={toggleAnimations}>Pausar Animações</button>
```

**Performance:** Animações reduzidas melhoram performance em dispositivos lentos

**Acessibilidade:** Essencial para usuários com vestibular disorders e epilepsia

**Tags:** accessibility, a11y, reduced-motion, inclusive, wcag
**Última atualização:** 2024-01-01

---

## 📊 Estatísticas do Seed Pack

- **Total de fontes:** 12
- **Categorias:**
  - React/JS Animations: 4 fontes
  - 3D/WebGL: 3 fontes
  - Assets Interativos: 2 fontes
  - Micro-interações/SVG/CSS: 2 fontes
  - Accessibility & Motion: 1 fonte

## 🎯 Destaques por Uso

### Para Performance
- **Motion One** (~12kb) - Mais leve
- **Anime.js** (~17kb) - Leve para micro-interações
- **React Spring** (~25kb) - Física natural

### Para Projetos React
- **Framer Motion** - Mais completo
- **React Spring** - Física natural
- **React Three Fiber** - 3D integrado

### Para Acessibilidade
- **Framer Motion** - prefers-reduced-motion automático
- **Motion One** - prefers-reduced-motion por padrão
- **Accessibility Guidelines** - Diretrizes W3C

### Para Projetos Complexos
- **GSAP** - Timeline avançada
- **Three.js** - 3D completo
- **Lottie** - Animações de designer

## 🔧 Configuração Recomendada

```css
/* CSS base para acessibilidade */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

```javascript
// JavaScript para detectar preferência
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

// Configurar bibliotecas baseado na preferência
if (prefersReducedMotion) {
  // Desabilitar ou reduzir animações
}
```

## 🚀 Próximos Passos

1. **Integração com RAG**: Indexar todas as fontes no sistema de busca
2. **Exemplos Práticos**: Criar demos interativos para cada biblioteca
3. **Performance Benchmarks**: Comparar performance entre bibliotecas
4. **Accessibility Testing**: Validar implementações com usuários reais
5. **Mobile Optimization**: Guias específicos para dispositivos móveis

---

*Última atualização: Janeiro 2024*
*Seed Pack mantido pela equipe de desenvolvimento*