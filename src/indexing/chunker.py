import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

# Import tiktoken with fallback
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None
    print("Warning: tiktoken not available. Some features may be limited.")

from config.config import RAGConfig

@dataclass
class Chunk:
    """Representa um chunk de conteúdo"""
    id: str
    content: str
    tokens: int
    start_char: int
    end_char: int
    section_title: str
    section_type: str
    metadata: Dict[str, Any]
    overlap_with_previous: bool = False
    overlap_with_next: bool = False

class ContentChunker:
    """Chunker de conteúdo para o sistema RAG"""
    
    def __init__(self, model_name: str = "gpt-4"):
        self.logger = logging.getLogger(__name__)
        
        # Configurações de chunking
        self.min_chunk_size = RAGConfig.CHUNK_SIZE_MIN
        self.max_chunk_size = RAGConfig.CHUNK_SIZE_MAX
        self.overlap_percent = RAGConfig.CHUNK_OVERLAP_PERCENT
        
        # Tokenizer
        self.tokenizer = None
        if TIKTOKEN_AVAILABLE and tiktoken is not None:
            try:
                self.tokenizer = tiktoken.encoding_for_model(model_name)
            except KeyError:
                self.logger.warning(f"Modelo {model_name} não encontrado, usando cl100k_base")
                try:
                    self.tokenizer = tiktoken.get_encoding("cl100k_base")
                except Exception as e:
                    self.logger.error(f"Erro ao inicializar tiktoken: {e}")
                    self.tokenizer = None
        else:
            self.logger.warning("tiktoken não disponível, usando contagem aproximada de tokens")
        
        # Padrões para quebra de texto
        self.sentence_endings = r'[.!?]\s+'
        self.paragraph_breaks = r'\n\s*\n'
        self.section_breaks = r'\n#{1,6}\s+'
        
        # Prioridades de quebra (maior = melhor lugar para quebrar)
        self.break_priorities = {
            'section': 100,
            'paragraph': 80,
            'sentence': 60,
            'word': 20,
            'character': 1
        }
    
    def _count_tokens(self, text: str) -> int:
        """Conta tokens no texto, com fallback se tiktoken não estiver disponível"""
        if self.tokenizer is not None:
            try:
                return len(self.tokenizer.encode(text))
            except Exception as e:
                self.logger.warning(f"Erro ao contar tokens com tiktoken: {e}")
        
        # Fallback: estimativa aproximada (1 token ≈ 4 caracteres)
        return max(1, len(text) // 4)
    
    def chunk_content(self, content: Dict[str, Any]) -> List[Chunk]:
        """Chunka conteúdo completo em pedaços menores"""
        try:
            self.logger.info(f"Chunkando conteúdo: {content.get('title', 'Sem título')}")
            
            all_chunks = []
            
            # Processa cada seção
            for section in content.get('sections', []):
                section_chunks = self._chunk_section(section, content['metadata'])
                all_chunks.extend(section_chunks)
            
            # Se não há seções, chunka o conteúdo bruto
            if not all_chunks and 'raw_html' in content:
                raw_chunks = self._chunk_raw_content(
                    content['raw_html'], 
                    content['metadata']
                )
                all_chunks.extend(raw_chunks)
            
            # Adiciona overlaps entre chunks
            all_chunks = self._add_overlaps(all_chunks)
            
            # Gera IDs únicos
            all_chunks = self._generate_chunk_ids(all_chunks, content)
            
            self.logger.info(f"Gerados {len(all_chunks)} chunks")
            return all_chunks
            
        except Exception as e:
            self.logger.error(f"Erro ao chunkar conteúdo: {str(e)}")
            return []
    
    def _chunk_section(self, section: Dict[str, Any], base_metadata: Dict[str, Any]) -> List[Chunk]:
        """Chunka uma seção individual"""
        content_text = section.get('content', '')
        section_title = section.get('title', 'Sem título')
        section_type = section.get('section_type', 'general')
        
        if not content_text or len(content_text.strip()) < 50:
            return []
        
        # Combina metadados
        chunk_metadata = base_metadata.copy()
        chunk_metadata.update({
            'section_title': section_title,
            'section_type': section_type,
            'importance_score': section.get('importance_score', 0.5),
            'has_code': len(section.get('code_blocks', [])) > 0,
            'has_links': len(section.get('links', [])) > 0
        })
        
        # Chunka o texto
        chunks = self._split_text_into_chunks(
            content_text, 
            section_title, 
            section_type, 
            chunk_metadata
        )
        
        return chunks
    
    def _chunk_raw_content(self, raw_content: str, base_metadata: Dict[str, Any]) -> List[Chunk]:
        """Chunka conteúdo bruto quando não há seções estruturadas"""
        return self._split_text_into_chunks(
            raw_content,
            "Conteúdo Principal",
            "general",
            base_metadata
        )
    
    def _split_text_into_chunks(self, text: str, section_title: str, 
                               section_type: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Divide texto em chunks respeitando limites de tokens"""
        chunks = []
        
        # Conta tokens do texto completo
        total_tokens = self._count_tokens(text)
        
        if total_tokens <= self.max_chunk_size:
            # Texto cabe em um chunk
            chunk = Chunk(
                id="",  # Será gerado depois
                content=text,
                tokens=total_tokens,
                start_char=0,
                end_char=len(text),
                section_title=section_title,
                section_type=section_type,
                metadata=metadata.copy()
            )
            return [chunk]
        
        # Precisa dividir em múltiplos chunks
        if self.tokenizer is not None:
            # Usa tokenização precisa
            return self._split_with_tokenizer(text, section_title, section_type, metadata)
        else:
            # Usa fallback baseado em caracteres
            return self._split_with_char_fallback(text, section_title, section_type, metadata)
    
    def _split_with_tokenizer(self, text: str, section_title: str, section_type: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Divide texto usando tokenização precisa"""
        chunks = []
        tokens = self.tokenizer.encode(text)
        total_tokens = len(tokens)
        current_pos = 0
        
        while current_pos < total_tokens:
            chunk_size = min(self.max_chunk_size, total_tokens - current_pos)
            
            if chunk_size < self.min_chunk_size and current_pos > 0:
                if chunks:
                    last_chunk = chunks[-1]
                    remaining_text = text[last_chunk.end_char:]
                    last_chunk.content += remaining_text
                    last_chunk.tokens = self._count_tokens(last_chunk.content)
                    last_chunk.end_char = len(text)
                break
            
            end_pos = current_pos + chunk_size
            break_pos = self._find_best_break_point_tokenized(text, tokens, current_pos, end_pos)
            
            chunk_tokens = tokens[current_pos:break_pos]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            start_char = len(self.tokenizer.decode(tokens[:current_pos]))
            end_char = len(self.tokenizer.decode(tokens[:break_pos]))
            
            chunk = Chunk(
                id="",
                content=chunk_text.strip(),
                tokens=len(chunk_tokens),
                start_char=start_char,
                end_char=end_char,
                section_title=section_title,
                section_type=section_type,
                metadata=metadata.copy()
            )
            
            chunks.append(chunk)
            current_pos = break_pos
        
        return chunks
    
    def _split_with_char_fallback(self, text: str, section_title: str, section_type: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Divide texto usando fallback baseado em caracteres"""
        chunks = []
        # Estima caracteres por chunk (4 chars ≈ 1 token)
        chars_per_chunk = self.max_chunk_size * 4
        current_pos = 0
        
        while current_pos < len(text):
            end_pos = min(current_pos + chars_per_chunk, len(text))
            
            # Procura por quebra natural
            if end_pos < len(text):
                # Procura por quebra de parágrafo
                para_break = text.rfind('\n\n', current_pos, end_pos)
                if para_break > current_pos:
                    end_pos = para_break + 2
                else:
                    # Procura por quebra de sentença
                    sent_break = max(
                        text.rfind('. ', current_pos, end_pos),
                        text.rfind('! ', current_pos, end_pos),
                        text.rfind('? ', current_pos, end_pos)
                    )
                    if sent_break > current_pos:
                        end_pos = sent_break + 2
                    else:
                        # Procura por espaço
                        space_break = text.rfind(' ', current_pos, end_pos)
                        if space_break > current_pos:
                            end_pos = space_break + 1
            
            chunk_text = text[current_pos:end_pos].strip()
            if chunk_text:
                chunk = Chunk(
                    id="",
                    content=chunk_text,
                    tokens=self._count_tokens(chunk_text),
                    start_char=current_pos,
                    end_char=end_pos,
                    section_title=section_title,
                    section_type=section_type,
                    metadata=metadata.copy()
                )
                chunks.append(chunk)
            
            current_pos = end_pos
        
        return chunks
    
    def _find_best_break_point_tokenized(self, text: str, tokens: List[int], 
                              start_pos: int, end_pos: int) -> int:
        """Encontra o melhor ponto para quebrar o texto"""
        # Se estamos no final, retorna a posição final
        if end_pos >= len(tokens):
            return len(tokens)
        
        # Converte posições de token para posições de caractere
        start_char = len(self.tokenizer.decode(tokens[:start_pos]))
        end_char = len(self.tokenizer.decode(tokens[:end_pos]))
        
        # Texto da região onde procuramos o ponto de quebra
        search_text = text[start_char:end_char]
        
        # Procura por diferentes tipos de quebra
        break_candidates = []
        
        # 1. Quebras de seção (headers markdown)
        section_matches = list(re.finditer(self.section_breaks, search_text))
        for match in section_matches:
            char_pos = start_char + match.start()
            token_pos = self._char_to_token_pos(text, tokens, char_pos)
            if start_pos < token_pos < end_pos:
                break_candidates.append((token_pos, self.break_priorities['section']))
        
        # 2. Quebras de parágrafo
        paragraph_matches = list(re.finditer(self.paragraph_breaks, search_text))
        for match in paragraph_matches:
            char_pos = start_char + match.start()
            token_pos = self._char_to_token_pos(text, tokens, char_pos)
            if start_pos < token_pos < end_pos:
                break_candidates.append((token_pos, self.break_priorities['paragraph']))
        
        # 3. Quebras de sentença
        sentence_matches = list(re.finditer(self.sentence_endings, search_text))
        for match in sentence_matches:
            char_pos = start_char + match.end()
            token_pos = self._char_to_token_pos(text, tokens, char_pos)
            if start_pos < token_pos < end_pos:
                break_candidates.append((token_pos, self.break_priorities['sentence']))
        
        # 4. Quebras de palavra (espaços)
        word_matches = list(re.finditer(r'\s+', search_text))
        for match in word_matches:
            char_pos = start_char + match.start()
            token_pos = self._char_to_token_pos(text, tokens, char_pos)
            if start_pos < token_pos < end_pos:
                break_candidates.append((token_pos, self.break_priorities['word']))
        
        # Escolhe o melhor candidato
        if break_candidates:
            # Ordena por prioridade (maior primeiro) e proximidade ao final
            break_candidates.sort(key=lambda x: (x[1], -abs(x[0] - end_pos)), reverse=True)
            return break_candidates[0][0]
        
        # Se não encontrou nenhum bom ponto, quebra no limite
        return end_pos
    
    def _char_to_token_pos(self, text: str, tokens: List[int], char_pos: int) -> int:
        """Converte posição de caractere para posição de token"""
        if self.tokenizer and TIKTOKEN_AVAILABLE:
            # Aproximação: tokeniza até a posição do caractere
            text_until_pos = text[:char_pos]
            tokens_until_pos = self.tokenizer.encode(text_until_pos)
            return len(tokens_until_pos)
        else:
            # Fallback: estimativa baseada em caracteres
            return int(char_pos / 4)  # Aproximação: 4 chars por token
    
    def _add_overlaps(self, chunks: List[Chunk]) -> List[Chunk]:
        """Adiciona overlaps entre chunks consecutivos"""
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            new_chunk = chunk
            
            # Adiciona overlap com chunk anterior
            if i > 0:
                prev_chunk = chunks[i-1]
                overlap_size = int(prev_chunk.tokens * self.overlap_percent)
                
                if overlap_size > 0:
                    if self.tokenizer and TIKTOKEN_AVAILABLE:
                        # Pega tokens do final do chunk anterior
                        prev_tokens = self.tokenizer.encode(prev_chunk.content)
                        overlap_tokens = prev_tokens[-overlap_size:]
                        overlap_text = self.tokenizer.decode(overlap_tokens)
                    else:
                        # Fallback: usa caracteres em vez de tokens
                        char_overlap = int(len(prev_chunk.content) * self.overlap_percent)
                        overlap_text = prev_chunk.content[-char_overlap:]
                    
                    # Adiciona ao início do chunk atual
                    new_content = overlap_text + " " + chunk.content
                    new_chunk = Chunk(
                        id=chunk.id,
                        content=new_content,
                        tokens=self._count_tokens(new_content),
                        start_char=chunk.start_char,
                        end_char=chunk.end_char,
                        section_title=chunk.section_title,
                        section_type=chunk.section_type,
                        metadata=chunk.metadata,
                        overlap_with_previous=True
                    )
            
            # Marca overlap com próximo chunk
            if i < len(chunks) - 1:
                new_chunk.overlap_with_next = True
            
            overlapped_chunks.append(new_chunk)
        
        return overlapped_chunks
    
    def _generate_chunk_ids(self, chunks: List[Chunk], content: Dict[str, Any]) -> List[Chunk]:
        """Gera IDs únicos para os chunks"""
        base_url = content.get('url', 'unknown')
        url_hash = str(hash(base_url))[-8:]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, chunk in enumerate(chunks):
            chunk.id = f"{url_hash}_{timestamp}_{i:03d}"
            
            # Adiciona informações do chunk aos metadados
            chunk.metadata.update({
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_id': chunk.id,
                'created_at': datetime.now().isoformat()
            })
        
        return chunks
    
    def get_chunk_stats(self, chunks: List[Chunk]) -> Dict[str, Any]:
        """Retorna estatísticas dos chunks gerados"""
        if not chunks:
            return {}
        
        token_counts = [chunk.tokens for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'total_tokens': sum(token_counts),
            'avg_tokens_per_chunk': sum(token_counts) / len(chunks),
            'min_tokens': min(token_counts),
            'max_tokens': max(token_counts),
            'chunks_with_overlap': sum(1 for c in chunks if c.overlap_with_previous or c.overlap_with_next),
            'section_types': list(set(c.section_type for c in chunks)),
            'chunks_with_code': sum(1 for c in chunks if c.metadata.get('has_code', False)),
            'chunks_with_links': sum(1 for c in chunks if c.metadata.get('has_links', False))
        }
    
    def chunk_batch(self, contents: List[Dict[str, Any]]) -> List[List[Chunk]]:
        """Chunka múltiplos conteúdos em lote"""
        all_chunks = []
        
        for i, content in enumerate(contents):
            try:
                chunks = self.chunk_content(content)
                all_chunks.append(chunks)
                self.logger.debug(f"Chunkado {i+1}/{len(contents)}: {len(chunks)} chunks")
                
            except Exception as e:
                self.logger.error(f"Erro ao chunkar conteúdo {i+1}: {str(e)}")
                all_chunks.append([])
        
        total_chunks = sum(len(chunks) for chunks in all_chunks)
        self.logger.info(f"Chunking em lote concluído: {total_chunks} chunks de {len(contents)} conteúdos")
        
        return all_chunks