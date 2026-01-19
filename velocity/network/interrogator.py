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
import os


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
        user_agent: str = "Velocity/0.1.0",
        use_real_search: bool = True
    ):
        """
        Initialize Network Interrogator
        
        Args:
            max_parallel: Maximum parallel queries
            timeout: Request timeout in seconds
            user_agent: User agent string
            use_real_search: Use real web search (Google/Bing/DDG)
        """
        self.max_parallel = max_parallel
        self.timeout = timeout
        self.user_agent = user_agent
        self.use_real_search = use_real_search
        
        # Initialize web search engine if enabled
        if use_real_search:
            try:
                from .web_search import WebSearchEngine, NLPProcessor
                self.web_search = WebSearchEngine(
                    google_api_key=os.getenv('GOOGLE_API_KEY'),
                    google_cse_id=os.getenv('GOOGLE_CSE_ID'),
                    bing_api_key=os.getenv('BING_API_KEY'),
                    max_results=3,
                    timeout=int(timeout)
                )
                self.nlp = NLPProcessor()
                logger.info("Real web search enabled")
            except Exception as e:
                logger.warning(f"Could not initialize web search: {e}, falling back to simulated")
                self.use_real_search = False
        
        # Statistics
        self.queries_executed = 0
        self.total_latency = 0.0
        self.errors = 0
        
        logger.info(f"Network Interrogator initialized (parallel={max_parallel}, real_search={use_real_search})")
    
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
            # 0. Try Real Web Search First (if enabled) 🌐
            if self.use_real_search and hasattr(self, 'web_search'):
                try:
                    logger.info(f"🔍 Real web search: {query}")
                    results = await self.web_search.search(query, source_type="web")
                    
                    if results:
                        # Combine multiple results for richer answer
                        all_content = []
                        all_titles = []
                        all_urls = []
                        
                        for result in results[:3]:  # Use top 3 results
                            content = result.content or result.snippet
                            if content and len(content) > 50:
                                all_content.append(content)
                                all_titles.append(result.title)
                                all_urls.append(result.url)
                        
                        if all_content:
                            # Combine and summarize all content
                            combined_text = " ".join(all_content)
                            
                            # Extract summary from combined content
                            summary = self.nlp.extractive_summarize(combined_text, num_sentences=4)
                            keywords = self.nlp.extract_keywords(combined_text, top_k=7)
                            
                            # Calculate average relevance
                            avg_relevance = sum(r.relevance_score for r in results[:3]) / min(3, len(results))
                            
                            logger.success(f"✅ Real search: {results[0].source_type} ({len(all_content)} sources)")
                            
                            return {
                                "success": True,
                                "query": query,
                                "source": f"{results[0].source_type}://multi-source",
                                "content": summary,
                                "metadata": {
                                    "titles": all_titles,
                                    "urls": all_urls,
                                    "keywords": keywords,
                                    "relevance": avg_relevance,
                                    "sources_combined": len(all_content),
                                    "method": "real_web_search+nlp+multi_source"
                                }
                            }
                except Exception as e:
                    logger.warning(f"⚠️ Real web search failed: {e}")
            
            # 1. Wikipedia (best for encyclopedic knowledge)
            try:
                result = await self._query_wikipedia_simple(query)
                if result["success"]:
                    return result
            except Exception as e:
                logger.debug(f"Wikipedia failed: {e}")
            
            # 2. Try DuckDuckGo instant answer
            try:
                result = await self._query_duckduckgo_instant(query)
                if result["success"]:
                    return result
            except Exception as e:
                logger.debug(f"DuckDuckGo instant failed: {e}")
            
            # 3. Fallback to simulated (with better content)
            return await self._simulated_search_enhanced(query)
            
        except Exception as e:
            logger.error(f"All query methods failed: {e}")
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
        
        # First try: search for the page
        search_params = {
            "action": "opensearch",
            "format": "json",
            "search": query,
            "limit": 1
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                # Step 1: Search for matching page
                async with session.get(
                    url,
                    params=search_params,
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as search_response:
                    if search_response.status != 200:
                        raise Exception(f"HTTP {search_response.status}")
                    
                    search_data = await search_response.json()
                    
                    # Get the first matching title
                    if not search_data or len(search_data) < 2 or not search_data[1]:
                        raise Exception(f"No Wikipedia page found for: {query}")
                    
                    page_title = search_data[1][0]
                    logger.debug(f"Found Wikipedia page: {page_title}")
                
                # Step 2: Get page content
                content_params = {
                    "action": "query",
                    "format": "json",
                    "prop": "extracts",
                    "exintro": True,
                    "explaintext": True,
                    "titles": page_title,
                }
                
                async with session.get(
                    url,
                    params=content_params,
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    data = await response.json()
                    pages = data.get("query", {}).get("pages", {})
                    
                    # Extract content
                    content = ""
                    page_id = ""
                    for pid, page_data in pages.items():
                        if "extract" in page_data:
                            content = page_data["extract"]
                            page_id = pid
                            break
                    
                    if not content:
                        raise Exception("No content extracted from Wikipedia")
                    
                    logger.info(f"Successfully retrieved Wikipedia content for '{page_title}' ({len(content)} chars)")
                    
                    return {
                        "success": True,
                        "query": query,
                        "source": f"wikipedia:{page_title}",
                        "content": content,
                        "metadata": {
                            "page_id": page_id,
                            "title": page_title,
                            "url": f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                        }
                    }
            except asyncio.TimeoutError:
                logger.warning(f"Wikipedia query timeout: {query}")
                raise Exception("timeout")
            except Exception as e:
                logger.warning(f"Wikipedia query failed for '{query}': {e}")
                raise
    
    async def _query_wikipedia_simple(self, query: str) -> Dict[str, Any]:
        """Simple Wikipedia query without search API"""
        # Clean query - remove command words
        clean_query = query.replace("answer:", "").replace("documentation", "").strip()
        
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_query.replace(' ', '_')}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"User-Agent": "Velocity/0.2.0 (Educational Research)"},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("extract", "")
                    
                    if content:
                        logger.info(f"Wikipedia SUCCESS: {data.get('title', clean_query)}")
                        return {
                            "success": True,
                            "query": query,
                            "source": f"wikipedia:{data.get('title', clean_query)}",
                            "content": content,
                            "metadata": {
                                "title": data.get("title"),
                                "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                            }
                        }
                
                raise Exception(f"HTTP {response.status}")
    
    async def _query_duckduckgo_instant(self, query: str) -> Dict[str, Any]:
        """Query DuckDuckGo Instant Answer API"""
        clean_query = query.replace("answer:", "").replace("documentation", "").strip()
        url = "https://api.duckduckgo.com/"
        params = {
            "q": clean_query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params=params,
                headers={"User-Agent": "Velocity/0.2.0 (Educational Research)"},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Try to get content from instant answer
                    content = data.get("AbstractText") or data.get("Abstract")
                    
                    if content and len(content) > 50:
                        logger.info(f"DuckDuckGo SUCCESS: {clean_query}")
                        return {
                            "success": True,
                            "query": query,
                            "source": f"duckduckgo:{data.get('Heading', clean_query)}",
                            "content": content,
                            "metadata": {
                                "heading": data.get("Heading"),
                                "url": data.get("AbstractURL", "")
                            }
                        }
                
                raise Exception(f"No instant answer available")
    
    async def _simulated_search_enhanced(self, query: str) -> Dict[str, Any]:
        """
        Enhanced simulated search with realistic content.
        
        This is a fallback when real APIs fail.
        In production, you'd integrate more APIs or use WebSearch service.
        """
        await asyncio.sleep(0.3)  # Simulate network latency
        
        # Extract topic from query
        clean_query = query.replace("answer:", "").replace("documentation", "").strip()
        
        # Knowledge base for common queries
        knowledge_base = {
            "python": "Python is a high-level, interpreted programming language created by Guido van Rossum and first released in 1991. It emphasizes code readability with significant whitespace. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            "quantum computing": "Quantum computing is a type of computation that uses quantum mechanical phenomena like superposition and entanglement. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits or qubits that can exist in multiple states simultaneously.",
            "artificial intelligence": "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction. AI applications include expert systems, natural language processing, speech recognition and machine vision.",
            "machine learning": "Machine learning is a subset of artificial intelligence that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.",
            "blockchain": "Blockchain is a distributed ledger technology that maintains a continuously growing list of records called blocks. Each block contains a cryptographic hash of the previous block, timestamp, and transaction data. It provides secure, transparent, and tamper-resistant record-keeping.",
            "rust": "Rust is a systems programming language focused on safety, concurrency, and performance. Created by Mozilla, it prevents common bugs like null pointer dereferences and data races through its unique ownership system and borrow checker.",
        }
        
        # Code generation responses
        code_requests = {
            "python": '''# Simple Python example
def hello_world():
    """A simple hello world function"""
    print("Hello, World!")
    return "Success"

# Example usage
if __name__ == "__main__":
    result = hello_world()
    print(f"Result: {result}")

# More complex example
def fibonacci(n):
    """Calculate fibonacci sequence"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Calculate first 10 fibonacci numbers
for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")''',
            
            "javascript": '''// Simple JavaScript example
function helloWorld() {
    console.log("Hello, World!");
    return "Success";
}

// Example usage
const result = helloWorld();
console.log(`Result: ${result}`);

// More complex example
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

// Calculate first 10 fibonacci numbers
for (let i = 0; i < 10; i++) {
    console.log(`fib(${i}) = ${fibonacci(i)}`);
}''',
            
            "java": '''// Simple Java example
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        
        // More complex example
        for (int i = 0; i < 10; i++) {
            System.out.println("fib(" + i + ") = " + fibonacci(i));
        }
    }
    
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n-1) + fibonacci(n-2);
    }
}''',
            
            "c": '''// Simple C example
#include <stdio.h>

// Fibonacci function
int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    printf("Hello, World!\\n");
    
    // Calculate first 10 fibonacci numbers
    for (int i = 0; i < 10; i++) {
        printf("fib(%d) = %d\\n", i, fibonacci(i));
    }
    
    return 0;
}''',
            
            "cpp": '''// Simple C++ example
#include <iostream>
using namespace std;

// Fibonacci function
int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    cout << "Hello, World!" << endl;
    
    // Calculate first 10 fibonacci numbers
    for (int i = 0; i < 10; i++) {
        cout << "fib(" << i << ") = " << fibonacci(i) << endl;
    }
    
    return 0;
}''',
            
            "rust": '''// Simple Rust example
fn fibonacci(n: u32) -> u32 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n-1) + fibonacci(n-2),
    }
}

fn main() {
    println!("Hello, World!");
    
    // Calculate first 10 fibonacci numbers
    for i in 0..10 {
        println!("fib({}) = {}", i, fibonacci(i));
    }
}''',
            
            "html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello World</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        h1 {
            color: #333;
        }
    </style>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This is a simple HTML page.</p>
    
    <h2>List Example:</h2>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
</body>
</html>''',
            
            "css": '''/* Simple CSS example */
body {
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1 {
    color: #333;
    font-size: 2.5em;
    margin-bottom: 20px;
}

.button {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.button:hover {
    background-color: #0056b3;
}''',
            
            "go": '''// Simple Go example
package main

import "fmt"

func fibonacci(n int) int {
    if n <= 1 {
        return n
    }
    return fibonacci(n-1) + fibonacci(n-2)
}

func main() {
    fmt.Println("Hello, World!")
    
    // Calculate first 10 fibonacci numbers
    for i := 0; i < 10; i++ {
        fmt.Printf("fib(%d) = %d\\n", i, fibonacci(i))
    }
}''',
            
            "php": '''<?php
// Simple PHP example

function fibonacci($n) {
    if ($n <= 1) {
        return $n;
    }
    return fibonacci($n-1) + fibonacci($n-2);
}

echo "Hello, World!\\n";

// Calculate first 10 fibonacci numbers
for ($i = 0; $i < 10; $i++) {
    echo "fib($i) = " . fibonacci($i) . "\\n";
}
?>''',
            
            "sql": '''-- Simple SQL example

-- Create a users table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com');

-- Query users
SELECT * FROM users WHERE name LIKE 'A%';

-- Update a user
UPDATE users SET email = 'newemail@example.com' WHERE id = 1;

-- Count users
SELECT COUNT(*) as total_users FROM users;''',
        }
        
        # Try to find matching content
        content = None
        matched_key = None
        query_lower = clean_query.lower()
        
        # Check if this is a code generation request
        is_code_request = any(keyword in query_lower for keyword in ['yaz', 'write', 'create', 'generate', 'kod', 'code', 'örnek', 'example'])
        
        if is_code_request:
            # Try to match programming language - check specific language keywords
            lang_keywords = {
                'html': ['html', 'web page', 'webpage'],
                'css': ['css', 'style', 'stylesheet'],
                'python': ['python', 'py'],
                'javascript': ['javascript', 'js', 'node'],
                'java': ['java'],
                'c': [' c ', 'c dili', 'c code', 'c kodu'],
                'cpp': ['c++', 'cpp'],
                'rust': ['rust', 'rs'],
                'go': ['go ', 'golang'],
                'php': ['php'],
                'sql': ['sql', 'database', 'query'],
            }
            
            detected_lang = None
            for lang, keywords in lang_keywords.items():
                if any(kw in query_lower for kw in keywords):
                    detected_lang = lang
                    break
            
            # If no specific language detected, default to Python
            if not detected_lang:
                detected_lang = 'python'
            
            # Get code for the detected language
            if detected_lang in code_requests:
                content = f"Here's a {detected_lang.upper()} code example:\n\n{code_requests[detected_lang]}"
                matched_key = f"{detected_lang}_code"
            else:
                # Fallback to Python
                content = f"Here's a Python code example:\n\n{code_requests['python']}"
                matched_key = "python_code"
        else:
            # Regular knowledge base lookup
            for key, value in knowledge_base.items():
                if key in query_lower or query_lower in key:
                    content = value
                    matched_key = key
                    break
        
        if not content:
            content = (
                f"Information about {clean_query}:\n\n"
                f"This is enhanced simulated content for Velocity testing. "
                f"In production, this would come from real search APIs, databases, "
                f"and network sources. The Velocity Paradigm emphasizes real-time "
                f"network interrogation rather than pre-trained knowledge storage."
            )
            matched_key = clean_query
        
        logger.info(f"Enhanced simulation: {matched_key}")
        
        return {
            "success": True,
            "query": query,
            "source": f"knowledge_base:{matched_key}",
            "content": content,
            "metadata": {
                "simulated": True,
                "matched_key": matched_key
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
