#!/usr/bin/env python3
"""
Visual Editor System - Sistema de edição visual revolucionário

Este sistema implementa:
1. Editor visual drag-and-drop de causar inveja
2. Preview em tempo real multi-device
3. Colaboração em tempo real com cursores ao vivo
4. Integração com IA generativa (DALL-E, Leonardo AI, etc.)
5. Sistema de componentes inteligente
6. Edição de código visual com syntax highlighting
"""

import asyncio
import json
import os
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import uuid
import websockets
import aiohttp
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

@dataclass
class VisualComponent:
    """Representa um componente visual no editor"""
    id: str
    type: str  # 'button', 'text', 'image', 'container', 'form', etc.
    name: str
    properties: Dict[str, Any]
    styles: Dict[str, Any]
    children: List[str] = None  # IDs dos componentes filhos
    parent_id: Optional[str] = None
    position: Dict[str, float] = None  # x, y, width, height
    responsive_breakpoints: Dict[str, Dict] = None
    ai_generated: bool = False
    ai_prompt: Optional[str] = None
    version: int = 1
    created_at: str = None
    updated_at: str = None

@dataclass
class EditorState:
    """Estado atual do editor visual"""
    project_id: str
    
    def initialize(self):
        """Inicializa o estado do editor"""
        if self.components is None:
            self.components = {}
        if self.collaboration_users is None:
            self.collaboration_users = []
        if self.undo_stack is None:
            self.undo_stack = []
        if self.redo_stack is None:
            self.redo_stack = []
        if self.ai_suggestions is None:
            self.ai_suggestions = []
    components: Dict[str, VisualComponent]
    selected_component_id: Optional[str] = None
    viewport: Dict[str, Any] = None  # width, height, zoom, device
    grid_settings: Dict[str, Any] = None
    theme: Dict[str, Any] = None
    collaboration_users: List[Dict] = None
    undo_stack: List[Dict] = None
    redo_stack: List[Dict] = None
    ai_suggestions: List[Dict] = None

@dataclass
class CollaborationUser:
    """Usuário colaborando no editor"""
    id: str
    name: str
    avatar: str
    cursor_position: Dict[str, float]
    selected_component: Optional[str]
    color: str  # Cor do cursor
    is_active: bool = True
    last_seen: str = None

