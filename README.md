# Velocity

**Network-Native, Dataset-Free General Intelligence**

> "Intelligence lives in the speed of interrogation, not in the size of memory."

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](https://github.com)

---

## Overview

Velocity is a novel paradigm for artificial intelligence that eliminates the need for pre-trained models and large language models. Instead of storing knowledge in parameters, Velocity accesses information in real-time through strategic network interrogation.

### Key Features

- **No pre-trained models**: No stored knowledge, no outdated information
- **No LLM dependency**: No hallucinations, only real sources
- **Real-time web search**: Always current information
- **NLP-based processing**: TF-IDF, extractive summarization, cosine similarity
- **7-step cognitive loop**: Transparent, auditable reasoning
- **Epistemically sound**: Confidence calibration and source tracking

### Core Principle

Intelligence emerges from the speed and quality of information access, not from the size of stored knowledge. Velocity optimizes for evaluation speed rather than storage capacity.

---

## Installation

### Requirements

- Python 3.10 or higher
- Internet connection (for real-time web search)
- Optional: Google/Bing API keys for enhanced search

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/velocity.git
cd velocity

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Velocity
pip install -e .
```

### Verification

```bash
# Run tests
pytest tests/

# Expected output: 26/26 tests passing
```

---

## Quick Start

### Interactive Mode

```bash
# Start interactive Q&A
python interactive_velocity.py

# Or on Windows
START_INTERACTIVE.bat
```

### Example Session

```
VELOCITY - INTERACTIVE MODE

[1] Your question: What is quantum computing?

[PROCESSING...] Velocity is thinking...

[ANSWER]
Quantum computing utilizes quantum mechanics principles like 
superposition and entanglement. Unlike classical bits, qubits 
can represent multiple states simultaneously.

[DETAILS]
  Confidence: 74.0%
  Uncertainty: LOW
  Sources: duckduckgo, wikipedia

[2] Your question: write python code

[ANSWER]
# Python code example
def hello_world():
    print("Hello, World!")
    return "Success"
```

### Python API

```python
from velocity.core.velocity_core import VelocityCore

# Initialize
core = VelocityCore(
    max_hypotheses=2,
    confidence_threshold=0.6,
    max_iterations=3
)

# Execute query
result = await core.execute("What is machine learning?")

# Access results
print(result['decision'])        # Final answer
print(result['confidence'])      # 0.0-1.0
print(result['uncertainty'])     # LOW/MEDIUM/HIGH
print(result['source_breakdown']) # Source attribution
```

---

## Architecture

### The 7-Step Cognitive Loop

Every query undergoes a structured reasoning process:

```
[1/7] INTENT PARSING
      Transform query into structured intent graph
      
[2/7] EPISTEMIC ROUTING
      Select appropriate knowledge sources
      
[3/7] HYPOTHESIS GENERATION
      Generate multiple parallel explanations
      
[4/7] NETWORK INTERROGATION
      Query sources: DuckDuckGo, Google, Bing, GitHub, StackOverflow
      
[5/7] CONTRADICTION HANDLING
      Detect and manage conflicting information
      
[6/7] HYPOTHESIS ELIMINATION
      Natural selection of hypotheses based on evidence
      
[7/7] STATE SYNTHESIS
      Synthesize final answer with confidence calibration
```

### Real Web Search

Velocity integrates multiple search engines:

- **DuckDuckGo HTML Scraping** (no API key required)
- **Google Custom Search** (optional, requires API key)
- **Bing Search API** (optional, requires API key)
- **GitHub Code Search** (for code-related queries)
- **StackOverflow API** (for programming questions)

### NLP Processing

All content processing uses traditional NLP techniques:

- **TF-IDF** for keyword extraction
- **Extractive summarization** for content condensation
- **Cosine similarity** for relevance scoring
- **BeautifulSoup** for HTML parsing

No large language models are used for generation or summarization.

---

## Configuration

### Environment Variables (Optional)

For enhanced search results, configure API keys:

```bash
# Google Custom Search
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_CSE_ID="your-cse-id"

# Bing Search
export BING_API_KEY="your-bing-key"
```

Without API keys, Velocity defaults to DuckDuckGo HTML scraping, which requires no authentication.

### Customization

```python
# Adjust hypothesis count (more = thorough but slower)
core = VelocityCore(max_hypotheses=5)

# Set confidence threshold (higher = only high-confidence answers)
core = VelocityCore(confidence_threshold=0.8)

# Configure iteration depth (deeper search)
core = VelocityCore(max_iterations=5)
```

---

## How It Works

### Traditional LLMs

```
User Query → LLM (black box) → Answer
              ↑
        Pre-trained knowledge
        (outdated, may hallucinate)
```

### Velocity

```
User Query
    ↓
[1] Parse Intent
    ↓
[2] Route to Sources
    ↓
[3] Generate Hypotheses
    ↓
[4] Search Web (real-time)
    ↓
[5] Handle Contradictions
    ↓
[6] Eliminate Weak Hypotheses
    ↓
[7] Synthesize Answer
    ↓
Answer (transparent, sourced, calibrated)
```

### Key Differences

| Traditional LLMs | Velocity |
|-----------------|----------|
| Pre-trained knowledge | Real-time search |
| Static, frozen in time | Always current |
| May hallucinate | Only uses real sources |
| Black box reasoning | Transparent 7-step process |
| No source tracking | Full attribution |
| Overconfident | Calibrated confidence |

---

## Use Cases

### Research & Fact-Checking

Velocity provides sourced, verifiable answers with confidence scores and full attribution.

### Code Generation

Retrieves real code examples from GitHub and StackOverflow rather than generating potentially incorrect code.

### Comparative Analysis

Handles multiple perspectives and conflicting information through structured contradiction management.

### Current Information

Always up-to-date since it searches the web in real-time rather than relying on training data.

---

## Performance

### Query Performance

- Average latency: 1-3 seconds
- Sources per query: 3-5 web pages
- Keywords extracted: 5-10 (TF-IDF)
- Summary: 3 sentences (extractive)
- Confidence: Calibrated 60-90%

### System Requirements

- Python 3.10+
- Memory: ~500MB
- CPU: Moderate (for NLP processing)
- Network: Required (for web search)

---

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=velocity

# Quick demonstration
python demo_simple.py
```

Test coverage: 26/26 unit tests passing, all integration tests passing.

---

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[PARADIGM.md](PARADIGM.md)** - The Velocity paradigm explained
- **[ALGORITHMIC_CORE.md](ALGORITHMIC_CORE.md)** - Detailed algorithm documentation
- **[REAL_WEB_SEARCH.md](REAL_WEB_SEARCH.md)** - Web search implementation details

---

## Contributing

Contributions are welcome. Please ensure:

1. All tests pass
2. Code follows existing style
3. Documentation is updated
4. Commits are atomic and well-described

### Areas for Contribution

- Additional search engines (Brave, Startpage)
- Enhanced NLP models
- Performance optimization
- Multi-language support
- Edge deployment

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## The Velocity Paradigm

### From Storage to Access

Traditional AI focuses on storing knowledge in parameters. Velocity focuses on accessing knowledge quickly and evaluating it effectively.

### From Training to Reasoning

GPUs are used not for training, but for parallel hypothesis evaluation. This is computation-based reasoning, not parameter optimization.

### From Generation to Retrieval

Instead of generating text (which may hallucinate), Velocity retrieves and summarizes real content from verified sources.

### Core Insight

In the age of instant internet access:
- Storage is cheap
- Access is instant  
- Evaluation is the bottleneck

Velocity optimizes for evaluation speed, not storage size.

---

## Comparison

### vs GPT-4 / Claude

- **Advantage**: Always current, no hallucinations, full source tracking
- **Trade-off**: Slightly slower (1-3s vs instant), requires internet

### vs RAG (Retrieval-Augmented Generation)

- **Advantage**: No LLM dependency, better source verification, cheaper
- **Trade-off**: Less fluent prose generation

### vs Traditional Search Engines

- **Advantage**: Structured reasoning, confidence calibration, multi-source synthesis
- **Trade-off**: More complex implementation

---

## Status

**Version**: 0.3.0  
**Status**: Production Ready  
**Tests**: 26/26 passing  
**Documentation**: Complete

---

**Velocity** - Network-Native Intelligence

*Intelligence through interrogation, not memorization.*
