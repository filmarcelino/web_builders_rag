import sqlite3
import json
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
import logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
import string
import unicodedata

from config.config import RAGConfig
from .chunker import Chunk
from .vector_indexer import IndexedChunk

@dataclass
class TextSearchResult:
    """Resultado de busca textual"""
    chunk_id: str
    content: str
    score: float
    matched_terms: List[str]
    metadata: Dict[str, Any]
    highlights: List[str]

class TextIndexer:
    """Indexador de texto para busca por palavras-chave"""
    
    def __init__(self, index_dir: str):
        self.logger = logging.getLogger(__name__)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivos do índice
        self.text_db_path = self.index_dir / "text_index.db"
        self.stopwords_path = self.index_dir / "stopwords.json"
        
        # Conexão SQLite
        self.db_conn = None
        
        # Stopwords (palavras comuns a ignorar)
        self.stopwords = self._load_stopwords()
        
        # Configurações de busca
        self.min_term_length = 2
        self.max_term_length = 50
        
        # Estatísticas
        self.stats = {
            'total_documents': 0,
            'total_terms': 0,
            'unique_terms': 0,
            'search_count': 0,
            'avg_search_time': 0
        }
        
        # Inicializa índice
        self._initialize_index()
    
    def _load_stopwords(self) -> Set[str]:
        """Carrega stopwords em português e inglês"""
        default_stopwords = {
            # Português
            'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'até', 'com', 'como',
            'da', 'das', 'de', 'dela', 'delas', 'dele', 'deles', 'depois', 'do', 'dos', 'e', 'ela', 'elas',
            'ele', 'eles', 'em', 'entre', 'essa', 'essas', 'esse', 'esses', 'esta', 'estas', 'este', 'estes',
            'eu', 'isso', 'isto', 'já', 'lhe', 'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu', 'meus', 'minha',
            'minhas', 'muito', 'na', 'nas', 'não', 'no', 'nos', 'nós', 'nossa', 'nossas', 'nosso', 'nossos',
            'num', 'numa', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos', 'por', 'qual', 'quando',
            'que', 'quem', 'se', 'sem', 'seu', 'seus', 'só', 'sua', 'suas', 'também', 'te', 'tem', 'tu', 'tua',
            'tuas', 'tudo', 'um', 'uma', 'umas', 'uns', 'você', 'vocês', 'vos',
            
            # Inglês
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it',
            'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'up', 'out',
            'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him',
            'time', 'two', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who',
            'oil', 'sit', 'now', 'find', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'
        }
        
        try:
            if self.stopwords_path.exists():
                with open(self.stopwords_path, 'r', encoding='utf-8') as f:
                    custom_stopwords = set(json.load(f))
                return default_stopwords.union(custom_stopwords)
        except Exception as e:
            self.logger.warning(f"Erro ao carregar stopwords customizadas: {str(e)}")
        
        return default_stopwords
    
    def _initialize_index(self):
        """Inicializa o índice de texto SQLite"""
        try:
            self.db_conn = sqlite3.connect(str(self.text_db_path), check_same_thread=False)
            self.db_conn.row_factory = sqlite3.Row
            
            # Habilita FTS (Full Text Search) do SQLite
            self.db_conn.execute('PRAGMA journal_mode=WAL')
            
            # Tabela principal de documentos
            self.db_conn.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    chunk_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    processed_content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    indexed_at TEXT NOT NULL,
                    section_title TEXT,
                    section_type TEXT,
                    source_url TEXT,
                    stack TEXT,
                    category TEXT,
                    language TEXT,
                    quality_score REAL
                )
            ''')
            
            # Tabela FTS para busca de texto completo
            self.db_conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    chunk_id,
                    content,
                    section_title,
                    section_type,
                    stack,
                    category,
                    content='documents',
                    content_rowid='rowid'
                )
            ''')
            
            # Tabela de termos individuais para busca avançada
            self.db_conn.execute('''
                CREATE TABLE IF NOT EXISTS terms (
                    term TEXT NOT NULL,
                    chunk_id TEXT NOT NULL,
                    frequency INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    PRIMARY KEY (term, chunk_id, position)
                )
            ''')
            
            # Índices para performance
            self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_terms_term ON terms(term)')
            self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_terms_chunk ON terms(chunk_id)')
            self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_docs_stack ON documents(stack)')
            self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_docs_category ON documents(category)')
            self.db_conn.execute('CREATE INDEX IF NOT EXISTS idx_docs_quality ON documents(quality_score)')
            
            # Triggers para manter FTS sincronizado
            self.db_conn.execute('''
                CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                    INSERT INTO documents_fts(chunk_id, content, section_title, section_type, stack, category)
                    VALUES (new.chunk_id, new.processed_content, new.section_title, new.section_type, new.stack, new.category);
                END
            ''')
            
            self.db_conn.execute('''
                CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                    DELETE FROM documents_fts WHERE chunk_id = old.chunk_id;
                END
            ''')
            
            self.db_conn.commit()
            
            # Atualiza estatísticas
            self._update_stats()
            
            self.logger.info(f"Índice de texto inicializado: {self.stats['total_documents']} documentos")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar índice de texto: {str(e)}")
            raise
    
    def add_chunks(self, chunks: List[Chunk]) -> int:
        """Adiciona chunks ao índice de texto"""
        if not chunks:
            return 0
        
        added_count = 0
        
        try:
            cursor = self.db_conn.cursor()
            
            for chunk in chunks:
                # Processa conteúdo
                processed_content = self._process_text(chunk.content)
                
                # Extrai termos
                terms = self._extract_terms(processed_content)
                
                # Insere documento
                cursor.execute('''
                    INSERT OR REPLACE INTO documents (
                        chunk_id, content, processed_content, metadata, indexed_at,
                        section_title, section_type, source_url, stack, category,
                        language, quality_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    chunk.id,
                    chunk.content,
                    processed_content,
                    json.dumps(chunk.metadata, ensure_ascii=False),
                    datetime.now().isoformat(),
                    chunk.section_title,
                    chunk.section_type,
                    chunk.metadata.get('source_url', ''),
                    chunk.metadata.get('stack', ''),
                    chunk.metadata.get('categoria', ''),
                    chunk.metadata.get('idioma', 'pt'),
                    chunk.metadata.get('quality_score', 0.0)
                ))
                
                # Remove termos antigos
                cursor.execute('DELETE FROM terms WHERE chunk_id = ?', (chunk.id,))
                
                # Insere novos termos
                for position, (term, frequency) in enumerate(terms.items()):
                    cursor.execute(
                        'INSERT INTO terms (term, chunk_id, frequency, position) VALUES (?, ?, ?, ?)',
                        (term, chunk.id, frequency, position)
                    )
                
                added_count += 1
            
            self.db_conn.commit()
            self._update_stats()
            
            self.logger.info(f"Adicionados {added_count} chunks ao índice de texto")
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar chunks ao índice de texto: {str(e)}")
            self.db_conn.rollback()
        
        return added_count
    
    def _process_text(self, text: str) -> str:
        """Processa texto para indexação"""
        # Remove HTML/Markdown
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links markdown
        text = re.sub(r'`[^`]+`', ' ', text)  # Code inline
        text = re.sub(r'```[^`]+```', ' ', text, flags=re.DOTALL)  # Code blocks
        
        # Normaliza unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Remove acentos (opcional)
        # text = ''.join(c for c in text if not unicodedata.combining(c))
        
        # Converte para minúsculas
        text = text.lower()
        
        # Remove pontuação excessiva
        text = re.sub(r'[^\w\s\-_.]', ' ', text)
        
        # Normaliza espaços
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_terms(self, text: str) -> Dict[str, int]:
        """Extrai termos do texto processado"""
        # Tokeniza
        tokens = re.findall(r'\b\w+\b', text)
        
        # Filtra tokens
        valid_tokens = []
        for token in tokens:
            if (self.min_term_length <= len(token) <= self.max_term_length and
                token not in self.stopwords and
                not token.isdigit()):
                valid_tokens.append(token)
        
        # Conta frequências
        term_frequencies = Counter(valid_tokens)
        
        return dict(term_frequencies)
    
    def search(self, query: str, top_k: int = 10, 
               filters: Optional[Dict[str, Any]] = None) -> List[TextSearchResult]:
        """Busca textual por palavras-chave"""
        if not query.strip():
            return []
        
        start_time = datetime.now()
        
        try:
            # Processa query
            processed_query = self._process_text(query)
            query_terms = self._extract_terms(processed_query)
            
            if not query_terms:
                return []
            
            # Busca usando FTS
            fts_results = self._search_fts(processed_query, top_k * 2, filters)
            
            # Busca por termos individuais
            term_results = self._search_terms(list(query_terms.keys()), top_k * 2, filters)
            
            # Combina e ranqueia resultados
            combined_results = self._combine_and_rank_results(
                fts_results, term_results, query_terms, top_k
            )
            
            # Atualiza estatísticas
            search_time = (datetime.now() - start_time).total_seconds()
            self.stats['search_count'] += 1
            self.stats['avg_search_time'] = (
                (self.stats['avg_search_time'] * (self.stats['search_count'] - 1) + search_time) /
                self.stats['search_count']
            )
            
            self.logger.debug(f"Busca textual: {len(combined_results)} resultados em {search_time:.3f}s")
            return combined_results
            
        except Exception as e:
            self.logger.error(f"Erro na busca textual: {str(e)}")
            return []
    
    def _search_fts(self, query: str, limit: int, 
                    filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Busca usando FTS (Full Text Search)"""
        cursor = self.db_conn.cursor()
        
        # Constrói query FTS
        fts_query = ' OR '.join(f'"{term}"' for term in query.split())
        
        # Constrói filtros
        where_clauses = []
        params = [fts_query]
        
        if filters:
            if filters.get('stack'):
                where_clauses.append('d.stack = ?')
                params.append(filters['stack'])
            
            if filters.get('categoria'):
                where_clauses.append('d.category = ?')
                params.append(filters['categoria'])
            
            if filters.get('licenca'):
                where_clauses.append('JSON_EXTRACT(d.metadata, "$.licenca") = ?')
                params.append(filters['licenca'])
            
            if filters.get('min_quality_score'):
                where_clauses.append('d.quality_score >= ?')
                params.append(filters['min_quality_score'])
        
        where_clause = ' AND '.join(where_clauses) if where_clauses else ''
        if where_clause:
            where_clause = f' AND {where_clause}'
        
        sql = f'''
            SELECT d.*, fts.rank
            FROM documents_fts fts
            JOIN documents d ON d.chunk_id = fts.chunk_id
            WHERE documents_fts MATCH ?
            {where_clause}
            ORDER BY fts.rank
            LIMIT ?
        '''
        
        params.append(limit)
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def _search_terms(self, terms: List[str], limit: int, 
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Busca por termos individuais"""
        cursor = self.db_conn.cursor()
        
        # Constrói query para termos
        term_placeholders = ','.join('?' * len(terms))
        
        # Constrói filtros
        where_clauses = []
        params = terms.copy()
        
        if filters:
            if filters.get('stack'):
                where_clauses.append('d.stack = ?')
                params.append(filters['stack'])
            
            if filters.get('categoria'):
                where_clauses.append('d.category = ?')
                params.append(filters['categoria'])
            
            if filters.get('licenca'):
                where_clauses.append('JSON_EXTRACT(d.metadata, "$.licenca") = ?')
                params.append(filters['licenca'])
        
        where_clause = ' AND '.join(where_clauses) if where_clauses else ''
        if where_clause:
            where_clause = f' AND {where_clause}'
        
        sql = f'''
            SELECT d.*, SUM(t.frequency) as term_score, COUNT(DISTINCT t.term) as matched_terms
            FROM terms t
            JOIN documents d ON d.chunk_id = t.chunk_id
            WHERE t.term IN ({term_placeholders})
            {where_clause}
            GROUP BY d.chunk_id
            ORDER BY matched_terms DESC, term_score DESC
            LIMIT ?
        '''
        
        params.append(limit)
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def _combine_and_rank_results(self, fts_results: List[Dict[str, Any]], 
                                  term_results: List[Dict[str, Any]], 
                                  query_terms: Dict[str, int], 
                                  top_k: int) -> List[TextSearchResult]:
        """Combina e ranqueia resultados de diferentes métodos de busca"""
        # Combina resultados por chunk_id
        combined = {}
        
        # Adiciona resultados FTS
        for result in fts_results:
            chunk_id = result['chunk_id']
            combined[chunk_id] = {
                'data': result,
                'fts_score': result.get('rank', 0),
                'term_score': 0,
                'matched_terms': 0
            }
        
        # Adiciona/atualiza com resultados de termos
        for result in term_results:
            chunk_id = result['chunk_id']
            if chunk_id in combined:
                combined[chunk_id]['term_score'] = result.get('term_score', 0)
                combined[chunk_id]['matched_terms'] = result.get('matched_terms', 0)
            else:
                combined[chunk_id] = {
                    'data': result,
                    'fts_score': 0,
                    'term_score': result.get('term_score', 0),
                    'matched_terms': result.get('matched_terms', 0)
                }
        
        # Calcula score final e cria resultados
        final_results = []
        
        for chunk_id, info in combined.items():
            data = info['data']
            
            # Score combinado (pode ser ajustado)
            fts_weight = 0.6
            term_weight = 0.4
            final_score = (fts_weight * info['fts_score'] + 
                          term_weight * info['term_score'])
            
            # Bonus por número de termos encontrados
            term_bonus = info['matched_terms'] / len(query_terms) if query_terms else 0
            final_score += term_bonus * 0.2
            
            # Bonus por qualidade
            quality_bonus = data.get('quality_score', 0) * 0.1
            final_score += quality_bonus
            
            # Encontra termos que fizeram match
            matched_terms = self._find_matched_terms(data['content'], query_terms)
            
            # Gera highlights
            highlights = self._generate_highlights(data['content'], matched_terms)
            
            result = TextSearchResult(
                chunk_id=chunk_id,
                content=data['content'],
                score=final_score,
                matched_terms=matched_terms,
                metadata=json.loads(data['metadata']),
                highlights=highlights
            )
            
            final_results.append(result)
        
        # Ordena por score e retorna top_k
        final_results.sort(key=lambda x: x.score, reverse=True)
        return final_results[:top_k]
    
    def _find_matched_terms(self, content: str, query_terms: Dict[str, int]) -> List[str]:
        """Encontra termos da query que aparecem no conteúdo"""
        content_lower = content.lower()
        matched = []
        
        for term in query_terms.keys():
            if term in content_lower:
                matched.append(term)
        
        return matched
    
    def _generate_highlights(self, content: str, matched_terms: List[str], 
                           max_highlights: int = 3, context_chars: int = 100) -> List[str]:
        """Gera highlights do conteúdo com termos encontrados"""
        if not matched_terms:
            return [content[:context_chars * 2] + '...' if len(content) > context_chars * 2 else content]
        
        highlights = []
        content_lower = content.lower()
        
        for term in matched_terms[:max_highlights]:
            # Encontra primeira ocorrência do termo
            pos = content_lower.find(term)
            if pos != -1:
                # Extrai contexto
                start = max(0, pos - context_chars)
                end = min(len(content), pos + len(term) + context_chars)
                
                highlight = content[start:end]
                
                # Adiciona elipses se necessário
                if start > 0:
                    highlight = '...' + highlight
                if end < len(content):
                    highlight = highlight + '...'
                
                # Destaca o termo (pode ser usado pelo frontend)
                highlight = highlight.replace(
                    content[pos:pos+len(term)], 
                    f'**{content[pos:pos+len(term)]}**'
                )
                
                highlights.append(highlight)
        
        return highlights if highlights else [content[:context_chars * 2] + '...']
    
    def _update_stats(self):
        """Atualiza estatísticas do índice"""
        cursor = self.db_conn.cursor()
        
        # Total de documentos
        cursor.execute('SELECT COUNT(*) FROM documents')
        self.stats['total_documents'] = cursor.fetchone()[0]
        
        # Total de termos
        cursor.execute('SELECT COUNT(*) FROM terms')
        self.stats['total_terms'] = cursor.fetchone()[0]
        
        # Termos únicos
        cursor.execute('SELECT COUNT(DISTINCT term) FROM terms')
        self.stats['unique_terms'] = cursor.fetchone()[0]
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do índice de texto"""
        cursor = self.db_conn.cursor()
        
        # Top termos
        cursor.execute('''
            SELECT term, COUNT(*) as doc_count, SUM(frequency) as total_freq
            FROM terms
            GROUP BY term
            ORDER BY doc_count DESC, total_freq DESC
            LIMIT 20
        ''')
        top_terms = [dict(row) for row in cursor.fetchall()]
        
        # Distribuição por stack
        cursor.execute('SELECT stack, COUNT(*) FROM documents GROUP BY stack')
        stack_distribution = dict(cursor.fetchall())
        
        # Distribuição por categoria
        cursor.execute('SELECT category, COUNT(*) FROM documents GROUP BY category')
        category_distribution = dict(cursor.fetchall())
        
        return {
            **self.stats,
            'top_terms': top_terms,
            'stack_distribution': stack_distribution,
            'category_distribution': category_distribution,
            'db_size_mb': self.text_db_path.stat().st_size / (1024 * 1024) if self.text_db_path.exists() else 0
        }
    
    def delete_chunks_by_source(self, source_url: str) -> int:
        """Remove chunks de uma fonte específica"""
        try:
            cursor = self.db_conn.cursor()
            
            # Busca chunks para remover
            cursor.execute('SELECT chunk_id FROM documents WHERE source_url = ?', (source_url,))
            chunk_ids = [row[0] for row in cursor.fetchall()]
            
            if not chunk_ids:
                return 0
            
            # Remove termos
            placeholders = ','.join('?' * len(chunk_ids))
            cursor.execute(f'DELETE FROM terms WHERE chunk_id IN ({placeholders})', chunk_ids)
            
            # Remove documentos (trigger remove do FTS automaticamente)
            cursor.execute('DELETE FROM documents WHERE source_url = ?', (source_url,))
            
            self.db_conn.commit()
            self._update_stats()
            
            self.logger.info(f"Removidos {len(chunk_ids)} chunks da fonte {source_url}")
            return len(chunk_ids)
            
        except Exception as e:
            self.logger.error(f"Erro ao remover chunks: {str(e)}")
            self.db_conn.rollback()
            return 0
    
    def optimize_index(self):
        """Otimiza o índice (rebuild FTS, vacuum, etc.)"""
        try:
            self.logger.info("Otimizando índice de texto...")
            
            # Rebuild FTS
            self.db_conn.execute('INSERT INTO documents_fts(documents_fts) VALUES("rebuild")')
            
            # Vacuum
            self.db_conn.execute('VACUUM')
            
            # Analyze
            self.db_conn.execute('ANALYZE')
            
            self.db_conn.commit()
            self.logger.info("Índice de texto otimizado")
            
        except Exception as e:
            self.logger.error(f"Erro ao otimizar índice: {str(e)}")
    
    def close(self):
        """Fecha conexão com banco"""
        if self.db_conn:
            self.db_conn.close()
        
        self.logger.info("Índice de texto fechado")