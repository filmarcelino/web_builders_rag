#!/usr/bin/env python3
"""
Context-Aware AI System - Sistema de IA Sensível ao Contexto

Este sistema implementa uma IA avançada que:
1. Analisa projetos e entende o contexto
2. Aprende com interações do usuário
3. Fornece recomendações inteligentes
4. Adapta-se ao estilo e preferências
5. Otimiza prompts automaticamente
6. Prediz necessidades futuras

É o cérebro por trás da Vibe Creation Platform.
"""

import asyncio
import json
import os
import time
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any, Tuple, Set
from pathlib import Path
import uuid
import pickle
from collections import defaultdict, deque
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import openai

@dataclass
class ProjectContext:
    """Contexto completo de um projeto"""
    project_id: str
    project_type: str
    industry: str
    target_audience: str
    brand_personality: List[str]
    visual_style: str
    color_psychology: Dict[str, str]
    content_tone: str
    technical_requirements: List[str]
    business_goals: List[str]
    user_journey_stage: str
    competitive_landscape: List[str]
    success_metrics: List[str]
    constraints: List[str]
    opportunities: List[str]

@dataclass
class UserBehaviorPattern:
    """Padrão de comportamento do usuário"""
    user_id: str
    preferred_styles: List[str]
    common_project_types: List[str]
    ai_usage_patterns: Dict[str, int]
    design_preferences: Dict[str, Any]
    workflow_patterns: List[str]
    time_patterns: Dict[str, List[int]]  # Horários de maior atividade
    collaboration_style: str
    feedback_patterns: Dict[str, float]
    learning_speed: float
    creativity_level: float
    technical_proficiency: float

@dataclass
class AIRecommendation:
    """Recomendação gerada pela IA"""
    id: str
    type: str  # 'component', 'ai_generation', 'workflow', 'optimization'
    title: str
    description: str
    confidence_score: float
    priority: str  # 'critical', 'high', 'medium', 'low'
    category: str
    suggested_action: Dict[str, Any]
    reasoning: str
    expected_impact: str
    implementation_effort: str
    dependencies: List[str]
    alternatives: List[Dict[str, Any]]
    success_probability: float
    created_at: str

@dataclass
class LearningInsight:
    """Insight aprendido pela IA"""
    id: str
    insight_type: str
    pattern_detected: str
    confidence: float
    supporting_data: List[Dict]
    actionable_recommendations: List[str]
    impact_assessment: str
    validation_status: str
    created_at: str

