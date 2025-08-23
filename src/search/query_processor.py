import asyncio
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import openai

from config.config import RAGConfig

@dataclass
class ProcessedQuery:
    """Query processada com expansões e contexto"""
    original_query: str
    rewritten_query: str
    expanded_terms: List[str]
    intent: str  # 'implementation', 'documentation', 'example', 'troubleshooting'
    stack_context: List[str]
    category_context: List[str]
    confidence: float
    processing_time: float
    used_rewriting: bool

class QueryProcessor:
    """Processador de queries com rewriting inteligente usando GPT-5 Full"""
    
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        self.client = openai.AsyncOpenAI(api_key=api_key)
        
        # Configurações
        self.rewriting_model = RAGConfig.GPT5_FULL_MODEL
        self.rewriting_threshold = 0.7  # Confiança mínima para usar rewriting
        self.max_expanded_terms = 10
        
        # Cache de queries processadas
        self._query_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Padrões de detecção de intent
        self.intent_patterns = {
            'implementation': [
                r'como implementar',
                r'como fazer',
                r'implementação',
                r'código para',
                r'exemplo de código',
                r'tutorial'
            ],
            'documentation': [
                r'documentação',
                r'referência',
                r'api',
                r'propriedades',
                r'parâmetros',
                r'props'
            ],
            'example': [
                r'exemplo',
                r'sample',
                r'demo',
                r'showcase',
                r'template'
            ],
            'troubleshooting': [
                r'erro',
                r'problema',
                r'bug',
                r'não funciona',
                r'fix',
                r'solução'
            ]
        }
        
        # Contexto de stacks conhecidas
        self.stack_keywords = {
            'nextjs': ['next.js', 'nextjs', 'next', 'app router', 'pages router'],
            'react': ['react', 'jsx', 'tsx', 'component', 'hook', 'state'],
            'tailwind': ['tailwind', 'css', 'styling', 'classes', 'responsive'],
            'shadcn': ['shadcn', 'shadcn/ui', 'radix', 'ui components'],
            'prisma': ['prisma', 'orm', 'database', 'schema', 'migration'],
            'auth': ['auth', 'authentication', 'login', 'oauth', 'jwt', 'session']
        }
        
        # Contexto de categorias
        self.category_keywords = {
            'ui_components': ['component', 'button', 'form', 'input', 'dialog', 'modal'],
            'routing': ['route', 'navigation', 'link', 'redirect', 'middleware'],
            'data_fetching': ['fetch', 'api', 'swr', 'query', 'mutation', 'cache'],
            'styling': ['css', 'style', 'theme', 'design', 'layout', 'responsive'],
            'authentication': ['auth', 'login', 'user', 'session', 'permission'],
            'database': ['database', 'sql', 'query', 'model', 'schema', 'migration']
        }
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> ProcessedQuery:
        """Processa query com rewriting inteligente"""
        start_time = datetime.now()
        
        # Verifica cache
        cache_key = self._get_cache_key(query, context)
        if cache_key in self._query_cache:
            self._cache_hits += 1
            cached_result = self._query_cache[cache_key]
            self.logger.debug(f"Cache hit para query: {query[:50]}...")
            return cached_result
        
        self._cache_misses += 1
        
        try:
            # 1. Análise básica da query
            intent = self._detect_intent(query)
            stack_context = self._extract_stack_context(query)
            category_context = self._extract_category_context(query)
            
            # 2. Determina se precisa de rewriting
            needs_rewriting = self._should_rewrite_query(query, intent, stack_context)
            
            rewritten_query = query
            expanded_terms = []
            confidence = 1.0
            used_rewriting = False
            
            if needs_rewriting:
                # 3. Executa rewriting com GPT-5 Full
                rewrite_result = await self._rewrite_query_with_gpt5(query, intent, stack_context, category_context, context)
                
                if rewrite_result and rewrite_result['confidence'] >= self.rewriting_threshold:
                    rewritten_query = rewrite_result['rewritten_query']
                    expanded_terms = rewrite_result['expanded_terms']
                    confidence = rewrite_result['confidence']
                    used_rewriting = True
                    
                    self.logger.info(f"Query reescrita: '{query}' -> '{rewritten_query}'")
                else:
                    self.logger.debug(f"Rewriting rejeitado por baixa confiança: {rewrite_result.get('confidence', 0) if rewrite_result else 0}")
            
            # 4. Expande termos adicionais se não houve rewriting
            if not used_rewriting:
                expanded_terms = self._expand_query_terms(query, stack_context, category_context)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = ProcessedQuery(
                original_query=query,
                rewritten_query=rewritten_query,
                expanded_terms=expanded_terms[:self.max_expanded_terms],
                intent=intent,
                stack_context=stack_context,
                category_context=category_context,
                confidence=confidence,
                processing_time=processing_time,
                used_rewriting=used_rewriting
            )
            
            # Cache resultado
            self._query_cache[cache_key] = result
            
            # Limita tamanho do cache
            if len(self._query_cache) > 1000:
                # Remove 20% das entradas mais antigas
                old_keys = list(self._query_cache.keys())[:200]
                for key in old_keys:
                    del self._query_cache[key]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no processamento da query: {str(e)}")
            
            # Retorna resultado básico em caso de erro
            processing_time = (datetime.now() - start_time).total_seconds()
            return ProcessedQuery(
                original_query=query,
                rewritten_query=query,
                expanded_terms=[],
                intent='unknown',
                stack_context=[],
                category_context=[],
                confidence=0.5,
                processing_time=processing_time,
                used_rewriting=False
            )
    
    def _get_cache_key(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """Gera chave de cache para query"""
        context_str = json.dumps(context or {}, sort_keys=True)
        return f"{query.lower().strip()}|{context_str}"
    
    def _detect_intent(self, query: str) -> str:
        """Detecta intenção da query"""
        query_lower = query.lower()
        
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            intent_scores[intent] = score
        
        # Retorna intent com maior score, ou 'general' se empate
        if intent_scores:
            max_score = max(intent_scores.values())
            if max_score > 0:
                return max(intent_scores, key=intent_scores.get)
        
        return 'general'
    
    def _extract_stack_context(self, query: str) -> List[str]:
        """Extrai contexto de stack da query"""
        query_lower = query.lower()
        detected_stacks = []
        
        for stack, keywords in self.stack_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    if stack not in detected_stacks:
                        detected_stacks.append(stack)
                    break
        
        return detected_stacks
    
    def _extract_category_context(self, query: str) -> List[str]:
        """Extrai contexto de categoria da query"""
        query_lower = query.lower()
        detected_categories = []
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    if category not in detected_categories:
                        detected_categories.append(category)
                    break
        
        return detected_categories
    
    def _should_rewrite_query(self, query: str, intent: str, stack_context: List[str]) -> bool:
        """Determina se query deve ser reescrita"""
        # Queries muito curtas ou muito específicas não precisam de rewriting
        if len(query.split()) <= 2:
            return False
        
        # Queries já muito específicas não precisam de rewriting
        if len(stack_context) >= 2 and intent != 'general':
            return False
        
        # Queries ambíguas se beneficiam de rewriting
        if intent == 'general' or not stack_context:
            return True
        
        # Queries com termos técnicos vagos
        vague_terms = ['como', 'fazer', 'usar', 'implementar', 'criar', 'configurar']
        query_lower = query.lower()
        
        vague_count = sum(1 for term in vague_terms if term in query_lower)
        return vague_count >= 2
    
    async def _rewrite_query_with_gpt5(self, query: str, intent: str, 
                                       stack_context: List[str], 
                                       category_context: List[str],
                                       context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Reescreve query usando GPT-5 Full"""
        try:
            # Monta contexto para o prompt
            context_info = []
            
            if stack_context:
                context_info.append(f"Stacks detectadas: {', '.join(stack_context)}")
            
            if category_context:
                context_info.append(f"Categorias detectadas: {', '.join(category_context)}")
            
            if context:
                if 'current_stack' in context:
                    context_info.append(f"Stack atual do projeto: {context['current_stack']}")
                if 'current_task' in context:
                    context_info.append(f"Tarefa atual: {context['current_task']}")
            
            context_str = "\n".join(context_info) if context_info else "Nenhum contexto adicional."
            
            prompt = f"""Você é um especialista em desenvolvimento web com foco em Next.js, React, Tailwind CSS, Shadcn/UI e tecnologias relacionadas.

Sua tarefa é reescrever uma query de busca para torná-la mais específica e efetiva para encontrar documentação, exemplos e soluções relevantes.

Query original: "{query}"
Intenção detectada: {intent}
Contexto:
{context_str}

Reescreva a query para ser mais específica e incluir termos técnicos relevantes. A query reescrita deve:
1. Manter a intenção original
2. Adicionar termos técnicos específicos quando apropriado
3. Ser mais precisa para busca em documentação técnica
4. Incluir sinônimos e variações relevantes

Responda APENAS com um JSON no formato:
{{
  "rewritten_query": "query reescrita mais específica",
  "expanded_terms": ["termo1", "termo2", "termo3"],
  "confidence": 0.85,
  "reasoning": "breve explicação da reescrita"
}}"""
            
            response = await self.client.chat.completions.create(
                model=self.rewriting_model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em reescrita de queries para busca técnica. Responda sempre com JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extrai JSON da resposta
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Valida resultado
                if all(key in result for key in ['rewritten_query', 'expanded_terms', 'confidence']):
                    return result
                else:
                    self.logger.warning("Resposta do GPT-5 incompleta")
                    return None
            else:
                self.logger.warning("Não foi possível extrair JSON da resposta do GPT-5")
                return None
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao parsear JSON do GPT-5: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Erro no rewriting com GPT-5: {str(e)}")
            return None
    
    def _expand_query_terms(self, query: str, stack_context: List[str], 
                           category_context: List[str]) -> List[str]:
        """Expande termos da query sem usar GPT-5"""
        expanded = []
        query_lower = query.lower()
        
        # Adiciona sinônimos baseados no contexto de stack
        for stack in stack_context:
            if stack == 'nextjs':
                if 'component' in query_lower:
                    expanded.extend(['server component', 'client component', 'page component'])
                if 'route' in query_lower:
                    expanded.extend(['app router', 'api route', 'dynamic route'])
            
            elif stack == 'react':
                if 'state' in query_lower:
                    expanded.extend(['useState', 'useEffect', 'useContext'])
                if 'component' in query_lower:
                    expanded.extend(['functional component', 'jsx', 'props'])
            
            elif stack == 'tailwind':
                if 'style' in query_lower or 'css' in query_lower:
                    expanded.extend(['utility classes', 'responsive design', 'dark mode'])
            
            elif stack == 'shadcn':
                if 'component' in query_lower:
                    expanded.extend(['radix ui', 'accessible', 'customizable'])
        
        # Adiciona termos baseados na categoria
        for category in category_context:
            if category == 'ui_components':
                expanded.extend(['accessibility', 'props', 'styling', 'variants'])
            elif category == 'routing':
                expanded.extend(['navigation', 'params', 'query string', 'middleware'])
            elif category == 'data_fetching':
                expanded.extend(['loading', 'error handling', 'caching', 'revalidation'])
        
        # Remove duplicatas e termos já presentes na query
        query_words = set(query_lower.split())
        expanded = [term for term in expanded if term.lower() not in query_words]
        
        return list(set(expanded))  # Remove duplicatas
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de processamento"""
        total_queries = self._cache_hits + self._cache_misses
        cache_hit_rate = self._cache_hits / total_queries if total_queries > 0 else 0
        
        return {
            'total_queries_processed': total_queries,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self._query_cache)
        }
    
    def clear_cache(self):
        """Limpa cache de queries"""
        self._query_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self.logger.info("Cache de queries limpo")