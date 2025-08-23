import openai
import json
import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from config.config import RAGConfig

@dataclass
class RationaleResult:
    """Resultado da geração de rationale"""
    rationale: str
    confidence: float
    reasoning_type: str  # 'relevance', 'quality', 'completeness', 'applicability'
    key_points: List[str]
    limitations: List[str]
    generated_at: str

class RationaleGenerator:
    """Gerador de explicações (rationales) para resultados de busca"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuração OpenAI
        openai.api_key = RAGConfig.OPENAI_API_KEY
        
        # Templates de rationale por tipo
        self.rationale_templates = {
            'relevance': {
                'prompt_focus': 'relevância direta para a consulta',
                'key_aspects': ['correspondência de termos', 'contexto semântico', 'aplicabilidade']
            },
            'quality': {
                'prompt_focus': 'qualidade e confiabilidade da informação',
                'key_aspects': ['completude', 'precisão técnica', 'fonte autorizada']
            },
            'completeness': {
                'prompt_focus': 'completude e profundidade da informação',
                'key_aspects': ['cobertura do tópico', 'exemplos práticos', 'detalhamento']
            },
            'applicability': {
                'prompt_focus': 'aplicabilidade prática para desenvolvimento',
                'key_aspects': ['implementação', 'casos de uso', 'compatibilidade']
            }
        }
        
        # Cache para rationales
        self._rationale_cache = {}
        
        # Estatísticas
        self._stats = {
            'total_generated': 0,
            'cache_hits': 0,
            'avg_generation_time': 0,
            'total_generation_time': 0,
            'by_type': {
                'relevance': 0,
                'quality': 0,
                'completeness': 0,
                'applicability': 0
            }
        }
        
        self.logger.info("RationaleGenerator inicializado")
    
    def generate_rationale(self, query: str, result: Dict[str, Any], 
                          rationale_type: str = 'relevance',
                          context: Optional[Dict[str, Any]] = None) -> RationaleResult:
        """Gera rationale para um resultado específico"""
        start_time = time.time()
        
        try:
            # Valida tipo de rationale
            if rationale_type not in self.rationale_templates:
                rationale_type = 'relevance'
            
            # Gera chave de cache
            cache_key = self._generate_cache_key(query, result, rationale_type)
            
            # Verifica cache
            if cache_key in self._rationale_cache:
                self._stats['cache_hits'] += 1
                return self._rationale_cache[cache_key]
            
            # Gera rationale
            rationale_result = self._generate_rationale_with_gpt5(
                query, result, rationale_type, context
            )
            
            # Atualiza cache
            self._rationale_cache[cache_key] = rationale_result
            
            # Atualiza estatísticas
            generation_time = time.time() - start_time
            self._update_stats(rationale_type, generation_time)
            
            return rationale_result
        
        except Exception as e:
            self.logger.error(f"Erro ao gerar rationale: {str(e)}")
            # Retorna rationale básico em caso de erro
            return self._generate_fallback_rationale(query, result, rationale_type)
    
    def generate_batch_rationales(self, query: str, results: List[Dict[str, Any]],
                                 rationale_type: str = 'relevance',
                                 context: Optional[Dict[str, Any]] = None) -> List[RationaleResult]:
        """Gera rationales para múltiplos resultados em lote"""
        try:
            self.logger.info(f"Gerando rationales em lote para {len(results)} resultados")
            
            rationales = []
            
            # Processa em lotes menores para otimizar
            batch_size = 3
            for i in range(0, len(results), batch_size):
                batch = results[i:i + batch_size]
                batch_rationales = self._generate_batch_with_gpt5(
                    query, batch, rationale_type, context
                )
                rationales.extend(batch_rationales)
            
            return rationales
        
        except Exception as e:
            self.logger.error(f"Erro ao gerar rationales em lote: {str(e)}")
            # Gera rationales individuais como fallback
            return [
                self.generate_rationale(query, result, rationale_type, context)
                for result in results
            ]
    
    def _generate_rationale_with_gpt5(self, query: str, result: Dict[str, Any],
                                     rationale_type: str, context: Optional[Dict[str, Any]]) -> RationaleResult:
        """Gera rationale usando GPT-5 Full"""
        try:
            # Constrói prompt
            prompt = self._build_rationale_prompt(query, result, rationale_type, context)
            
            # Chama GPT-5
            response = self._call_gpt5_for_rationale(prompt)
            
            # Processa resposta
            return self._parse_rationale_response(response, rationale_type)
        
        except Exception as e:
            self.logger.error(f"Erro na geração com GPT-5: {str(e)}")
            raise
    
    def _build_rationale_prompt(self, query: str, result: Dict[str, Any],
                               rationale_type: str, context: Optional[Dict[str, Any]]) -> str:
        """Constrói prompt para geração de rationale"""
        template = self.rationale_templates[rationale_type]
        
        # Informações do resultado
        chunk = result.get('chunk', '')[:800]  # Limita tamanho
        fonte = result.get('fonte', {})
        metadata = result.get('metadata', {})
        score = result.get('score', 0)
        
        # Contexto adicional
        context_info = ""
        if context:
            stack = context.get('stack', '')
            categoria = context.get('categoria', '')
            if stack or categoria:
                context_info = f"\nContexto do projeto: Stack={stack}, Categoria={categoria}"
        
        prompt = f"""Você é um especialista em desenvolvimento web que precisa explicar por que um resultado de busca é relevante para um desenvolvedor.

