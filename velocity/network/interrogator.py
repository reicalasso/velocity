"""
Network Interrogator

The network is not storage.
The network is an active epistemological space.

This module interrogates the network in real-time.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from loguru import logger
from bs4 import BeautifulSoup
import time


class NetworkInterrogator:
    """
    Network Interrogation System
    
    Executes parallel queries against the network.
    The network is the knowledge base.
    """
    
    def __init__(
        self,
        max_parallel: int = 5,
        timeout: float = 10.0,
        user_agent: str = "Velocity/0.1.0"
    ):
        """
        Initialize Network Interrogator
        
        Args:
            max_parallel: Maximum parallel queries
            timeout: Request timeout in seconds
            user_agent: User agent string
        """
        self.max_parallel = max_parallel
        self.timeout = timeout
        self.user_agent = user_agent
        
        # Statistics
        self.queries_executed = 0
        self.total_latency = 0.0
        self.errors = 0
        
        logger.info(f"Network Interrogator initialized (parallel={max_parallel})")
    
    async def search_parallel(
        self,
        queries: List[str],
        search_engine: str = "duckduckgo"
    ) -> List[Dict[str, Any]]:
        """
        Execute parallel searches across the network.
        
        This is the core of "access-driven" intelligence:
        Speed of interrogation matters more than size of memory.
        
        Args:
            queries: List of search queries
            search_engine: Search engine to use
            
        Returns:
            List of search results
        """
        logger.debug(f"Executing {len(queries)} parallel queries")
        
        # Create tasks for parallel execution
        tasks = [
            self._execute_query(query, search_engine)
            for query in queries[:self.max_parallel]
        ]
        
        # Execute in parallel
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        latency = time.time() - start_time
        
        self.total_latency += latency
        logger.debug(f"Parallel queries completed in {latency:.2f}s")
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Query failed: {result}")
                self.errors += 1
                continue
            processed_results.append(result)
        
        return processed_results
    
    async def _execute_query(
        self,
        query: str,
        search_engine: str
    ) -> Dict[str, Any]:
        """
        Execute a single query.
        
        Args:
            query: Search query
            search_engine: Search engine to use
            
        Returns:
            Query result
        """
        self.queries_executed += 1
        
        try:
            if search_engine == "duckduckgo":
                return await self._query_duckduckgo(query)
            elif search_engine == "wikipedia":
                return await self._query_wikipedia(query)
            else:
                # Fallback: simulate search
                return await self._simulated_search(query)
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }
    
    async def _query_duckduckgo(self, query: str) -> Dict[str, Any]:
        """
        Query DuckDuckGo HTML API.
        
        Note: For production, you'd want to use proper API or services.
        This is a demonstration.
        """
        url = "https://html.duckduckgo.com/html/"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    data={"q": query},
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    html = await response.text()
                    content = self._extract_content_from_html(html)
                    
                    return {
                        "success": True,
                        "query": query,
                        "source": "duckduckgo",
                        "content": content,
                        "metadata": {
                            "url": str(response.url),
                            "status": response.status
                        }
                    }
            except asyncio.TimeoutError:
                logger.warning(f"Query timeout: {query}")
                return {
                    "success": False,
                    "query": query,
                    "error": "timeout"
                }
    
    async def _query_wikipedia(self, query: str) -> Dict[str, Any]:
        """
        Query Wikipedia API.
        
        Wikipedia is an excellent knowledge source for Velocity:
        - Always up to date
        - Well-structured
        - Contradictions documented
        """
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": query,
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url,
                    params=params,
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    data = await response.json()
                    pages = data.get("query", {}).get("pages", {})
                    
                    # Extract content
                    content = ""
                    for page_id, page_data in pages.items():
                        if "extract" in page_data:
                            content = page_data["extract"]
                            break
                    
                    return {
                        "success": True,
                        "query": query,
                        "source": "wikipedia",
                        "content": content,
                        "metadata": {
                            "page_id": page_id,
                            "title": page_data.get("title", "")
                        }
                    }
            except asyncio.TimeoutError:
                logger.warning(f"Query timeout: {query}")
                return {
                    "success": False,
                    "query": query,
                    "error": "timeout"
                }
    
    async def _simulated_search(self, query: str) -> Dict[str, Any]:
        """
        Simulated search for testing.
        
        In production, this would be replaced with real search APIs.
        """
        await asyncio.sleep(0.5)  # Simulate network latency
        
        content = (
            f"Simulated search result for: {query}\n\n"
            f"This is a demonstration of the Velocity Paradigm. "
            f"In production, this would query real search engines, databases, "
            f"APIs, and other network sources in real-time.\n\n"
            f"The key insight is that intelligence doesn't come from "
            f"storing this information in model weights, but from the "
            f"speed and quality of accessing it when needed."
        )
        
        return {
            "success": True,
            "query": query,
            "source": "simulated",
            "content": content,
            "metadata": {
                "simulation": True
            }
        }
    
    def _extract_content_from_html(self, html: str) -> str:
        """
        Extract meaningful content from HTML.
        
        Network returns raw HTML. We need to extract signal from noise.
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)
        
        # Limit length
        return text[:2000]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get interrogator statistics"""
        avg_latency = (
            self.total_latency / self.queries_executed
            if self.queries_executed > 0
            else 0.0
        )
        
        return {
            "queries_executed": self.queries_executed,
            "total_latency": round(self.total_latency, 2),
            "avg_latency": round(avg_latency, 3),
            "errors": self.errors,
            "success_rate": (
                (self.queries_executed - self.errors) / self.queries_executed
                if self.queries_executed > 0
                else 0.0
            )
        }
