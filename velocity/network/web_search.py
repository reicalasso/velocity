"""
REAL WEB SEARCH + NLP
=====================

Velocity'nin asıl gücü: LLM yok, sadece web'den bilgi çekip NLP ile işle.

"Intelligence lives in the speed of interrogation, not in the size of memory."
"""

import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import time
from loguru import logger


@dataclass
class SearchResult:
    """Web arama sonucu"""
    url: str
    title: str
    snippet: str
    content: Optional[str] = None
    relevance_score: float = 0.0
    source_type: str = "web"


class WebSearchEngine:
    """
    Gerçek web araması yapan motor
    
    Multiple sources:
    - Google Custom Search API
    - Bing Search API
    - DuckDuckGo HTML scraping
    - Direct website scraping
    """
    
    def __init__(
        self,
        google_api_key: Optional[str] = None,
        google_cse_id: Optional[str] = None,
        bing_api_key: Optional[str] = None,
        max_results: int = 5,
        timeout: int = 10
    ):
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
        self.bing_api_key = bing_api_key
        self.max_results = max_results
        self.timeout = timeout
        
        # User agent for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    async def search(self, query: str, source_type: str = "web") -> List[SearchResult]:
        """
        Web'de arama yap
        
        Args:
            query: Arama sorgusu
            source_type: Arama tipi (web, code, academic, etc.)
            
        Returns:
            SearchResult listesi
        """
        logger.info(f"Web search: '{query}' (type: {source_type})")
        
        results = []
        
        # Strategy 1: Try Google Custom Search (if API key available)
        if self.google_api_key and self.google_cse_id:
            try:
                google_results = await self._search_google(query)
                results.extend(google_results)
                logger.info(f"Google returned {len(google_results)} results")
            except Exception as e:
                logger.warning(f"Google search failed: {e}")
        
        # Strategy 2: Try Bing Search (if API key available)
        if self.bing_api_key and len(results) < self.max_results:
            try:
                bing_results = await self._search_bing(query)
                results.extend(bing_results)
                logger.info(f"Bing returned {len(bing_results)} results")
            except Exception as e:
                logger.warning(f"Bing search failed: {e}")
        
        # Strategy 3: DuckDuckGo HTML scraping (no API key needed)
        if len(results) < self.max_results:
            try:
                ddg_results = await self._search_duckduckgo_html(query)
                results.extend(ddg_results)
                logger.info(f"DuckDuckGo returned {len(ddg_results)} results")
            except Exception as e:
                logger.warning(f"DuckDuckGo search failed: {e}")
        
        # Strategy 4: Code-specific search for generative queries
        if source_type == "code" and len(results) < self.max_results:
            try:
                code_results = await self._search_code(query)
                results.extend(code_results)
                logger.info(f"Code search returned {len(code_results)} results")
            except Exception as e:
                logger.warning(f"Code search failed: {e}")
        
        # Limit results
        results = results[:self.max_results]
        
        # Fetch full content for top results
        for result in results[:3]:  # Only top 3
            try:
                result.content = await self._fetch_content(result.url)
            except Exception as e:
                logger.debug(f"Failed to fetch content from {result.url}: {e}")
        
        return results
    
    async def _search_google(self, query: str) -> List[SearchResult]:
        """Google Custom Search API"""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'q': query,
            'num': self.max_results
        }
        
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('items', []):
            results.append(SearchResult(
                url=item['link'],
                title=item['title'],
                snippet=item.get('snippet', ''),
                source_type='google'
            ))
        
        return results
    
    async def _search_bing(self, query: str) -> List[SearchResult]:
        """Bing Search API"""
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {
            'Ocp-Apim-Subscription-Key': self.bing_api_key
        }
        params = {
            'q': query,
            'count': self.max_results
        }
        
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('webPages', {}).get('value', []):
            results.append(SearchResult(
                url=item['url'],
                title=item['name'],
                snippet=item.get('snippet', ''),
                source_type='bing'
            ))
        
        return results
    
    async def _search_duckduckgo_html(self, query: str) -> List[SearchResult]:
        """
        DuckDuckGo HTML scraping (API yok, HTML parse et)
        
        Bu yöntem API key gerektirmez ama rate limit'e takılabilir
        """
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        
        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        # Parse search results
        for result_div in soup.find_all('div', class_='result'):
            try:
                # Extract title and link
                title_elem = result_div.find('a', class_='result__a')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                
                # Extract snippet
                snippet_elem = result_div.find('a', class_='result__snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                
                if link and title:
                    results.append(SearchResult(
                        url=link,
                        title=title,
                        snippet=snippet,
                        source_type='duckduckgo'
                    ))
                
                if len(results) >= self.max_results:
                    break
                    
            except Exception as e:
                logger.debug(f"Failed to parse DDG result: {e}")
                continue
        
        return results
    
    async def _search_code(self, query: str) -> List[SearchResult]:
        """
        Kod araması (GitHub, StackOverflow vb.)
        
        GitHub Code Search: https://api.github.com/search/code
        StackOverflow: https://api.stackexchange.com/2.3/search
        """
        results = []
        
        # GitHub Code Search (no auth needed for limited requests)
        try:
            gh_url = "https://api.github.com/search/code"
            params = {
                'q': query,
                'per_page': 3
            }
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Velocity-Search'
            }
            
            response = requests.get(
                gh_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', [])[:3]:
                    results.append(SearchResult(
                        url=item['html_url'],
                        title=f"{item['name']} - {item['repository']['full_name']}",
                        snippet=f"GitHub code: {item['path']}",
                        source_type='github'
                    ))
        except Exception as e:
            logger.debug(f"GitHub search failed: {e}")
        
        # StackOverflow Search (no auth needed)
        try:
            so_url = "https://api.stackexchange.com/2.3/search"
            params = {
                'order': 'desc',
                'sort': 'relevance',
                'intitle': query,
                'site': 'stackoverflow',
                'pagesize': 3
            }
            
            response = requests.get(
                so_url,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', [])[:3]:
                    # Get accepted answer if available
                    answer_text = ""
                    if item.get('is_answered'):
                        answer_text = " (✓ answered)"
                    
                    results.append(SearchResult(
                        url=item['link'],
                        title=item['title'],
                        snippet=f"StackOverflow{answer_text} - Score: {item['score']}",
                        source_type='stackoverflow'
                    ))
        except Exception as e:
            logger.debug(f"StackOverflow search failed: {e}")
        
        return results
    
    async def _fetch_content(self, url: str) -> str:
        """
        Fetch and clean content from URL
        
        This is the first step of NLP processing: raw HTML to text extraction
        """
        try:
            # Fix protocol-relative URLs (// -> https://)
            if url.startswith('//'):
                url = 'https:' + url
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Limit length (first 5000 characters)
            return text[:5000]
            
        except Exception as e:
            logger.debug(f"Content fetch failed for {url}: {e}")
            return ""


class NLPProcessor:
    """
    NLP-based text processing
    
    LLM kullanmadan:
    - Text summarization (extractive)
    - Keyword extraction
    - Relevance scoring
    - Entity recognition
    """
    
    def __init__(self):
        # TF-IDF for keyword extraction
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """
        TF-IDF ile keyword extraction
        
        LLM gerektirmez, istatistiksel yöntem
        """
        try:
            # Vectorize
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Get top keywords
            tfidf_scores = tfidf_matrix.toarray()[0]
            top_indices = tfidf_scores.argsort()[-top_k:][::-1]
            
            keywords = [feature_names[i] for i in top_indices]
            return keywords
            
        except Exception as e:
            logger.debug(f"Keyword extraction failed: {e}")
            return []
    
    def extractive_summarize(self, text: str, num_sentences: int = 3) -> str:
        """
        Extractive summarization with natural spacing
        
        Selects most important sentences using TF-IDF
        """
        try:
            # Clean text spacing first
            text = self._clean_text_spacing(text)
            
            # Split into sentences (preserve spacing)
            sentences = re.split(r'(?<=[.!?])\s+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            if len(sentences) <= num_sentences:
                result = ' '.join(sentences)
                if not result.endswith('.'):
                    result += '.'
                return result
            
            # Score sentences with TF-IDF
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Sum TF-IDF scores for each sentence
            sentence_scores = tfidf_matrix.sum(axis=1).A1
            
            # Get top sentences
            top_indices = sentence_scores.argsort()[-num_sentences:][::-1]
            top_indices.sort()  # Keep original order
            
            summary_sentences = [sentences[i] for i in top_indices]
            
            # Join with proper spacing
            result = ' '.join(summary_sentences)
            
            # Ensure ends with period
            if not result.endswith(('.', '!', '?')):
                result += '.'
            
            return result
            
        except Exception as e:
            logger.debug(f"Summarization failed: {e}")
            # Fallback: first N sentences with cleaning
            text = self._clean_text_spacing(text)
            sentences = re.split(r'(?<=[.!?])\s+', text)
            result = ' '.join(sentences[:num_sentences])
            if not result.endswith('.'):
                result += '.'
            return result
    
    def _clean_text_spacing(self, text: str) -> str:
        """
        Fix common spacing issues in extracted text
        
        Makes text readable and natural
        """
        # Fix concatenated camelCase words
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Fix word-number concatenation
        text = re.sub(r'([a-z])(\d)', r'\1 \2', text)
        text = re.sub(r'(\d)([a-z])', r'\1 \2', text)
        
        # Fix punctuation spacing
        text = re.sub(r'\s*,\s*', ', ', text)
        text = re.sub(r'\s*\.\s*', '. ', text)
        text = re.sub(r'\s*;\s*', '; ', text)
        text = re.sub(r'\s*:\s*', ': ', text)
        text = re.sub(r'\s*!\s*', '! ', text)
        text = re.sub(r'\s*\?\s*', '? ', text)
        
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix space before period
        text = re.sub(r'\s+\.', '.', text)
        
        return text.strip()
    
    def calculate_relevance(
        self,
        query: str,
        text: str,
        method: str = "cosine"
    ) -> float:
        """
        Query ile text arasındaki relevance skoru
        
        Cosine similarity (TF-IDF vectors)
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([query, text])
            
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.debug(f"Relevance calculation failed: {e}")
            # Fallback: simple keyword overlap
            query_words = set(query.lower().split())
            text_words = set(text.lower().split())
            overlap = len(query_words & text_words) / max(len(query_words), 1)
            return overlap