class ProjectIntelligenceEngine:
    """Motor de inteligência para análise de projetos"""
    
    def __init__(self):
        self.project_patterns = {}
        self.success_indicators = {}
        self.failure_patterns = {}
        self.industry_benchmarks = {}
        
    async def analyze_project_context(self, project_data: Dict) -> ProjectContext:
        """Analisa e extrai contexto completo do projeto"""
        
        # Análise de indústria baseada em descrição e tipo
        industry = await self._detect_industry(project_data)
        
        # Análise de personalidade da marca
        brand_personality = await self._analyze_brand_personality(
            project_data.get('vibe_description', ''),
            project_data.get('description', '')
        )
        
        # Psicologia das cores
        color_psychology = await self._analyze_color_psychology(
            project_data.get('color_palette', [])
        )
        
        # Análise de requisitos técnicos
        technical_requirements = await self._extract_technical_requirements(project_data)
        
        # Análise competitiva
        competitive_landscape = await self._analyze_competitive_landscape(
            industry, project_data.get('project_type')
        )
        
        # Identificar oportunidades
        opportunities = await self._identify_opportunities(
            project_data, industry, competitive_landscape
        )
        
        return ProjectContext(
            project_id=project_data['id'],
            project_type=project_data.get('project_type', 'unknown'),
            industry=industry,
            target_audience=project_data.get('target_audience', 'general'),
            brand_personality=brand_personality,
            visual_style=project_data.get('brand_style', 'modern'),
            color_psychology=color_psychology,
            content_tone=await self._determine_content_tone(brand_personality),
            technical_requirements=technical_requirements,
            business_goals=await self._extract_business_goals(project_data),
            user_journey_stage='awareness',  # Detectar automaticamente
            competitive_landscape=competitive_landscape,
            success_metrics=await self._define_success_metrics(project_data),
            constraints=await self._identify_constraints(project_data),
            opportunities=opportunities
        )
    
    async def _detect_industry(self, project_data: Dict) -> str:
        """Detecta a indústria do projeto"""
        description = f"{project_data.get('description', '')} {project_data.get('vibe_description', '')}"
        
        industry_keywords = {
            'technology': ['ai', 'software', 'app', 'tech', 'digital', 'saas', 'platform'],
            'healthcare': ['health', 'medical', 'wellness', 'fitness', 'therapy'],
            'finance': ['finance', 'banking', 'investment', 'crypto', 'fintech'],
            'ecommerce': ['shop', 'store', 'product', 'buy', 'sell', 'marketplace'],
            'education': ['education', 'learning', 'course', 'school', 'training'],
            'real_estate': ['property', 'real estate', 'home', 'apartment', 'rent'],
            'food': ['restaurant', 'food', 'recipe', 'cooking', 'delivery'],
            'travel': ['travel', 'hotel', 'booking', 'vacation', 'tourism'],
            'entertainment': ['game', 'music', 'movie', 'entertainment', 'media'],
            'nonprofit': ['nonprofit', 'charity', 'foundation', 'cause', 'volunteer']
        }
        
        description_lower = description.lower()
        industry_scores = {}
        
        for industry, keywords in industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            if score > 0:
                industry_scores[industry] = score
        
        if industry_scores:
            return max(industry_scores, key=industry_scores.get)
        
        return 'general'
    
    async def _analyze_brand_personality(self, vibe_description: str, description: str) -> List[str]:
        """Analisa personalidade da marca"""
        text = f"{vibe_description} {description}".lower()
        
        personality_traits = {
            'innovative': ['innovative', 'cutting-edge', 'revolutionary', 'advanced', 'future'],
            'trustworthy': ['reliable', 'secure', 'trusted', 'professional', 'established'],
            'friendly': ['friendly', 'welcoming', 'warm', 'approachable', 'personal'],
            'premium': ['luxury', 'premium', 'exclusive', 'high-end', 'sophisticated'],
            'playful': ['fun', 'playful', 'creative', 'colorful', 'energetic'],
            'minimalist': ['clean', 'simple', 'minimal', 'elegant', 'refined'],
            'bold': ['bold', 'strong', 'powerful', 'dynamic', 'impactful'],
            'authentic': ['authentic', 'genuine', 'real', 'honest', 'transparent']
        }
        
        detected_traits = []
        for trait, keywords in personality_traits.items():
            if any(keyword in text for keyword in keywords):
                detected_traits.append(trait)
        
        return detected_traits if detected_traits else ['professional']
    
    async def _analyze_color_psychology(self, color_palette: List[str]) -> Dict[str, str]:
        """Analisa psicologia das cores"""
        color_meanings = {
            '#007bff': 'trust, reliability, professionalism',
            '#28a745': 'growth, success, nature',
            '#dc3545': 'urgency, passion, energy',
            '#ffc107': 'optimism, creativity, attention',
            '#6f42c1': 'luxury, creativity, innovation',
            '#fd7e14': 'enthusiasm, warmth, confidence',
            '#20c997': 'balance, harmony, freshness',
            '#6c757d': 'neutrality, sophistication, balance'
        }
        
        psychology = {}
        for color in color_palette:
            if color in color_meanings:
                psychology[color] = color_meanings[color]
            else:
                # Análise básica por cor
                if 'blue' in color.lower() or color.startswith('#0'):
                    psychology[color] = 'trust, stability'
                elif 'green' in color.lower() or color.startswith('#2'):
                    psychology[color] = 'growth, nature'
                elif 'red' in color.lower() or color.startswith('#d'):
                    psychology[color] = 'energy, passion'
                else:
                    psychology[color] = 'neutral'
        
        return psychology
    
    async def _extract_technical_requirements(self, project_data: Dict) -> List[str]:
        """Extrai requisitos técnicos"""
        requirements = []
        
        project_type = project_data.get('project_type', '')
        
        if project_type == 'ecommerce':
            requirements.extend([
                'payment_processing', 'inventory_management', 'user_authentication',
                'shopping_cart', 'order_tracking', 'product_catalog'
            ])
        elif project_type == 'dashboard':
            requirements.extend([
                'data_visualization', 'real_time_updates', 'user_roles',
                'analytics', 'reporting', 'api_integration'
            ])
        elif project_type == 'landing_page':
            requirements.extend([
                'lead_capture', 'analytics_tracking', 'seo_optimization',
                'responsive_design', 'fast_loading'
            ])
        
        # Adicionar requisitos baseados na descrição
        description = project_data.get('description', '').lower()
        if 'mobile' in description:
            requirements.append('mobile_optimization')
        if 'real-time' in description:
            requirements.append('real_time_features')
        if 'social' in description:
            requirements.append('social_integration')
        
        return list(set(requirements))
    
    async def _analyze_competitive_landscape(self, industry: str, project_type: str) -> List[str]:
        """Analisa cenário competitivo"""
        competitive_factors = {
            'technology': ['user_experience', 'performance', 'innovation', 'security'],
            'ecommerce': ['price', 'user_experience', 'product_variety', 'delivery_speed'],
            'healthcare': ['trust', 'accessibility', 'compliance', 'user_experience'],
            'finance': ['security', 'trust', 'user_experience', 'compliance'],
            'education': ['content_quality', 'user_experience', 'accessibility', 'engagement']
        }
        
        return competitive_factors.get(industry, ['user_experience', 'quality', 'performance'])
    
    async def _identify_opportunities(self, project_data: Dict, industry: str, 
                                   competitive_factors: List[str]) -> List[str]:
        """Identifica oportunidades"""
        opportunities = []
        
        # Oportunidades baseadas em tendências
        current_trends = {
            'ai_integration': 'Integrar IA para personalização',
            'voice_interface': 'Adicionar interface por voz',
            'ar_vr_features': 'Explorar realidade aumentada',
            'sustainability': 'Focar em sustentabilidade',
            'accessibility': 'Melhorar acessibilidade',
            'micro_interactions': 'Adicionar micro-interações',
            'dark_mode': 'Implementar modo escuro',
            'progressive_web_app': 'Criar PWA'
        }
        
        # Selecionar oportunidades relevantes
        for trend, description in current_trends.items():
            if self._is_trend_relevant(trend, project_data, industry):
                opportunities.append(description)
        
        return opportunities
    
    def _is_trend_relevant(self, trend: str, project_data: Dict, industry: str) -> bool:
        """Verifica se uma tendência é relevante"""
        relevance_map = {
            'ai_integration': ['technology', 'ecommerce', 'finance'],
            'voice_interface': ['technology', 'healthcare', 'education'],
            'ar_vr_features': ['ecommerce', 'real_estate', 'entertainment'],
            'sustainability': ['all'],
            'accessibility': ['all'],
            'micro_interactions': ['all'],
            'dark_mode': ['technology', 'entertainment', 'productivity'],
            'progressive_web_app': ['ecommerce', 'technology', 'media']
        }
        
        relevant_industries = relevance_map.get(trend, [])
        return 'all' in relevant_industries or industry in relevant_industries
    
    async def _determine_content_tone(self, brand_personality: List[str]) -> str:
        """Determina tom de conteúdo"""
        tone_mapping = {
            'professional': 'formal',
            'friendly': 'conversational',
            'playful': 'casual',
            'premium': 'sophisticated',
            'innovative': 'inspiring',
            'trustworthy': 'authoritative',
            'bold': 'confident',
            'authentic': 'genuine'
        }
        
        for personality in brand_personality:
            if personality in tone_mapping:
                return tone_mapping[personality]
        
        return 'professional'
    
    async def _extract_business_goals(self, project_data: Dict) -> List[str]:
        """Extrai objetivos de negócio"""
        goals = []
        
        project_type = project_data.get('project_type', '')
        
        if project_type == 'landing_page':
            goals.extend(['lead_generation', 'brand_awareness', 'conversion'])
        elif project_type == 'ecommerce':
            goals.extend(['sales_increase', 'customer_acquisition', 'retention'])
        elif project_type == 'dashboard':
            goals.extend(['data_insights', 'efficiency', 'decision_support'])
        elif project_type == 'portfolio':
            goals.extend(['showcase_work', 'personal_branding', 'lead_generation'])
        
        return goals
    
    async def _define_success_metrics(self, project_data: Dict) -> List[str]:
        """Define métricas de sucesso"""
        metrics = ['user_engagement', 'page_load_speed', 'mobile_responsiveness']
        
        project_type = project_data.get('project_type', '')
        
        if project_type == 'landing_page':
            metrics.extend(['conversion_rate', 'bounce_rate', 'lead_quality'])
        elif project_type == 'ecommerce':
            metrics.extend(['sales_conversion', 'cart_abandonment', 'customer_lifetime_value'])
        elif project_type == 'dashboard':
            metrics.extend(['data_accuracy', 'user_adoption', 'task_completion_rate'])
        
        return metrics
    
    async def _identify_constraints(self, project_data: Dict) -> List[str]:
        """Identifica restrições"""
        constraints = []
        
        # Restrições comuns
        constraints.extend(['budget_limitations', 'time_constraints', 'technical_limitations'])
        
        # Restrições específicas por indústria
        description = project_data.get('description', '').lower()
        
        if any(word in description for word in ['healthcare', 'medical', 'health']):
            constraints.extend(['hipaa_compliance', 'medical_regulations'])
        
        if any(word in description for word in ['finance', 'banking', 'payment']):
            constraints.extend(['pci_compliance', 'financial_regulations'])
        
        if any(word in description for word in ['education', 'school', 'student']):
            constraints.extend(['ferpa_compliance', 'accessibility_requirements'])
        
        return constraints