QUERY: "{query}"{context_info}

RESULTADO PARA ANALISAR:
Fonte: {fonte.get('title', 'N/A')} ({fonte.get('url', 'N/A')})
Stack: {metadata.get('stack', 'N/A')}
Categoria: {metadata.get('categoria', 'N/A')}
Score: {score:.3f}
Conteúdo: {chunk}

FOCO DA ANÁLISE: {template['prompt_focus']}

ASPECTOS A CONSIDERAR:
{chr(10).join(f'- {aspect}' for aspect in template['key_aspects'])}

TAREFA:
Gere uma explicação concisa (máximo 100 palavras) explicando por que este resultado é útil para a query do desenvolvedor.

RESPONDA EM JSON:
{{
  "rationale": "Explicação clara e concisa",
  "confidence": 0.85,
  "key_points": ["Ponto 1", "Ponto 2", "Ponto 3"],
  "limitations": ["Limitação 1", "Limitação 2"]
}}

DIRETRIZES:
- Seja específico e prático
- Foque no valor para o desenvolvedor
- Mencione aspectos técnicos relevantes
- Seja honesto sobre limitações
- Use linguagem clara e direta"""
        
        return prompt
    
    def _call_gpt5_for_rationale(self, prompt: str) -> str:
        """Chama GPT-5 Full para geração de rationale"""
        try:
            response = openai.chat.completions.create(
                model=RAGConfig.GPT5_FULL_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em desenvolvimento web. Forneça análises precisas e práticas em JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            self.logger.error(f"Erro na chamada GPT-5 para rationale: {str(e)}")
            raise
    
    def _parse_rationale_response(self, response: str, rationale_type: str) -> RationaleResult:
        """Processa resposta do GPT-5 para rationale"""
        try:
            data = json.loads(response)
            
            # Valida campos obrigatórios
            rationale = data.get('rationale', 'Rationale não disponível')
            confidence = data.get('confidence', 0.5)
            key_points = data.get('key_points', [])
            limitations = data.get('limitations', [])
            
            # Valida confidence
            confidence = max(0, min(1, confidence))
            
            # Limita tamanho dos arrays
            key_points = key_points[:5] if isinstance(key_points, list) else []
            limitations = limitations[:3] if isinstance(limitations, list) else []
            
            return RationaleResult(
                rationale=rationale,
                confidence=confidence,
                reasoning_type=rationale_type,
                key_points=key_points,
                limitations=limitations,
                generated_at=datetime.now().isoformat()
            )
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao parsear JSON do rationale: {str(e)}")
            return self._generate_fallback_rationale_result(rationale_type)
        
        except Exception as e:
            self.logger.error(f"Erro ao processar resposta do rationale: {str(e)}")
            return self._generate_fallback_rationale_result(rationale_type)
    
    def _generate_batch_with_gpt5(self, query: str, results: List[Dict[str, Any]],
                                 rationale_type: str, context: Optional[Dict[str, Any]]) -> List[RationaleResult]:
        """Gera rationales em lote usando GPT-5"""
        try:
            # Constrói prompt para lote
            prompt = self._build_batch_rationale_prompt(query, results, rationale_type, context)
            
            # Chama GPT-5
            response = self._call_gpt5_for_rationale(prompt)
            
            # Processa resposta
            return self._parse_batch_rationale_response(response, rationale_type, len(results))
        
        except Exception as e:
            self.logger.error(f"Erro na geração em lote: {str(e)}")
            # Fallback para geração individual
            return [
                self.generate_rationale(query, result, rationale_type, context)
                for result in results
            ]
    
    def _build_batch_rationale_prompt(self, query: str, results: List[Dict[str, Any]],
                                     rationale_type: str, context: Optional[Dict[str, Any]]) -> str:
        """Constrói prompt para geração em lote"""
        template = self.rationale_templates[rationale_type]
        
        # Contexto
        context_info = ""
        if context:
            stack = context.get('stack', '')
            categoria = context.get('categoria', '')
            if stack or categoria:
                context_info = f"\nContexto: Stack={stack}, Categoria={categoria}"
        
        # Resultados
        results_text = ""
        for i, result in enumerate(results):
            chunk = result.get('chunk', '')[:400]  # Menor para lote
            fonte = result.get('fonte', {})
            score = result.get('score', 0)
            
            results_text += f"\n[{i}] Score: {score:.3f}\n"
            results_text += f"Fonte: {fonte.get('title', 'N/A')}\n"
            results_text += f"Conteúdo: {chunk}\n"
        
        prompt = f"""Gere rationales para múltiplos resultados de busca.

