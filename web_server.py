#!/usr/bin/env python3
"""
Servidor Web da Vibe Creation Platform
Servidor simples para acessar projetos e demonstrar a plataforma
"""

import json
import os
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Diretórios da plataforma
VIBE_DIR = Path('.vibe')
PROJECTS_DIR = VIBE_DIR / 'projects'
PLATFORM_STATE_FILE = VIBE_DIR / 'platform_state.json'

# Template HTML principal
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎨 Vibe Creation Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-4px);
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 16px;
            font-size: 1.3rem;
        }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status.active {
            background: #d4edda;
            color: #155724;
        }
        .status.partial {
            background: #fff3cd;
            color: #856404;
        }
        .projects-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        .project-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .project-title {
            font-size: 1.4rem;
            color: #333;
            margin-bottom: 8px;
        }
        .project-meta {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 16px;
        }
        .project-description {
            color: #555;
            line-height: 1.6;
            margin-bottom: 16px;
        }
        .project-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 16px;
        }
        .tag {
            background: #f0f0f0;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            color: #666;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: background 0.3s ease;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }
        .ai-assets {
            margin-top: 16px;
        }
        .ai-asset {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 8px;
            border-left: 3px solid #28a745;
        }
        .ai-asset.failed {
            border-left-color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Vibe Creation Platform</h1>
            <p>A revolução da criação visual está aqui!</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>📊 Status da Plataforma</h3>
                <p><strong>Status:</strong> <span class="status active">{{ platform_status }}</span></p>
                <p><strong>Sistemas Ativos:</strong> {{ active_systems }}/{{ total_systems }}</p>
                <p><strong>Última Atualização:</strong> {{ last_update }}</p>
            </div>
            
            <div class="card">
                <h3>🚀 Projetos</h3>
                <p><strong>Total:</strong> {{ total_projects }}</p>
                <p><strong>Em Desenvolvimento:</strong> {{ active_projects }}</p>
                <a href="/projects" class="btn">Ver Todos os Projetos</a>
            </div>
            
            <div class="card">
                <h3>🤖 IA Generativa</h3>
                <p><strong>Providers:</strong> DALL-E, Leonardo, Kling, Veo3, HeyGen</p>
                <p><strong>Tipos:</strong> Imagem, Vídeo, Avatar, Texto</p>
                <a href="/ai-hub" class="btn">Acessar IA Hub</a>
            </div>
        </div>
        
        {% if projects %}
        <h2 style="color: white; margin-bottom: 20px;">📁 Projetos Recentes</h2>
        <div class="projects-grid">
            {% for project in projects %}
            <div class="project-card">
                <div class="project-title">{{ project.name }}</div>
                <div class="project-meta">
                    ID: {{ project.id[:8] }}... | Criado: {{ project.created_at }}
                </div>
                <div class="project-description">{{ project.description }}</div>
                <div class="project-description"><strong>Vibe:</strong> {{ project.vibe_description }}</div>
                
                {% if project.tags %}
                <div class="project-tags">
                    {% for tag in project.tags %}
                    <span class="tag">{{ tag }}</span>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if project.ai_assets %}
                <div class="ai-assets">
                    <strong>🤖 Assets de IA:</strong>
                    {% for asset_id, asset in project.ai_assets.items() %}
                    <div class="ai-asset {{ 'failed' if asset.status == 'failed' else '' }}">
                        <strong>{{ asset.type.title() }}:</strong> {{ asset.provider }}
                        <br><small>Status: {{ asset.status }}</small>
                        {% if asset.error_message %}
                        <br><small style="color: #dc3545;">Erro: {{ asset.error_message }}</small>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
                
                <a href="/project/{{ project.id }}" class="btn">Ver Projeto</a>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="footer">
            <p>🌟 Vibe Creation Platform - Transformando ideias em realidade visual</p>
            <p>Acesse via: <strong>http://localhost:5000</strong></p>
        </div>
    </div>
</body>
</html>
"""

PROJECT_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project.name }} - Vibe Creation Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        .project-card {
            background: white;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .project-title {
            font-size: 2.5rem;
            color: #667eea;
            margin-bottom: 16px;
        }
        .project-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .meta-item {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
        }
        .meta-label {
            font-weight: bold;
            color: #666;
            font-size: 0.9rem;
        }
        .meta-value {
            color: #333;
            margin-top: 4px;
        }
        .color-palette {
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }
        .color-swatch {
            width: 30px;
            height: 30px;
            border-radius: 4px;
            border: 2px solid #ddd;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-secondary:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📁 Detalhes do Projeto</h1>
            <a href="/" class="btn btn-secondary">← Voltar ao Dashboard</a>
        </div>
        
        <div class="project-card">
            <div class="project-title">{{ project.name }}</div>
            
            <div class="project-meta">
                <div class="meta-item">
                    <div class="meta-label">ID do Projeto</div>
                    <div class="meta-value">{{ project.id }}</div>
                </div>
                
                <div class="meta-item">
                    <div class="meta-label">Tipo</div>
                    <div class="meta-value">{{ project.project_type }}</div>
                </div>
                
                <div class="meta-item">
                    <div class="meta-label">Status</div>
                    <div class="meta-value">{{ project.status }}</div>
                </div>
                
                <div class="meta-item">
                    <div class="meta-label">Público-Alvo</div>
                    <div class="meta-value">{{ project.target_audience }}</div>
                </div>
                
                <div class="meta-item">
                    <div class="meta-label">Estilo da Marca</div>
                    <div class="meta-value">{{ project.brand_style }}</div>
                </div>
                
                <div class="meta-item">
                    <div class="meta-label">Criado em</div>
                    <div class="meta-value">{{ project.created_at }}</div>
                </div>
            </div>
            
            <div class="meta-item">
                <div class="meta-label">Descrição</div>
                <div class="meta-value">{{ project.description }}</div>
            </div>
            
            <div class="meta-item">
                <div class="meta-label">Vibe do Projeto</div>
                <div class="meta-value">{{ project.vibe_description }}</div>
            </div>
            
            {% if project.color_palette %}
            <div class="meta-item">
                <div class="meta-label">Paleta de Cores</div>
                <div class="color-palette">
                    {% for color in project.color_palette %}
                    <div class="color-swatch" style="background-color: {{ color }}" title="{{ color }}"></div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if project.typography %}
            <div class="meta-item">
                <div class="meta-label">Tipografia</div>
                <div class="meta-value">
                    <strong>Primária:</strong> {{ project.typography.primary }}<br>
                    <strong>Secundária:</strong> {{ project.typography.secondary }}
                </div>
            </div>
            {% endif %}
            
            {% if project.ai_assets %}
            <div class="meta-item">
                <div class="meta-label">🤖 Assets de IA Gerados</div>
                <div class="meta-value">
                    {% for asset_id, asset in project.ai_assets.items() %}
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 6px; margin-bottom: 8px;">
                        <strong>{{ asset.type.title() }}:</strong> {{ asset.provider }}<br>
                        <small><strong>Status:</strong> {{ asset.status }}</small><br>
                        {% if asset.error_message %}
                        <small style="color: #dc3545;"><strong>Erro:</strong> {{ asset.error_message }}</small><br>
                        {% endif %}
                        <small><strong>Prompt:</strong> {{ asset.prompt[:100] }}...</small>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            <div style="margin-top: 24px;">
                <a href="/" class="btn">← Voltar ao Dashboard</a>
                <a href="/project/{{ project.id }}/preview" class="btn">🚀 Preview do Projeto</a>
                <a href="/project/{{ project.id }}/edit" class="btn">✏️ Editar Projeto</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

def load_platform_state():
    """Carrega o estado da plataforma"""
    try:
        if PLATFORM_STATE_FILE.exists():
            with open(PLATFORM_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar estado da plataforma: {e}")
    return {}

def load_projects():
    """Carrega todos os projetos"""
    projects = []
    try:
        if PROJECTS_DIR.exists():
            for project_file in PROJECTS_DIR.glob('*.json'):
                with open(project_file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                    projects.append(project_data)
    except Exception as e:
        print(f"Erro ao carregar projetos: {e}")
    
    # Ordenar por data de criação (mais recente primeiro)
    projects.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return projects

def load_project(project_id):
    """Carrega um projeto específico"""
    try:
        project_file = PROJECTS_DIR / f"{project_id}.json"
        if project_file.exists():
            with open(project_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar projeto {project_id}: {e}")
    return None

@app.route('/')
def dashboard():
    """Dashboard principal da plataforma"""
    platform_state = load_platform_state()
    projects = load_projects()
    
    # Estatísticas da plataforma
    platform_status = platform_state.get('initialization', {}).get('platform_status', 'unknown')
    systems_status = platform_state.get('initialization', {}).get('systems_status', {})
    
    active_systems = sum(1 for system in systems_status.values() if system.get('status') == 'active')
    total_systems = len(systems_status)
    
    total_projects = len(projects)
    active_projects = sum(1 for p in projects if p.get('status') == 'designing')
    
    return render_template_string(MAIN_TEMPLATE, 
        platform_status=platform_status,
        active_systems=active_systems,
        total_systems=total_systems,
        total_projects=total_projects,
        active_projects=active_projects,
        projects=projects[:3],  # Mostrar apenas os 3 mais recentes
        last_update=datetime.now().strftime('%d/%m/%Y %H:%M')
    )

@app.route('/projects')
def projects_list():
    """Lista todos os projetos"""
    projects = load_projects()
    return jsonify({
        'total': len(projects),
        'projects': projects
    })

@app.route('/project/<project_id>')
def project_detail(project_id):
    """Detalhes de um projeto específico"""
    project = load_project(project_id)
    if not project:
        return "Projeto não encontrado", 404
    
    return render_template_string(PROJECT_TEMPLATE, project=project)

@app.route('/project/<project_id>/preview')
def project_preview(project_id):
    """Preview do projeto (simulado)"""
    project = load_project(project_id)
    if not project:
        return "Projeto não encontrado", 404
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Preview: {project['name']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 40px; background: {project.get('color_palette', ['#f0f0f0'])[0]}; }}
            .preview {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            h1 {{ color: {project.get('color_palette', ['#333'])[0]}; }}
        </style>
    </head>
    <body>
        <div class="preview">
            <h1>🚀 {project['name']}</h1>
            <p><strong>Descrição:</strong> {project['description']}</p>
            <p><strong>Vibe:</strong> {project['vibe_description']}</p>
            <p><strong>Tipo:</strong> {project['project_type']}</p>
            <p><strong>Público-alvo:</strong> {project['target_audience']}</p>
            <hr>
            <p><em>Este é um preview simulado do projeto. Em uma implementação completa, aqui seria renderizado o projeto real com todos os componentes visuais.</em></p>
            <br>
            <a href="/project/{project_id}" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px;">← Voltar aos Detalhes</a>
        </div>
    </body>
    </html>
    """

@app.route('/ai-hub')
def ai_hub():
    """Hub de IA Generativa"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 IA Hub - Vibe Creation Platform</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            .ai-provider { background: rgba(255,255,255,0.1); padding: 20px; margin: 10px 0; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 IA Hub - Geradores Disponíveis</h1>
            
            <div class="ai-provider">
                <h3>🎨 DALL-E 3 (OpenAI)</h3>
                <p>Geração de imagens de alta qualidade</p>
                <p><strong>Status:</strong> Configuração necessária (OPENAI_API_KEY)</p>
            </div>
            
            <div class="ai-provider">
                <h3>🎭 Leonardo AI</h3>
                <p>Arte digital e ilustrações</p>
                <p><strong>Status:</strong> Disponível</p>
            </div>
            
            <div class="ai-provider">
                <h3>🎬 Kling AI</h3>
                <p>Geração de vídeos</p>
                <p><strong>Status:</strong> Disponível</p>
            </div>
            
            <div class="ai-provider">
                <h3>🎥 Veo 3</h3>
                <p>Vídeos avançados</p>
                <p><strong>Status:</strong> Disponível</p>
            </div>
            
            <div class="ai-provider">
                <h3>👤 HeyGen</h3>
                <p>Avatares e apresentações</p>
                <p><strong>Status:</strong> Disponível</p>
            </div>
            
            <br>
            <a href="/" style="background: rgba(255,255,255,0.2); color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px;">← Voltar ao Dashboard</a>
        </div>
    </body>
    </html>
    """

@app.route('/api/status')
def api_status():
    """API de status da plataforma"""
    platform_state = load_platform_state()
    projects = load_projects()
    
    return jsonify({
        'platform_status': platform_state.get('initialization', {}).get('platform_status', 'unknown'),
        'total_projects': len(projects),
        'active_projects': sum(1 for p in projects if p.get('status') == 'designing'),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🌐 Iniciando servidor web da Vibe Creation Platform...")
    print("📍 Acesse: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000")
    print("📁 Projetos: http://localhost:5000/projects")
    print("🤖 IA Hub: http://localhost:5000/ai-hub")
    print("\n🎨 Vibe Creation Platform - A revolução da criação visual!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)