class UserBehaviorAnalyzer:
    """Analisador de comportamento do usuário"""
    
    def __init__(self):
        self.user_sessions = defaultdict(list)
        self.interaction_patterns = defaultdict(dict)
        self.learning_models = {}
    
    async def track_user_interaction(self, user_id: str, interaction_data: Dict):
        """Rastreia interação do usuário"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction_data.get('type'),
            'action': interaction_data.get('action'),
            'context': interaction_data.get('context', {}),
            'result': interaction_data.get('result'),
            'satisfaction': interaction_data.get('satisfaction'),
            'duration': interaction_data.get('duration', 0)
        }
        
        self.user_sessions[user_id].append(interaction)
        
        # Manter apenas últimas 1000 interações por usuário
        if len(self.user_sessions[user_id]) > 1000:
            self.user_sessions[user_id] = self.user_sessions[user_id][-1000:]
    
    async def analyze_user_patterns(self, user_id: str) -> UserBehaviorPattern:
        """Analisa padrões de comportamento do usuário"""
        
        if user_id not in self.user_sessions:
            return self._create_default_pattern(user_id)
        
        sessions = self.user_sessions[user_id]
        
        # Analisar preferências de estilo
        preferred_styles = await self._analyze_style_preferences(sessions)
        
        # Analisar tipos de projeto comuns
        common_project_types = await self._analyze_project_type_preferences(sessions)
        
        # Analisar padrões de uso de IA
        ai_usage_patterns = await self._analyze_ai_usage(sessions)
        
        # Analisar preferências de design
        design_preferences = await self._analyze_design_preferences(sessions)
        
        # Analisar padrões de workflow
        workflow_patterns = await self._analyze_workflow_patterns(sessions)
        
        # Analisar padrões temporais
        time_patterns = await self._analyze_time_patterns(sessions)
        
        # Calcular métricas de comportamento
        collaboration_style = await self._determine_collaboration_style(sessions)
        feedback_patterns = await self._analyze_feedback_patterns(sessions)
        learning_speed = await self._calculate_learning_speed(sessions)
        creativity_level = await self._assess_creativity_level(sessions)
        technical_proficiency = await self._assess_technical_proficiency(sessions)
        
        return UserBehaviorPattern(
            user_id=user_id,
            preferred_styles=preferred_styles,
            common_project_types=common_project_types,
            ai_usage_patterns=ai_usage_patterns,
            design_preferences=design_preferences,
            workflow_patterns=workflow_patterns,
            time_patterns=time_patterns,
            collaboration_style=collaboration_style,
            feedback_patterns=feedback_patterns,
            learning_speed=learning_speed,
            creativity_level=creativity_level,
            technical_proficiency=technical_proficiency
        )
    
    def _create_default_pattern(self, user_id: str) -> UserBehaviorPattern:
        """Cria padrão padrão para novo usuário"""
        return UserBehaviorPattern(
            user_id=user_id,
            preferred_styles=['modern'],
            common_project_types=['landing_page'],
            ai_usage_patterns={'image': 0, 'text': 0, 'video': 0},
            design_preferences={'complexity': 'medium', 'color_preference': 'cool'},
            workflow_patterns=['design_first'],
            time_patterns={'weekday': [9, 10, 11, 14, 15, 16], 'weekend': [10, 11, 15, 16]},
            collaboration_style='independent',
            feedback_patterns={'positive': 0.5, 'negative': 0.5},
            learning_speed=0.5,
            creativity_level=0.5,
            technical_proficiency=0.5
        )
    
    async def _analyze_style_preferences(self, sessions: List[Dict]) -> List[str]:
        """Analisa preferências de estilo"""
        style_counts = defaultdict(int)
        
        for session in sessions:
            context = session.get('context', {})
            if 'style' in context:
                style_counts[context['style']] += 1
        
        # Retornar top 3 estilos
        sorted_styles = sorted(style_counts.items(), key=lambda x: x[1], reverse=True)
        return [style for style, count in sorted_styles[:3]]
    
    async def _analyze_project_type_preferences(self, sessions: List[Dict]) -> List[str]:
        """Analisa preferências de tipo de projeto"""
        type_counts = defaultdict(int)
        
        for session in sessions:
            context = session.get('context', {})
            if 'project_type' in context:
                type_counts[context['project_type']] += 1
        
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return [ptype for ptype, count in sorted_types[:3]]
    
    async def _analyze_ai_usage(self, sessions: List[Dict]) -> Dict[str, int]:
        """Analisa padrões de uso de IA"""
        ai_usage = defaultdict(int)
        
        for session in sessions:
            if session.get('type') == 'ai_generation':
                ai_type = session.get('context', {}).get('ai_type', 'unknown')
                ai_usage[ai_type] += 1
        
        return dict(ai_usage)
    
    async def _analyze_design_preferences(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Analisa preferências de design"""
        preferences = {
            'complexity': 'medium',
            'color_preference': 'neutral',
            'layout_preference': 'grid',
            'animation_preference': 'subtle'
        }
        
        # Analisar com base nas interações
        complexity_scores = []
        color_preferences = defaultdict(int)
        
        for session in sessions:
            context = session.get('context', {})
            
            if 'complexity' in context:
                complexity_map = {'simple': 1, 'medium': 2, 'complex': 3}
                complexity_scores.append(complexity_map.get(context['complexity'], 2))
            
            if 'colors' in context:
                for color in context['colors']:
                    if color.startswith('#'):
                        # Classificar cor como warm/cool/neutral
                        color_type = self._classify_color(color)
                        color_preferences[color_type] += 1
        
        if complexity_scores:
            avg_complexity = sum(complexity_scores) / len(complexity_scores)
            if avg_complexity < 1.5:
                preferences['complexity'] = 'simple'
            elif avg_complexity > 2.5:
                preferences['complexity'] = 'complex'
        
        if color_preferences:
            preferences['color_preference'] = max(color_preferences, key=color_preferences.get)
        
        return preferences
    
    def _classify_color(self, color: str) -> str:
        """Classifica cor como warm/cool/neutral"""
        # Implementação simplificada
        if color.lower() in ['#ff0000', '#ff6b6b', '#ffa500', '#ffff00']:
            return 'warm'
        elif color.lower() in ['#0000ff', '#00ffff', '#008000', '#800080']:
            return 'cool'
        else:
            return 'neutral'
    
    async def _analyze_workflow_patterns(self, sessions: List[Dict]) -> List[str]:
        """Analisa padrões de workflow"""
        workflows = []
        
        # Analisar sequência de ações
        action_sequences = []
        current_sequence = []
        
        for session in sessions:
            action = session.get('action')
            if action:
                current_sequence.append(action)
                
                # Se mudou de contexto, salvar sequência
                if len(current_sequence) > 3:
                    action_sequences.append(current_sequence.copy())
                    current_sequence = []
        
        # Identificar padrões comuns
        common_patterns = self._find_common_sequences(action_sequences)
        
        return common_patterns[:5]  # Top 5 padrões
    
    def _find_common_sequences(self, sequences: List[List[str]]) -> List[str]:
        """Encontra sequências comuns"""
        # Implementação simplificada
        pattern_counts = defaultdict(int)
        
        for sequence in sequences:
            for i in range(len(sequence) - 2):
                pattern = ' -> '.join(sequence[i:i+3])
                pattern_counts[pattern] += 1
        
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        return [pattern for pattern, count in sorted_patterns if count > 1]
    
    async def _analyze_time_patterns(self, sessions: List[Dict]) -> Dict[str, List[int]]:
        """Analisa padrões temporais"""
        weekday_hours = defaultdict(int)
        weekend_hours = defaultdict(int)
        
        for session in sessions:
            timestamp = datetime.fromisoformat(session['timestamp'])
            hour = timestamp.hour
            
            if timestamp.weekday() < 5:  # Segunda a sexta
                weekday_hours[hour] += 1
            else:  # Fim de semana
                weekend_hours[hour] += 1
        
        # Retornar horários mais ativos
        active_weekday_hours = [hour for hour, count in weekday_hours.items() if count > 2]
        active_weekend_hours = [hour for hour, count in weekend_hours.items() if count > 1]
        
        return {
            'weekday': sorted(active_weekday_hours),
            'weekend': sorted(active_weekend_hours)
        }
    
    async def _determine_collaboration_style(self, sessions: List[Dict]) -> str:
        """Determina estilo de colaboração"""
        collaboration_actions = 0
        total_actions = len(sessions)
        
        for session in sessions:
            if session.get('type') in ['collaboration', 'share', 'comment']:
                collaboration_actions += 1
        
        if total_actions == 0:
            return 'unknown'
        
        collaboration_ratio = collaboration_actions / total_actions
        
        if collaboration_ratio > 0.3:
            return 'collaborative'
        elif collaboration_ratio > 0.1:
            return 'occasional_collaborator'
        else:
            return 'independent'
    
    async def _analyze_feedback_patterns(self, sessions: List[Dict]) -> Dict[str, float]:
        """Analisa padrões de feedback"""
        positive_feedback = 0
        negative_feedback = 0
        total_feedback = 0
        
        for session in sessions:
            satisfaction = session.get('satisfaction')
            if satisfaction is not None:
                total_feedback += 1
                if satisfaction > 0.6:
                    positive_feedback += 1
                elif satisfaction < 0.4:
                    negative_feedback += 1
        
        if total_feedback == 0:
            return {'positive': 0.5, 'negative': 0.5}
        
        return {
            'positive': positive_feedback / total_feedback,
            'negative': negative_feedback / total_feedback
        }
    
    async def _calculate_learning_speed(self, sessions: List[Dict]) -> float:
        """Calcula velocidade de aprendizado"""
        # Analisar melhoria ao longo do tempo
        if len(sessions) < 10:
            return 0.5  # Padrão para poucos dados
        
        # Dividir sessões em grupos temporais
        early_sessions = sessions[:len(sessions)//3]
        recent_sessions = sessions[-len(sessions)//3:]
        
        # Calcular métricas de eficiência
        early_efficiency = self._calculate_session_efficiency(early_sessions)
        recent_efficiency = self._calculate_session_efficiency(recent_sessions)
        
        # Calcular melhoria
        improvement = (recent_efficiency - early_efficiency) / max(early_efficiency, 0.1)
        
        # Normalizar para 0-1
        learning_speed = max(0, min(1, 0.5 + improvement))
        
        return learning_speed
    
    def _calculate_session_efficiency(self, sessions: List[Dict]) -> float:
        """Calcula eficiência das sessões"""
        if not sessions:
            return 0.5
        
        total_duration = sum(session.get('duration', 0) for session in sessions)
        successful_actions = sum(1 for session in sessions 
                               if session.get('result') == 'success')
        
        if total_duration == 0:
            return 0.5
        
        # Eficiência = ações bem-sucedidas por minuto
        efficiency = (successful_actions * 60) / total_duration
        
        # Normalizar
        return min(1, efficiency / 10)  # Assumindo 10 ações/min como máximo
    
    async def _assess_creativity_level(self, sessions: List[Dict]) -> float:
        """Avalia nível de criatividade"""
        creativity_indicators = 0
        total_sessions = len(sessions)
        
        if total_sessions == 0:
            return 0.5
        
        for session in sessions:
            context = session.get('context', {})
            action = session.get('action', '')
            
            # Indicadores de criatividade
            if any(indicator in action.lower() for indicator in 
                   ['custom', 'creative', 'unique', 'original', 'innovative']):
                creativity_indicators += 1
            
            if context.get('uses_ai_generation', False):
                creativity_indicators += 0.5
            
            if context.get('experiments_with_styles', False):
                creativity_indicators += 0.5
        
        creativity_score = creativity_indicators / total_sessions
        return min(1, creativity_score)
    
    async def _assess_technical_proficiency(self, sessions: List[Dict]) -> float:
        """Avalia proficiência técnica"""
        technical_actions = 0
        total_sessions = len(sessions)
        
        if total_sessions == 0:
            return 0.5
        
        technical_keywords = [
            'code', 'api', 'integration', 'custom_css', 'javascript',
            'advanced', 'configuration', 'deployment', 'optimization'
        ]
        
        for session in sessions:
            action = session.get('action', '').lower()
            context = session.get('context', {})
            
            if any(keyword in action for keyword in technical_keywords):
                technical_actions += 1
            
            if context.get('uses_advanced_features', False):
                technical_actions += 0.5
        
        proficiency_score = technical_actions / total_sessions
        return min(1, proficiency_score)

class ContextAwareAISystem:
    """Sistema principal de IA sensível ao contexto"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.ai_dir = self.project_dir / ".vibe" / "ai"
        self.ai_dir.mkdir(parents=True, exist_ok=True)
        
        # Componentes do sistema
        self.project_intelligence = ProjectIntelligenceEngine()
        self.behavior_analyzer = UserBehaviorAnalyzer()
        
        # Memória e aprendizado
        self.context_memory = {}
        self.learning_insights = {}
        self.recommendation_history = {}
        
        # Modelos de ML
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.project_clusters = None
        
        # Cache de recomendações
        self.recommendation_cache = {}
        
        # Estado de inicialização
        self.initialized = False
        
        print("🧠 Context-Aware AI System inicializado")
    
    async def initialize(self):
        """Inicializa o sistema de IA"""
        if self.initialized:
            return
            
        print("🚀 Inicializando Context-Aware AI...")
        
        # Carregar dados existentes
        await self._load_existing_data()
        
        self.initialized = True
        print("✅ Context-Aware AI inicializado com sucesso")
    
    async def cleanup(self):
        """Limpa recursos"""
        self.initialized = False
        
        # Treinar modelos iniciais
        await self._train_initial_models()
        
        print("✅ Context-Aware AI pronto!")
    
    async def analyze_project_and_generate_recommendations(self, project_data: Dict, 
                                                         user_id: str) -> List[AIRecommendation]:
        """Analisa projeto e gera recomendações inteligentes"""
        
        # 1. Analisar contexto do projeto
        project_context = await self.project_intelligence.analyze_project_context(project_data)
        
        # 2. Analisar padrões do usuário
        user_patterns = await self.behavior_analyzer.analyze_user_patterns(user_id)
        
        # 3. Gerar recomendações contextuais
        recommendations = await self._generate_contextual_recommendations(
            project_context, user_patterns, project_data
        )
        
        # 4. Priorizar e filtrar recomendações
        prioritized_recommendations = await self._prioritize_recommendations(
            recommendations, project_context, user_patterns
        )
        
        # 5. Salvar no histórico
        await self._save_recommendation_history(
            project_data['id'], user_id, prioritized_recommendations
        )
        
        return prioritized_recommendations
    
    async def enhance_prompt_with_context(self, original_prompt: str, project_data: Dict, 
                                        user_id: str, generation_type: str) -> str:
        """Enriquece prompt com contexto inteligente"""
        
        # Obter contexto do projeto
        project_context = await self.project_intelligence.analyze_project_context(project_data)
        
        # Obter padrões do usuário
        user_patterns = await self.behavior_analyzer.analyze_user_patterns(user_id)
        
        # Construir contexto enriquecido
        context_elements = []
        
        # Contexto do projeto
        context_elements.extend([
            f"Industry: {project_context.industry}",
            f"Target audience: {project_context.target_audience}",
            f"Brand personality: {', '.join(project_context.brand_personality)}",
            f"Visual style: {project_context.visual_style}",
            f"Content tone: {project_context.content_tone}"
        ])
        
        # Contexto do usuário
        if user_patterns.preferred_styles:
            context_elements.append(f"User prefers: {', '.join(user_patterns.preferred_styles)}")
        
        if user_patterns.design_preferences:
            complexity = user_patterns.design_preferences.get('complexity', 'medium')
            context_elements.append(f"Complexity preference: {complexity}")
        
        # Contexto específico do tipo de geração
        if generation_type == 'image':
            context_elements.extend([
                f"Color psychology: {list(project_context.color_psychology.values())}",
                f"Visual opportunities: {project_context.opportunities[:2]}"
            ])
        elif generation_type == 'text':
            context_elements.extend([
                f"Business goals: {', '.join(project_context.business_goals[:3])}",
                f"Success metrics: {', '.join(project_context.success_metrics[:2])}"
            ])
        
        # Construir prompt enriquecido
        enhanced_prompt = f"{original_prompt}\n\nContext: {'; '.join(context_elements)}\n\nGenerate content that aligns with this context and maintains consistency with the project's vision."
        
        return enhanced_prompt
    
    async def learn_from_interaction(self, interaction_data: Dict):
        """Aprende com interações do usuário"""
        
        user_id = interaction_data.get('user_id')
        project_id = interaction_data.get('project_id')
        
        # Rastrear interação
        await self.behavior_analyzer.track_user_interaction(user_id, interaction_data)
        
        # Analisar feedback
        if 'feedback' in interaction_data:
            await self._process_feedback(interaction_data)
        
        # Detectar novos padrões
        if len(self.behavior_analyzer.user_sessions[user_id]) % 50 == 0:
            await self._detect_new_patterns(user_id)
        
        # Atualizar modelos se necessário
        if len(self.behavior_analyzer.user_sessions[user_id]) % 100 == 0:
            await self._update_learning_models(user_id)
    
    async def predict_user_needs(self, user_id: str, current_context: Dict) -> List[Dict]:
        """Prediz necessidades futuras do usuário"""
        
        user_patterns = await self.behavior_analyzer.analyze_user_patterns(user_id)
        
        predictions = []
        
        # Predições baseadas em padrões temporais
        current_hour = datetime.now().hour
        current_day_type = 'weekday' if datetime.now().weekday() < 5 else 'weekend'
        
        active_hours = user_patterns.time_patterns.get(current_day_type, [])
        
        if current_hour in active_hours:
            predictions.append({
                'type': 'activity_prediction',
                'prediction': 'User likely to be active now',
                'confidence': 0.8,
                'suggested_action': 'Offer proactive assistance'
            })
        
        # Predições baseadas em workflow
        for workflow in user_patterns.workflow_patterns:
            if self._matches_current_context(workflow, current_context):
                next_step = self._predict_next_workflow_step(workflow)
                predictions.append({
                    'type': 'workflow_prediction',
                    'prediction': f'User likely to {next_step} next',
                    'confidence': 0.7,
                    'suggested_action': f'Prepare {next_step} tools'
                })
        
        # Predições baseadas em uso de IA
        ai_usage = user_patterns.ai_usage_patterns
        most_used_ai = max(ai_usage, key=ai_usage.get) if ai_usage else None
        
        if most_used_ai and current_context.get('project_stage') == 'design':
            predictions.append({
                'type': 'ai_usage_prediction',
                'prediction': f'User likely to use {most_used_ai} generation',
                'confidence': 0.6,
                'suggested_action': f'Pre-load {most_used_ai} tools'
            })
        
        return predictions
    
    # Métodos auxiliares
    async def _generate_contextual_recommendations(self, project_context: ProjectContext,
                                                 user_patterns: UserBehaviorPattern,
                                                 project_data: Dict) -> List[AIRecommendation]:
        """Gera recomendações contextuais"""
        
        recommendations = []
        
        # Recomendações baseadas no tipo de projeto
        project_type_recs = await self._get_project_type_recommendations(
            project_context.project_type, project_context
        )
        recommendations.extend(project_type_recs)
        
        # Recomendações baseadas na indústria
        industry_recs = await self._get_industry_recommendations(
            project_context.industry, project_context
        )
        recommendations.extend(industry_recs)
        
        # Recomendações baseadas no usuário
        user_recs = await self._get_user_based_recommendations(
            user_patterns, project_context
        )
        recommendations.extend(user_recs)
        
        # Recomendações de oportunidades
        opportunity_recs = await self._get_opportunity_recommendations(
            project_context.opportunities, project_context
        )
        recommendations.extend(opportunity_recs)
        
        return recommendations
    
    async def _get_project_type_recommendations(self, project_type: str, 
                                              context: ProjectContext) -> List[AIRecommendation]:
        """Gera recomendações baseadas no tipo de projeto"""
        
        recommendations = []
        
        if project_type == 'landing_page':
            recommendations.extend([
                AIRecommendation(
                    id=str(uuid.uuid4()),
                    type='component',
                    title='Hero Section Impactante',
                    description='Criar uma seção hero que capture atenção imediatamente',
                    confidence_score=0.9,
                    priority='high',
                    category='design',
                    suggested_action={
                        'type': 'add_component',
                        'component': 'hero_section',
                        'parameters': {
                            'style': context.visual_style,
                            'tone': context.content_tone
                        }
                    },
                    reasoning='Landing pages precisam capturar atenção nos primeiros 3 segundos',
                    expected_impact='Aumento de 40-60% na taxa de conversão',
                    implementation_effort='medium',
                    dependencies=[],
                    alternatives=[
                        {'type': 'video_hero', 'description': 'Hero com vídeo de fundo'},
                        {'type': 'interactive_hero', 'description': 'Hero com elementos interativos'}
                    ],
                    success_probability=0.85,
                    created_at=datetime.now().isoformat()
                ),
                AIRecommendation(
                    id=str(uuid.uuid4()),
                    type='ai_generation',
                    title='Gerar Imagem Hero com IA',
                    description='Usar DALL-E 3 para criar imagem hero personalizada',
                    confidence_score=0.8,
                    priority='high',
                    category='ai_content',
                    suggested_action={
                        'type': 'ai_generation',
                        'provider': 'dalle3',
                        'content_type': 'image',
                        'prompt_template': 'Professional hero image for {industry} {project_type}'
                    },
                    reasoning='Imagens personalizadas aumentam engajamento e conversão',
                    expected_impact='Melhoria de 25-35% no tempo de permanência',
                    implementation_effort='low',
                    dependencies=['hero_section'],
                    alternatives=[
                        {'type': 'stock_photo', 'description': 'Usar foto de banco de imagens'},
                        {'type': 'illustration', 'description': 'Criar ilustração customizada'}
                    ],
                    success_probability=0.75,
                    created_at=datetime.now().isoformat()
                )
            ])
        
        elif project_type == 'ecommerce':
            recommendations.extend([
                AIRecommendation(
                    id=str(uuid.uuid4()),
                    type='component',
                    title='Grid de Produtos Inteligente',
                    description='Implementar grid de produtos com filtros e busca avançada',
                    confidence_score=0.95,
                    priority='critical',
                    category='functionality',
                    suggested_action={
                        'type': 'add_component',
                        'component': 'product_grid',
                        'parameters': {
                            'layout': 'responsive_grid',
                            'filters': ['category', 'price', 'rating'],
                            'sorting': ['popularity', 'price', 'newest']
                        }
                    },
                    reasoning='Grid de produtos é essencial para navegação e descoberta',
                    expected_impact='Aumento de 50-70% na taxa de conversão',
                    implementation_effort='high',
                    dependencies=['product_database'],
                    alternatives=[
                        {'type': 'list_view', 'description': 'Visualização em lista'},
                        {'type': 'carousel', 'description': 'Carrossel de produtos'}
                    ],
                    success_probability=0.9,
                    created_at=datetime.now().isoformat()
                )
            ])
        
        return recommendations
    
    async def _get_industry_recommendations(self, industry: str, 
                                          context: ProjectContext) -> List[AIRecommendation]:
        """Gera recomendações baseadas na indústria"""
        
        recommendations = []
        
        if industry == 'technology':
            recommendations.append(
                AIRecommendation(
                    id=str(uuid.uuid4()),
                    type='optimization',
                    title='Otimização de Performance',
                    description='Implementar lazy loading e otimizações para tech-savvy users',
                    confidence_score=0.8,
                    priority='medium',
                    category='performance',
                    suggested_action={
                        'type': 'optimization',
                        'optimizations': ['lazy_loading', 'code_splitting', 'image_optimization']
                    },
                    reasoning='Usuários de tecnologia esperam performance excepcional',
                    expected_impact='Melhoria de 30-40% no tempo de carregamento',
                    implementation_effort='medium',
                    dependencies=[],
                    alternatives=[],
                    success_probability=0.8,
                    created_at=datetime.now().isoformat()
                )
            )
        
        elif industry == 'healthcare':
            recommendations.append(
                AIRecommendation(
                    id=str(uuid.uuid4()),
                    type='compliance',
                    title='Implementar Acessibilidade WCAG',
                    description='Garantir conformidade com padrões de acessibilidade para saúde',
                    confidence_score=0.95,
                    priority='critical',
                    category='compliance',
                    suggested_action={
                        'type': 'accessibility_audit',
                        'standards': ['WCAG_2.1_AA', 'Section_508']
                    },
                    reasoning='Acessibilidade é crítica e obrigatória na área da saúde',
                    expected_impact='Conformidade legal e melhor UX para todos',
                    implementation_effort='high',
                    dependencies=[],
                    alternatives=[],
                    success_probability=0.9,
                    created_at=datetime.now().isoformat()
                )
            )
        
        return recommendations
    
    async def _get_user_based_recommendations(self, user_patterns: UserBehaviorPattern,
                                            context: ProjectContext) -> List[AIRecommendation]:
        """Gera recomendações baseadas no usuário"""
        
        recommendations = []
        
        # Recomendações baseadas em criatividade
        if user_patterns.creativity_level > 0.7:
            recommendations.append(
                AIRecommendation(
                    id=str(uuid.uuid4()),
                    type='ai_generation',
                    title='Explorar Geração de Vídeo com IA',
                    description='Usar Veo 3 para criar conteúdo de vídeo único',
                    confidence_score=0.7,
                    priority='medium',
                    category='creative',
                    suggested_action={
                        'type': 'ai_generation',
                        'provider': 'veo3',
                        'content_type': 'video'
                    },
                    reasoning='Usuário demonstra alta criatividade e pode se beneficiar de ferramentas avançadas',
                    expected_impact='Conteúdo único e engajante',
                    implementation_effort='medium',
                    dependencies=[],
                    alternatives=[],
                    success_probability=0.6,
                    created_at=datetime.now().isoformat()
                )
            )
        
        # Recomendações baseadas em proficiência técnica
        if user_patterns.technical_proficiency > 0.8:
            recommendations.append(
                AIRecommendation(
                    id=str(uuid.uuid4()),
                    type='workflow',
                    title='Configurar Deploy Automático',
                    description='Implementar CI/CD com GitHub Actions e Vercel',
                    confidence_score=0.8,
                    priority='medium',
                    category='technical',
                    suggested_action={
                        'type': 'setup_cicd',
                        'platform': 'github_actions',
                        'deployment': 'vercel'
                    },
                    reasoning='Usuário tem proficiência técnica para aproveitar automação avançada',
                    expected_impact='Redução de 80% no tempo de deploy',
                    implementation_effort='high',
                    dependencies=['github_integration'],
                    alternatives=[],
                    success_probability=0.85,
                    created_at=datetime.now().isoformat()
                )
            )
        
        return recommendations
    
    async def _get_opportunity_recommendations(self, opportunities: List[str],
                                             context: ProjectContext) -> List[AIRecommendation]:
        """Gera recomendações baseadas em oportunidades"""
        
        recommendations = []
        
        for opportunity in opportunities[:3]:  # Top 3 oportunidades
            if 'IA' in opportunity or 'AI' in opportunity:
                recommendations.append(
                    AIRecommendation(
                        id=str(uuid.uuid4()),
                        type='ai_integration',
                        title='Integrar IA Personalizada',
                        description=opportunity,
                        confidence_score=0.75,
                        priority='medium',
                        category='innovation',
                        suggested_action={
                            'type': 'ai_integration',
                            'integration_type': 'personalization'
                        },
                        reasoning='Oportunidade identificada para diferenciação competitiva',
                        expected_impact='Diferenciação significativa no mercado',
                        implementation_effort='high',
                        dependencies=[],
                        alternatives=[],
                        success_probability=0.6,
                        created_at=datetime.now().isoformat()
                    )
                )
        
        return recommendations
    
    async def _prioritize_recommendations(self, recommendations: List[AIRecommendation],
                                        project_context: ProjectContext,
                                        user_patterns: UserBehaviorPattern) -> List[AIRecommendation]:
        """Prioriza recomendações baseado em contexto"""
        
        def calculate_priority_score(rec: AIRecommendation) -> float:
            score = rec.confidence_score * rec.success_probability
            
            # Ajustar baseado na prioridade
            priority_multipliers = {
                'critical': 2.0,
                'high': 1.5,
                'medium': 1.0,
                'low': 0.5
            }
            score *= priority_multipliers.get(rec.priority, 1.0)
            
            # Ajustar baseado no esforço de implementação
            effort_multipliers = {
                'low': 1.2,
                'medium': 1.0,
                'high': 0.8
            }
            score *= effort_multipliers.get(rec.implementation_effort, 1.0)
            
            # Ajustar baseado nas preferências do usuário
            if rec.category in ['creative', 'ai_content'] and user_patterns.creativity_level > 0.7:
                score *= 1.3
            
            if rec.category in ['technical', 'optimization'] and user_patterns.technical_proficiency > 0.7:
                score *= 1.3
            
            return score
        
        # Calcular scores e ordenar
        for rec in recommendations:
            rec.priority_score = calculate_priority_score(rec)
        
        return sorted(recommendations, key=lambda x: x.priority_score, reverse=True)
    
    async def _save_recommendation_history(self, project_id: str, user_id: str,
                                         recommendations: List[AIRecommendation]):
        """Salva histórico de recomendações"""
        
        history_key = f"{project_id}_{user_id}"
        
        if history_key not in self.recommendation_history:
            self.recommendation_history[history_key] = []
        
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'recommendations': [asdict(rec) for rec in recommendations],
            'context': {
                'project_id': project_id,
                'user_id': user_id
            }
        }
        
        self.recommendation_history[history_key].append(history_entry)
        
        # Manter apenas últimas 50 entradas
        if len(self.recommendation_history[history_key]) > 50:
            self.recommendation_history[history_key] = self.recommendation_history[history_key][-50:]
    
    async def _load_existing_data(self):
        """Carrega dados existentes"""
        # Carregar histórico de recomendações
        history_file = self.ai_dir / "recommendation_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.recommendation_history = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar histórico: {e}")
        
        # Carregar insights de aprendizado
        insights_file = self.ai_dir / "learning_insights.json"
        if insights_file.exists():
            try:
                with open(insights_file, 'r', encoding='utf-8') as f:
                    self.learning_insights = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar insights: {e}")
    
    async def _train_initial_models(self):
        """Treina modelos iniciais"""
        # Implementar treinamento de modelos de ML
        # Por enquanto, usar modelos pré-configurados
        pass
    
    async def _process_feedback(self, interaction_data: Dict):
        """Processa feedback do usuário"""
        feedback = interaction_data.get('feedback', {})
        
        # Analisar feedback e ajustar modelos
        if feedback.get('recommendation_helpful') is not None:
            # Atualizar confiança nas recomendações
            rec_id = feedback.get('recommendation_id')
            helpful = feedback.get('recommendation_helpful')
            
            # Implementar ajuste de confiança
            pass
    
    async def _detect_new_patterns(self, user_id: str):
        """Detecta novos padrões de comportamento"""
        # Analisar sessões recentes para novos padrões
        recent_sessions = self.behavior_analyzer.user_sessions[user_id][-50:]
        
        # Implementar detecção de padrões
        pass
    
    async def _update_learning_models(self, user_id: str):
        """Atualiza modelos de aprendizado"""
        # Retreinar modelos com novos dados
        pass
    
    def _matches_current_context(self, workflow: str, current_context: Dict) -> bool:
        """Verifica se workflow corresponde ao contexto atual"""
        workflow_keywords = workflow.lower().split(' -> ')
        context_stage = current_context.get('stage', '').lower()
        context_action = current_context.get('last_action', '').lower()
        
        return any(keyword in context_stage or keyword in context_action 
                  for keyword in workflow_keywords)
    
    def _predict_next_workflow_step(self, workflow: str) -> str:
        """Prediz próximo passo no workflow"""
        steps = workflow.split(' -> ')
        
        # Mapear próximos passos comuns
        next_step_map = {
            'design': 'code_generation',
            'code_generation': 'preview',
            'preview': 'optimization',
            'optimization': 'deployment',
            'ai_generation': 'integration',
            'integration': 'testing'
        }
        
        if len(steps) > 1:
            last_step = steps[-1].strip()
            return next_step_map.get(last_step, 'review')
        
        return 'continue_workflow'
    
    async def save_state(self):
        """Salva estado do sistema"""
        try:
            # Salvar histórico de recomendações
            history_file = self.ai_dir / "recommendation_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.recommendation_history, f, indent=2, ensure_ascii=False)
            
            # Salvar insights de aprendizado
            insights_file = self.ai_dir / "learning_insights.json"
            with open(insights_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_insights, f, indent=2, ensure_ascii=False)
            
            # Salvar sessões de usuário
            sessions_file = self.ai_dir / "user_sessions.pkl"
            with open(sessions_file, 'wb') as f:
                pickle.dump(dict(self.behavior_analyzer.user_sessions), f)
            
            print("💾 Estado do Context-Aware AI salvo")
            
        except Exception as e:
            print(f"❌ Erro ao salvar estado: {e}")
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Retorna analytics do sistema"""
        total_users = len(self.behavior_analyzer.user_sessions)
        total_sessions = sum(len(sessions) for sessions in self.behavior_analyzer.user_sessions.values())
        total_recommendations = sum(len(history) for history in self.recommendation_history.values())
        
        # Calcular métricas de engajamento
        avg_session_length = 0
        if total_sessions > 0:
            total_duration = 0
            session_count = 0
            
            for sessions in self.behavior_analyzer.user_sessions.values():
                for session in sessions:
                    duration = session.get('duration', 0)
                    if duration > 0:
                        total_duration += duration
                        session_count += 1
            
            if session_count > 0:
                avg_session_length = total_duration / session_count
        
        # Calcular distribuição de tipos de projeto
        project_types = defaultdict(int)
        for sessions in self.behavior_analyzer.user_sessions.values():
            for session in sessions:
                project_type = session.get('context', {}).get('project_type')
                if project_type:
                    project_types[project_type] += 1
        
        return {
            'system_metrics': {
                'total_users': total_users,
                'total_sessions': total_sessions,
                'total_recommendations': total_recommendations,
                'avg_session_length_minutes': round(avg_session_length / 60, 2) if avg_session_length > 0 else 0
            },
            'user_engagement': {
                'active_users_last_24h': self._count_active_users(24),
                'active_users_last_7d': self._count_active_users(24 * 7),
                'retention_rate': self._calculate_retention_rate()
            },
            'project_distribution': dict(project_types),
             'ai_usage_stats': self._get_ai_usage_stats(),
             'recommendation_effectiveness': self._calculate_recommendation_effectiveness()
         }
    
    def _count_active_users(self, hours: int) -> int:
        """Conta usuários ativos nas últimas N horas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        active_users = 0
        
        for sessions in self.behavior_analyzer.user_sessions.values():
            for session in sessions:
                session_time = datetime.fromisoformat(session['timestamp'])
                if session_time > cutoff_time:
                    active_users += 1
                    break
        
        return active_users
    
    def _calculate_retention_rate(self) -> float:
        """Calcula taxa de retenção"""
        if len(self.behavior_analyzer.user_sessions) < 2:
            return 0.0
        
        users_with_multiple_sessions = 0
        
        for sessions in self.behavior_analyzer.user_sessions.values():
            if len(sessions) > 1:
                users_with_multiple_sessions += 1
        
        return users_with_multiple_sessions / len(self.behavior_analyzer.user_sessions)
    
    def _get_ai_usage_stats(self) -> Dict[str, int]:
        """Obtém estatísticas de uso de IA"""
        ai_stats = defaultdict(int)
        
        for sessions in self.behavior_analyzer.user_sessions.values():
            for session in sessions:
                if session.get('type') == 'ai_generation':
                    ai_type = session.get('context', {}).get('ai_type', 'unknown')
                    ai_stats[ai_type] += 1
        
        return dict(ai_stats)
    
    def _calculate_recommendation_effectiveness(self) -> Dict[str, float]:
        """Calcula efetividade das recomendações"""
        total_recommendations = 0
        accepted_recommendations = 0
        
        for history in self.recommendation_history.values():
            for entry in history:
                recommendations = entry.get('recommendations', [])
                total_recommendations += len(recommendations)
                
                # Contar recomendações aceitas (implementar lógica de tracking)
                # Por enquanto, usar estimativa baseada em feedback
                accepted_recommendations += len(recommendations) * 0.6  # 60% estimado
        
        acceptance_rate = 0.0
        if total_recommendations > 0:
            acceptance_rate = accepted_recommendations / total_recommendations
        
        return {
            'total_recommendations': total_recommendations,
            'acceptance_rate': round(acceptance_rate, 3),
            'avg_recommendations_per_session': round(total_recommendations / max(1, len(self.recommendation_history)), 2)
        }

# Função principal para inicializar o sistema
async def initialize_context_aware_ai(project_dir: str = ".") -> ContextAwareAISystem:
    """Inicializa e retorna sistema de IA sensível ao contexto"""
    
    system = ContextAwareAISystem(project_dir)
    await system.initialize()
    
    return system

# Exemplo de uso
if __name__ == "__main__":
    async def main():
        # Inicializar sistema
        ai_system = await initialize_context_aware_ai()
        
        # Exemplo de projeto
        project_data = {
            'id': 'test_project_001',
            'project_type': 'landing_page',
            'description': 'Modern landing page for AI startup',
            'vibe_description': 'Innovative, trustworthy, cutting-edge technology',
            'target_audience': 'tech entrepreneurs',
            'brand_style': 'modern',
            'color_palette': ['#007bff', '#28a745']
        }
        
        user_id = 'user_001'
        
        # Gerar recomendações
        recommendations = await ai_system.analyze_project_and_generate_recommendations(
            project_data, user_id
        )
        
        print(f"\n🎯 Geradas {len(recommendations)} recomendações:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"{i}. {rec.title} (Confiança: {rec.confidence_score:.2f})")
            print(f"   {rec.description}")
            print(f"   Impacto esperado: {rec.expected_impact}\n")
        
        # Exemplo de enhancement de prompt
        original_prompt = "Create a hero section for a landing page"
        enhanced_prompt = await ai_system.enhance_prompt_with_context(
            original_prompt, project_data, user_id, 'image'
        )
        
        print(f"\n🚀 Prompt Original: {original_prompt}")
        print(f"\n✨ Prompt Enriquecido: {enhanced_prompt[:200]}...")
        
        # Simular interação
        interaction_data = {
            'user_id': user_id,
            'project_id': project_data['id'],
            'type': 'ai_generation',
            'action': 'generate_hero_image',
            'context': {
                'ai_type': 'dalle3',
                'project_type': 'landing_page',
                'style': 'modern'
            },
            'result': 'success',
            'satisfaction': 0.8,
            'duration': 45
        }
        
        await ai_system.learn_from_interaction(interaction_data)
        
        # Predições
        predictions = await ai_system.predict_user_needs(user_id, {
            'project_stage': 'design',
            'last_action': 'generate_image'
        })
        
        print(f"\n🔮 Predições para o usuário:")
        for pred in predictions:
            print(f"- {pred['prediction']} (Confiança: {pred['confidence']})")
        
        # Analytics
        analytics = await ai_system.get_system_analytics()
        print(f"\n📊 Analytics do Sistema:")
        print(f"- Usuários totais: {analytics['system_metrics']['total_users']}")
        print(f"- Sessões totais: {analytics['system_metrics']['total_sessions']}")
        print(f"- Taxa de retenção: {analytics['user_engagement']['retention_rate']:.2%}")
        
        # Salvar estado
        await ai_system.save_state()
        
        print("\n✅ Context-Aware AI System demonstrado com sucesso!")
    
    # Executar exemplo
    asyncio.run(main())