QUERY: "{query}"{context_info}

FOCO: {template['prompt_focus']}

RESULTADOS:{results_text}

RESPONDA EM JSON:
{{
  "rationales": [
    {{
      "index": 0,
      "rationale": "Explicação concisa",
      "confidence": 0.85,
      "key_points": ["Ponto 1", "Ponto 2"],
      "limitations": ["Limitação 1"]
    }}
  ]
}}

Gere um rationale para cada resultado (máximo 80 palavras cada)."""
        
        return prompt
    
    def _parse_batch_rationale_response(self, response: str, rationale_type: str, 
                                       expected_count: int) -> List[RationaleResult]:
        """Processa resposta em lote do GPT-5"""
        try:
            data = json.loads(response)
            rationales_data = data.get('rationales', [])
            
            results = []
            for item in rationales_data:
                rationale = item.get('rationale', 'Rationale não disponível')
                confidence = max(0, min(1, item.get('confidence', 0.5)))
                key_points = item.get('key_points', [])[:5]
                limitations = item.get('limitations', [])[:3]
                
                results.append(RationaleResult(
                    rationale=rationale,
                    confidence=confidence,
                    reasoning_type=rationale_type,
                    key_points=key_points,
                    limitations=limitations,
                    generated_at=datetime.now().isoformat()
                ))
            
            # Preenche resultados faltantes se necessário
            while len(results) < expected_count:
                results.append(self._generate_fallback_rationale_result(rationale_type))
            
            return results[:expected_count]
        
        except Exception as e:
            self.logger.error(f"Erro ao processar lote de rationales: {str(e)}")
            # Retorna fallbacks
            return [
                self._generate_fallback_rationale_result(rationale_type)
                for _ in range(expected_count)
            ]
    
    def _generate_fallback_rationale(self, query: str, result: Dict[str, Any], 
                                   rationale_type: str) -> RationaleResult:
        """Gera rationale básico como fallback"""
        fonte = result.get('fonte', {})
        metadata = result.get('metadata', {})
        score = result.get('score', 0)
        
        # Rationale básico baseado em metadados
        rationale_parts = []
        
        if score > 0.8:
            rationale_parts.append("Alta relevância para a consulta")
        elif score > 0.6:
            rationale_parts.append("Boa relevância para a consulta")
        else:
            rationale_parts.append("Relevância moderada para a consulta")
        
        stack = metadata.get('stack', '')
        if stack:
            rationale_parts.append(f"Específico para {stack}")
        
        categoria = metadata.get('categoria', '')
        if categoria:
            rationale_parts.append(f"Categoria: {categoria}")
        
        fonte_title = fonte.get('title', '')
        if fonte_title:
            rationale_parts.append(f"Fonte: {fonte_title}")
        
        rationale = ". ".join(rationale_parts) + "."
        
        return RationaleResult(
            rationale=rationale,
            confidence=0.5,
            reasoning_type=rationale_type,
            key_points=["Análise baseada em metadados"],
            limitations=["Rationale gerado automaticamente"],
            generated_at=datetime.now().isoformat()
        )
    
    def _generate_fallback_rationale_result(self, rationale_type: str) -> RationaleResult:
        """Gera resultado de rationale básico"""
        return RationaleResult(
            rationale="Rationale não disponível devido a erro no processamento",
            confidence=0.3,
            reasoning_type=rationale_type,
            key_points=[],
            limitations=["Processamento com erro"],
            generated_at=datetime.now().isoformat()
        )
    
    def _generate_cache_key(self, query: str, result: Dict[str, Any], rationale_type: str) -> str:
        """Gera chave de cache para rationale"""
        import hashlib
        
        chunk_id = result.get('metadata', {}).get('chunk_id', '')
        score = result.get('score', 0)
        
        cache_string = f"{query.lower().strip()}|{chunk_id}|{score:.3f}|{rationale_type}"
        
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()[:16]
    
    def _update_stats(self, rationale_type: str, generation_time: float):
        """Atualiza estatísticas"""
        self._stats['total_generated'] += 1
        self._stats['total_generation_time'] += generation_time
        self._stats['avg_generation_time'] = (
            self._stats['total_generation_time'] / self._stats['total_generated']
        )
        self._stats['by_type'][rationale_type] += 1
    
    def get_rationale_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de geração de rationales"""
        return self._stats.copy()
    
    def clear_cache(self):
        """Limpa cache de rationales"""
        self._rationale_cache.clear()
        self.logger.info("Cache de rationales limpo")
    
    def get_cache_size(self) -> int:
        """Retorna tamanho do cache"""
        return len(self._rationale_cache)