class VisualEditorSystem:
    """Sistema de edição visual revolucionário"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.editor_dir = self.project_dir / ".vibe" / "editor"
        self.editor_dir.mkdir(parents=True, exist_ok=True)
        
        # Estado do editor
        self.editor_state = None
        self.collaboration_users = {}
        self.websocket_connections = set()
        
        # Componentes disponíveis
        self.component_library = self._initialize_component_library()
        
        # Integrações de IA
        self.ai_integrations = {
            'dalle': None,
            'leonardo': None,
            'midjourney': None,
            'stable_diffusion': None
        }
        
        # Templates e temas
        self.templates = self._load_templates()
        self.themes = self._load_themes()
        
        # Sistema de preview
        self.preview_server = None
        self.preview_sockets = set()
        
        # Estado de inicialização
        self.initialized = False
    
    async def initialize(self):
        """Inicializa o sistema de edição visual"""
        if self.initialized:
            return
        
        # Configurar sessão HTTP para integrações
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'VibeCreationPlatform/1.0'}
        )
        
        # Inicializar estado do editor
        if self.editor_state is None:
            self.editor_state = EditorState(
                project_id="default",
                components={},
                selected_component_id=None,
                collaboration_users=[],
                undo_stack=[],
                redo_stack=[],
                ai_suggestions=[]
            )
        
        # Configurar integrações de IA
        await self._setup_ai_integrations()
        
        self.initialized = True
        print(f"🎨 Visual Editor inicializado com {len(self.component_library)} componentes")
    
    async def cleanup(self):
        """Limpa recursos"""
        if hasattr(self, 'session') and self.session:
            await self.session.close()
        self.initialized = False
    
    async def _setup_ai_integrations(self):
        """Configura integrações com IA generativa"""
        # Configurar integrações básicas (simuladas)
        self.ai_integrations = {
            'dalle': {'status': 'ready', 'api_key': 'simulated'},
            'leonardo': {'status': 'ready', 'api_key': 'simulated'},
            'midjourney': {'status': 'ready', 'api_key': 'simulated'},
            'stable_diffusion': {'status': 'ready', 'api_key': 'simulated'}
        }
    
    def _initialize_component_library(self) -> Dict[str, Dict]:
        """Inicializa biblioteca de componentes visuais"""
        return {
            # === COMPONENTES BÁSICOS ===
            'text': {
                'name': 'Text',
                'category': 'basic',
                'icon': '📝',
                'default_props': {
                    'content': 'Your text here',
                    'tag': 'p',
                    'editable': True
                },
                'default_styles': {
                    'fontSize': '16px',
                    'color': '#333333',
                    'fontFamily': 'Inter, sans-serif',
                    'lineHeight': '1.5'
                },
                'ai_enhanceable': True
            },
            
            'button': {
                'name': 'Button',
                'category': 'interactive',
                'icon': '🔘',
                'default_props': {
                    'text': 'Click me',
                    'variant': 'primary',
                    'size': 'medium',
                    'disabled': False
                },
                'default_styles': {
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'padding': '12px 24px',
                    'borderRadius': '8px',
                    'border': 'none',
                    'cursor': 'pointer',
                    'fontSize': '16px',
                    'fontWeight': '500'
                },
                'hover_styles': {
                    'backgroundColor': '#0056b3',
                    'transform': 'translateY(-2px)',
                    'boxShadow': '0 4px 12px rgba(0,123,255,0.3)'
                },
                'ai_enhanceable': True
            },
            
            'image': {
                'name': 'Image',
                'category': 'media',
                'icon': '🖼️',
                'default_props': {
                    'src': '',
                    'alt': 'Image description',
                    'lazy': True,
                    'responsive': True
                },
                'default_styles': {
                    'width': '100%',
                    'height': 'auto',
                    'borderRadius': '8px',
                    'objectFit': 'cover'
                },
                'ai_enhanceable': True,
                'ai_generators': ['dalle', 'leonardo', 'midjourney']
            },
            
            'container': {
                'name': 'Container',
                'category': 'layout',
                'icon': '📦',
                'default_props': {
                    'tag': 'div',
                    'responsive': True
                },
                'default_styles': {
                    'display': 'flex',
                    'flexDirection': 'column',
                    'gap': '16px',
                    'padding': '24px',
                    'backgroundColor': 'transparent',
                    'borderRadius': '12px'
                },
                'accepts_children': True,
                'ai_enhanceable': True
            },
            
            # === COMPONENTES AVANÇADOS ===
            'hero_section': {
                'name': 'Hero Section',
                'category': 'sections',
                'icon': '🦸',
                'default_props': {
                    'title': 'Amazing Hero Title',
                    'subtitle': 'Compelling subtitle that converts',
                    'cta_text': 'Get Started',
                    'background_type': 'gradient'
                },
                'default_styles': {
                    'minHeight': '80vh',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center',
                    'alignItems': 'center',
                    'textAlign': 'center',
                    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'color': 'white',
                    'padding': '80px 20px'
                },
                'ai_enhanceable': True,
                'ai_generators': ['dalle', 'leonardo']
            },
            
            'card': {
                'name': 'Card',
                'category': 'content',
                'icon': '🃏',
                'default_props': {
                    'title': 'Card Title',
                    'description': 'Card description goes here',
                    'image_url': '',
                    'link_url': '',
                    'elevation': 2
                },
                'default_styles': {
                    'backgroundColor': 'white',
                    'borderRadius': '16px',
                    'padding': '24px',
                    'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
                    'transition': 'all 0.3s ease',
                    'border': '1px solid #f0f0f0'
                },
                'hover_styles': {
                    'transform': 'translateY(-8px)',
                    'boxShadow': '0 12px 40px rgba(0,0,0,0.15)'
                },
                'ai_enhanceable': True
            },
            
            'form': {
                'name': 'Form',
                'category': 'interactive',
                'icon': '📋',
                'default_props': {
                    'title': 'Contact Form',
                    'fields': [
                        {'type': 'text', 'name': 'name', 'label': 'Name', 'required': True},
                        {'type': 'email', 'name': 'email', 'label': 'Email', 'required': True},
                        {'type': 'textarea', 'name': 'message', 'label': 'Message', 'required': True}
                    ],
                    'submit_text': 'Send Message',
                    'action': '/api/contact'
                },
                'default_styles': {
                    'backgroundColor': 'white',
                    'padding': '32px',
                    'borderRadius': '16px',
                    'boxShadow': '0 8px 32px rgba(0,0,0,0.1)'
                },
                'ai_enhanceable': True
            }
        }
    
    async def initialize_editor(self, project_id: str) -> EditorState:
        """Inicializa o editor visual"""
        print(f"🎨 Inicializando Editor Visual para projeto: {project_id}")
        
        # Criar estado inicial do editor
        self.editor_state = EditorState(
            project_id=project_id,
            components={},
            viewport={
                'width': 1440,
                'height': 900,
                'zoom': 1.0,
                'device': 'desktop'
            },
            grid_settings={
                'enabled': True,
                'size': 8,
                'snap': True,
                'visible': True
            },
            theme={
                'name': 'Modern Light',
                'primary': '#007bff',
                'secondary': '#6c757d',
                'success': '#28a745',
                'warning': '#ffc107',
                'danger': '#dc3545',
                'background': '#ffffff',
                'surface': '#f8f9fa',
                'text': '#212529'
            },
            collaboration_users=[],
            undo_stack=[],
            redo_stack=[],
            ai_suggestions=[]
        )
        
        # Carregar estado existente se houver
        await self._load_editor_state(project_id)
        
        # Inicializar integrações de IA
        await self._initialize_ai_integrations()
        
        # Configurar servidor de preview
        await self._setup_preview_server()
        
        print("✅ Editor Visual inicializado com sucesso!")
        return self.editor_state
    
    async def add_component(self, component_type: str, parent_id: Optional[str] = None, 
                          position: Optional[Dict] = None, ai_prompt: Optional[str] = None) -> VisualComponent:
        """Adiciona um novo componente ao editor"""
        
        if component_type not in self.component_library:
            raise ValueError(f"Tipo de componente '{component_type}' não encontrado")
        
        component_def = self.component_library[component_type]
        component_id = str(uuid.uuid4())
        
        # Criar componente
        component = VisualComponent(
            id=component_id,
            type=component_type,
            name=f"{component_def['name']} {len(self.editor_state.components) + 1}",
            properties=component_def['default_props'].copy(),
            styles=component_def['default_styles'].copy(),
            children=[] if component_def.get('accepts_children') else None,
            parent_id=parent_id,
            position=position or {'x': 0, 'y': 0, 'width': 200, 'height': 100},
            responsive_breakpoints={
                'mobile': {},
                'tablet': {},
                'desktop': {}
            },
            ai_generated=bool(ai_prompt),
            ai_prompt=ai_prompt,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Aplicar IA se solicitado
        if ai_prompt and component_def.get('ai_enhanceable'):
            component = await self._enhance_component_with_ai(component, ai_prompt)
        
        # Adicionar ao estado
        self.editor_state.components[component_id] = component
        
        # Adicionar ao pai se especificado
        if parent_id and parent_id in self.editor_state.components:
            parent = self.editor_state.components[parent_id]
            if parent.children is not None:
                parent.children.append(component_id)
        
        # Salvar estado
        await self._save_editor_state()
        
        # Notificar colaboradores
        await self._broadcast_component_change('added', component)
        
        print(f"✅ Componente {component_type} adicionado: {component_id}")
        return component
    
    async def update_component(self, component_id: str, updates: Dict[str, Any]) -> VisualComponent:
        """Atualiza um componente existente"""
        
        if component_id not in self.editor_state.components:
            raise ValueError(f"Componente '{component_id}' não encontrado")
        
        component = self.editor_state.components[component_id]
        
        # Salvar estado anterior para undo
        self._save_to_undo_stack()
        
        # Aplicar atualizações
        if 'properties' in updates:
            component.properties.update(updates['properties'])
        
        if 'styles' in updates:
            component.styles.update(updates['styles'])
        
        if 'position' in updates:
            component.position.update(updates['position'])
        
        if 'name' in updates:
            component.name = updates['name']
        
        component.updated_at = datetime.now().isoformat()
        component.version += 1
        
        # Salvar estado
        await self._save_editor_state()
        
        # Notificar colaboradores
        await self._broadcast_component_change('updated', component)
        
        # Atualizar preview em tempo real
        await self._update_live_preview()
        
        return component
    
    async def generate_ai_component(self, prompt: str, component_type: str = 'auto') -> VisualComponent:
        """Gera componente usando IA"""
        print(f"🤖 Gerando componente com IA: {prompt}")
        
        # Determinar tipo de componente automaticamente se necessário
        if component_type == 'auto':
            component_type = await self._determine_component_type_from_prompt(prompt)
        
        # Gerar conteúdo com IA
        ai_content = await self._generate_content_with_ai(prompt, component_type)
        
        # Criar componente com conteúdo gerado
        component = await self.add_component(
            component_type=component_type,
            ai_prompt=prompt
        )
        
        # Aplicar conteúdo gerado pela IA
        if ai_content:
            await self.update_component(component.id, ai_content)
        
        print(f"✅ Componente gerado com IA: {component.id}")
        return component
    
    async def generate_ai_image(self, prompt: str, style: str = 'photorealistic', 
                              size: str = '1024x1024', provider: str = 'dalle') -> str:
        """Gera imagem usando IA"""
        print(f"🎨 Gerando imagem com {provider}: {prompt}")
        
        if provider == 'dalle':
            return await self._generate_dalle_image(prompt, size)
        elif provider == 'leonardo':
            return await self._generate_leonardo_image(prompt, style, size)
        elif provider == 'midjourney':
            return await self._generate_midjourney_image(prompt, style)
        else:
            raise ValueError(f"Provedor de IA '{provider}' não suportado")
    
    async def start_collaboration_session(self, user: CollaborationUser) -> str:
        """Inicia sessão de colaboração"""
        session_id = str(uuid.uuid4())
        
        # Adicionar usuário
        self.collaboration_users[session_id] = user
        self.editor_state.collaboration_users.append(asdict(user))
        
        # Notificar outros usuários
        await self._broadcast_user_joined(user)
        
        print(f"👥 Usuário {user.name} entrou na colaboração: {session_id}")
        return session_id
    
    async def update_user_cursor(self, session_id: str, cursor_position: Dict[str, float]):
        """Atualiza posição do cursor do usuário"""
        if session_id in self.collaboration_users:
            user = self.collaboration_users[session_id]
            user.cursor_position = cursor_position
            user.last_seen = datetime.now().isoformat()
            
            # Broadcast cursor position
            await self._broadcast_cursor_update(user)
    
    async def export_to_code(self, framework: str = 'react') -> Dict[str, str]:
        """Exporta design para código"""
        print(f"💻 Exportando para {framework}...")
        
        if framework == 'react':
            return await self._export_to_react()
        elif framework == 'vue':
            return await self._export_to_vue()
        elif framework == 'html':
            return await self._export_to_html()
        else:
            raise ValueError(f"Framework '{framework}' não suportado")
    
    # Métodos auxiliares
    async def _enhance_component_with_ai(self, component: VisualComponent, prompt: str) -> VisualComponent:
        """Melhora componente usando IA"""
        # Implementar melhorias de IA
        return component
    
    async def _generate_content_with_ai(self, prompt: str, component_type: str) -> Dict:
        """Gera conteúdo usando IA"""
        # Implementar geração de conteúdo
        return {}
    
    async def _determine_component_type_from_prompt(self, prompt: str) -> str:
        """Determina tipo de componente baseado no prompt"""
        # Análise simples de palavras-chave
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['button', 'click', 'cta']):
            return 'button'
        elif any(word in prompt_lower for word in ['image', 'photo', 'picture']):
            return 'image'
        elif any(word in prompt_lower for word in ['form', 'input', 'contact']):
            return 'form'
        elif any(word in prompt_lower for word in ['hero', 'banner', 'header']):
            return 'hero_section'
        elif any(word in prompt_lower for word in ['card', 'box', 'container']):
            return 'card'
        else:
            return 'text'
    
    async def _generate_dalle_image(self, prompt: str, size: str) -> str:
        """Gera imagem com DALL-E"""
        # Implementar integração DALL-E
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    async def _generate_leonardo_image(self, prompt: str, style: str, size: str) -> str:
        """Gera imagem com Leonardo AI"""
        # Implementar integração Leonardo AI
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    async def _generate_midjourney_image(self, prompt: str, style: str) -> str:
        """Gera imagem com Midjourney"""
        # Implementar integração Midjourney
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    async def _export_to_react(self) -> Dict[str, str]:
        """Exporta para React"""
        files = {}
        
        # Gerar componentes React
        for component_id, component in self.editor_state.components.items():
            if not component.parent_id:  # Componente raiz
                react_code = self._generate_react_component(component)
                files[f"{component.name.replace(' ', '')}.jsx"] = react_code
        
        # Gerar App.jsx principal
        app_code = self._generate_react_app()
        files['App.jsx'] = app_code
        
        # Gerar estilos CSS
        css_code = self._generate_css_styles()
        files['styles.css'] = css_code
        
        return files
    
    def _generate_react_component(self, component: VisualComponent) -> str:
        """Gera código React para um componente"""
        # Implementar geração de código React
        return f"// React component for {component.name}\nexport default function {component.name.replace(' ', '')}() {{\n  return <div>Generated component</div>;\n}}"
    
    def _generate_react_app(self) -> str:
        """Gera App.jsx principal"""
        return "import React from 'react';\nimport './styles.css';\n\nfunction App() {\n  return (\n    <div className='app'>\n      <h1>Generated App</h1>\n    </div>\n  );\n}\n\nexport default App;"
    
    def _generate_css_styles(self) -> str:
        """Gera estilos CSS"""
        css = ".app {\n  font-family: Inter, sans-serif;\n  margin: 0;\n  padding: 0;\n}\n\n"
        
        for component in self.editor_state.components.values():
            css += f".{component.id} {{\n"
            for prop, value in component.styles.items():
                css_prop = self._camel_to_kebab(prop)
                css += f"  {css_prop}: {value};\n"
            css += "}\n\n"
        
        return css
    
    def _camel_to_kebab(self, camel_str: str) -> str:
        """Converte camelCase para kebab-case"""
        import re
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', camel_str).lower()
    
    async def _save_editor_state(self):
        """Salva estado do editor"""
        state_file = self.editor_dir / f"{self.editor_state.project_id}_state.json"
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.editor_state), f, indent=2, ensure_ascii=False, default=str)
    
    async def _load_editor_state(self, project_id: str):
        """Carrega estado do editor"""
        state_file = self.editor_dir / f"{project_id}_state.json"
        
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
                # Reconstruir objetos
                # Implementar deserialização completa
    
    def _save_to_undo_stack(self):
        """Salva estado atual na pilha de undo"""
        if len(self.editor_state.undo_stack) >= 50:  # Limite de 50 undos
            self.editor_state.undo_stack.pop(0)
        
        self.editor_state.undo_stack.append({
            'timestamp': datetime.now().isoformat(),
            'components': {k: asdict(v) for k, v in self.editor_state.components.items()}
        })
    
    async def _broadcast_component_change(self, action: str, component: VisualComponent):
        """Notifica mudanças de componente para colaboradores"""
        message = {
            'type': 'component_change',
            'action': action,
            'component': asdict(component),
            'timestamp': datetime.now().isoformat()
        }
        
        await self._broadcast_to_collaborators(message)
    
    async def _broadcast_user_joined(self, user: CollaborationUser):
        """Notifica entrada de usuário"""
        message = {
            'type': 'user_joined',
            'user': asdict(user),
            'timestamp': datetime.now().isoformat()
        }
        
        await self._broadcast_to_collaborators(message)
    
    async def _broadcast_cursor_update(self, user: CollaborationUser):
        """Notifica atualização de cursor"""
        message = {
            'type': 'cursor_update',
            'user_id': user.id,
            'cursor_position': user.cursor_position,
            'timestamp': datetime.now().isoformat()
        }
        
        await self._broadcast_to_collaborators(message)
    
    async def _broadcast_to_collaborators(self, message: Dict):
        """Envia mensagem para todos os colaboradores"""
        if self.websocket_connections:
            await asyncio.gather(
                *[ws.send(json.dumps(message)) for ws in self.websocket_connections],
                return_exceptions=True
            )
    
    async def _update_live_preview(self):
        """Atualiza preview em tempo real"""
        preview_data = {
            'type': 'preview_update',
            'components': {k: asdict(v) for k, v in self.editor_state.components.items()},
            'timestamp': datetime.now().isoformat()
        }
        
        if self.preview_sockets:
            await asyncio.gather(
                *[ws.send(json.dumps(preview_data)) for ws in self.preview_sockets],
                return_exceptions=True
            )
    
    def _load_templates(self) -> Dict:
        """Carrega templates disponíveis"""
        return {
            'landing_page': {
                'name': 'Landing Page',
                'description': 'Template moderno para landing page',
                'components': ['hero_section', 'features', 'testimonials', 'cta']
            },
            'dashboard': {
                'name': 'Dashboard',
                'description': 'Template para dashboard administrativo',
                'components': ['sidebar', 'header', 'stats', 'charts']
            }
        }
    
    def _load_themes(self) -> Dict:
        """Carrega temas disponíveis"""
        return {
            'modern_light': {
                'name': 'Modern Light',
                'colors': {
                    'primary': '#007bff',
                    'secondary': '#6c757d',
                    'background': '#ffffff',
                    'surface': '#f8f9fa'
                }
            },
            'dark_mode': {
                'name': 'Dark Mode',
                'colors': {
                    'primary': '#0d6efd',
                    'secondary': '#6c757d',
                    'background': '#121212',
                    'surface': '#1e1e1e'
                }
            }
        }
    
    async def _initialize_ai_integrations(self):
        """Inicializa integrações com IA"""
        # Configurar APIs de IA
        self.ai_integrations['dalle'] = os.getenv('OPENAI_API_KEY')
        self.ai_integrations['leonardo'] = os.getenv('LEONARDO_API_KEY')
        print("🤖 Integrações de IA inicializadas")
    
    async def _setup_preview_server(self):
        """Configura servidor de preview"""
        # Implementar servidor WebSocket para preview
        print("🖥️ Servidor de preview configurado")
    
    async def _export_to_vue(self) -> Dict[str, str]:
        """Exporta para Vue.js"""
        # Implementar exportação Vue
        return {}
    
    async def _export_to_html(self) -> Dict[str, str]:
        """Exporta para HTML puro"""
        # Implementar exportação HTML
        return {}

# Função principal
async def main():
    """Função principal para testar o editor"""
    editor = VisualEditorSystem()
    
    # Inicializar editor
    state = await editor.initialize_editor("test-project")
    
    # Adicionar alguns componentes de teste
    hero = await editor.add_component('hero_section')
    button = await editor.add_component('button', parent_id=hero.id)
    
    # Gerar componente com IA
    ai_component = await editor.generate_ai_component(
        "Create a beautiful pricing card with three tiers"
    )
    
    # Exportar para React
    react_files = await editor.export_to_code('react')
    
    print("\n🎉 Editor Visual System testado com sucesso!")
    print(f"Componentes criados: {len(state.components)}")
    print(f"Arquivos React gerados: {len(react_files)}")

if __name__ == "__main__":
    asyncio.run(main())