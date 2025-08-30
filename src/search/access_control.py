#!/usr/bin/env python3
"""
Sistema de Controle de Acesso para RAG
Controla o acesso a informações sensíveis baseado em palavras-chave de autorização
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AccessControlResult:
    """Resultado da verificação de controle de acesso"""
    access_granted: bool
    filtered_chunks: List[Dict[str, Any]]
    restricted_count: int
    access_level: str
    authorization_found: bool
    message: Optional[str] = None

class AccessController:
    """Controlador de acesso para informações sensíveis no RAG"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Palavra-chave de autorização para criação de agentes
        self.AGENT_BUILDER_AUTH_KEY = "vinapermitecriar"
        
        # Categorias de conteúdo restrito - MAIS ESPECÍFICAS
        self.restricted_categories = {
            'agent_building': {
                'keywords': [
                    'agent builder', 'agent creation', 'building agents', 'create agent',
                    'agent development', 'agent framework development', 'agent architecture design',
                    'langchain agent tutorial', 'langgraph agent creation', 'autogen setup',
                    'crewai implementation', 'multi-agent system development',
                    'agent deployment guide', 'agent orchestration setup',
                    'how to build agent', 'agent development tutorial',
                    'agent design patterns implementation', 'agent best practices guide'
                ],
                'auth_required': self.AGENT_BUILDER_AUTH_KEY,
                'access_level': 'restricted',
                'description': 'Informações específicas sobre criação e desenvolvimento de agentes AI'
            }
        }
        
        # Padrões de detecção de conteúdo restrito
        self.detection_patterns = {
            'agent_building': [
                r'\b(agent|agente)\s+(building|creation|development|framework)\b',
                r'\b(ai|artificial intelligence)\s+agent\b',
                r'\b(multi-agent|multiagent)\b',
                r'\b(langchain|langgraph|autogen|crewai)\b',
                r'\b(agent|agente)\s+(architecture|design|pattern)\b',
                r'\b(autonomous|conversational|task)\s+agent\b',
                r'\b(rag|retrieval augmented generation)\s+agent\b',
                r'\b(agent|agente)\s+(deployment|orchestration|workflow)\b'
            ]
        }
        
        # Estatísticas
        self._stats = {
            'total_checks': 0,
            'access_granted': 0,
            'access_denied': 0,
            'restricted_chunks_filtered': 0,
            'authorization_attempts': 0,
            'successful_authorizations': 0
        }
        
        self.logger.info("AccessController inicializado")
    
    def check_access(self, 
                    query: str, 
                    chunks: List[Dict[str, Any]], 
                    context: Optional[Dict[str, Any]] = None) -> AccessControlResult:
        """Verifica acesso e filtra chunks baseado em autorização"""
        self._stats['total_checks'] += 1
        
        # 1. Detectar se a consulta contém palavra-chave de autorização
        authorization_found = self._check_authorization(query)
        
        # 2. Identificar chunks que contêm conteúdo restrito
        restricted_chunks, unrestricted_chunks = self._classify_chunks(chunks)
        
        # 3. Determinar nível de acesso
        if not restricted_chunks:
            # Nenhum conteúdo restrito encontrado
            self._stats['access_granted'] += 1
            return AccessControlResult(
                access_granted=True,
                filtered_chunks=chunks,
                restricted_count=0,
                access_level='public',
                authorization_found=authorization_found
            )
        
        # 4. Verificar autorização para conteúdo restrito
        if authorization_found:
            self._stats['access_granted'] += 1
            self._stats['successful_authorizations'] += 1
            return AccessControlResult(
                access_granted=True,
                filtered_chunks=chunks,  # Todos os chunks liberados
                restricted_count=len(restricted_chunks),
                access_level='authorized',
                authorization_found=True,
                message=f"Acesso autorizado a {len(restricted_chunks)} recursos sobre criação de agentes"
            )
        else:
            # Acesso negado - filtrar conteúdo restrito
            self._stats['access_denied'] += 1
            self._stats['restricted_chunks_filtered'] += len(restricted_chunks)
            
            return AccessControlResult(
                access_granted=False,
                filtered_chunks=unrestricted_chunks,
                restricted_count=len(restricted_chunks),
                access_level='filtered',
                authorization_found=False,
                message=f"Acesso restrito: {len(restricted_chunks)} recursos sobre criação de agentes foram filtrados. Use a palavra-chave de autorização para acessar."
            )
    
    def _check_authorization(self, query: str) -> bool:
        """Verifica se a consulta contém palavra-chave de autorização"""
        self._stats['authorization_attempts'] += 1
        
        # Normalizar query para busca case-insensitive
        normalized_query = query.lower().strip()
        
        # Verificar presença da palavra-chave de autorização
        auth_found = self.AGENT_BUILDER_AUTH_KEY.lower() in normalized_query
        
        if auth_found:
            self.logger.info(f"Autorização encontrada na consulta: {self.AGENT_BUILDER_AUTH_KEY}")
        
        return auth_found
    
    def _classify_chunks(self, chunks: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Classifica chunks em restritos e não-restritos"""
        restricted_chunks = []
        unrestricted_chunks = []
        
        for chunk in chunks:
            if self._is_restricted_content(chunk):
                restricted_chunks.append(chunk)
            else:
                unrestricted_chunks.append(chunk)
        
        return restricted_chunks, unrestricted_chunks
    
    def _is_restricted_content(self, chunk: Dict[str, Any]) -> bool:
        """Verifica se um chunk contém conteúdo restrito"""
        # Extrair texto do chunk
        text_content = ""
        if 'content' in chunk:
            text_content += chunk['content']
        if 'title' in chunk:
            text_content += " " + chunk['title']
        if 'metadata' in chunk and isinstance(chunk['metadata'], dict):
            if 'title' in chunk['metadata']:
                text_content += " " + chunk['metadata']['title']
            if 'description' in chunk['metadata']:
                text_content += " " + chunk['metadata']['description']
        
        text_content = text_content.lower()
        
        # Verificar padrões de conteúdo restrito
        for category, patterns in self.detection_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    return True
        
        # Verificar palavras-chave de conteúdo restrito
        for category, config in self.restricted_categories.items():
            for keyword in config['keywords']:
                if keyword.lower() in text_content:
                    return True
        
        return False
    
    def get_access_message(self, access_result: AccessControlResult) -> str:
        """Gera mensagem informativa sobre o controle de acesso"""
        if access_result.access_granted and access_result.access_level == 'authorized':
            return f"✅ Acesso autorizado concedido a recursos sobre criação de agentes."
        elif not access_result.access_granted:
            return f"🔒 {access_result.restricted_count} recursos sobre criação de agentes foram filtrados. Para acessar essas informações, inclua a palavra-chave de autorização '{self.AGENT_BUILDER_AUTH_KEY}' em sua consulta."
        else:
            return "✅ Consulta processada normalmente."
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do controle de acesso"""
        return {
            **self._stats,
            'access_rate': self._stats['access_granted'] / max(self._stats['total_checks'], 1),
            'authorization_success_rate': self._stats['successful_authorizations'] / max(self._stats['authorization_attempts'], 1),
            'avg_restricted_per_check': self._stats['restricted_chunks_filtered'] / max(self._stats['total_checks'], 1)
        }
    
    def add_restricted_category(self, 
                              category_name: str, 
                              keywords: List[str], 
                              auth_key: str, 
                              patterns: Optional[List[str]] = None):
        """Adiciona nova categoria de conteúdo restrito"""
        self.restricted_categories[category_name] = {
            'keywords': keywords,
            'auth_required': auth_key,
            'access_level': 'restricted',
            'description': f'Categoria restrita: {category_name}'
        }
        
        if patterns:
            self.detection_patterns[category_name] = patterns
        
        self.logger.info(f"Nova categoria restrita adicionada: {category_name}")
    
    def remove_restricted_category(self, category_name: str):
        """Remove categoria de conteúdo restrito"""
        if category_name in self.restricted_categories:
            del self.restricted_categories[category_name]
        
        if category_name in self.detection_patterns:
            del self.detection_patterns[category_name]
        
        self.logger.info(f"Categoria restrita removida: {category_name}")