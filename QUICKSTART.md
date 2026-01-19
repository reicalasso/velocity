# Velocity Quick Start Guide

**Get up and running in 5 minutes**

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/velocity.git
cd velocity
```

### Step 2: Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Velocity

```bash
pip install -e .
```

---

## Verification

```bash
# Run tests
pytest tests/

# Expected output: 26/26 tests passing
```

---

## Running Interactive Mode

### Option 1: Double-Click (Windows)

```
Double-click: START_INTERACTIVE.bat
```

### Option 2: Command Line

```bash
python interactive_velocity.py
```

---

## Example Session

```
VELOCITY - INTERACTIVE MODE
======================================================================

Commands:
  - Type a question and press Enter
  - Type 'exit' or 'quit' to exit
  - Type 'help' for help

======================================================================

[OK] Velocity ready! You can ask questions now.


[1] Your question: What is machine learning?

======================================================================
QUESTION: What is machine learning?
======================================================================

[PROCESSING...] Velocity is thinking...

[1/7] INTENT PARSING          
[2/7] EPISTEMIC ROUTING       
[3/7] HYPOTHESIS GENERATION   
[4/7] NETWORK INTERROGATION   (Real web search!)
[5/7] CONTRADICTION HANDLING  
[6/7] HYPOTHESIS ELIMINATION  
[7/7] STATE SYNTHESIS         

[ANSWER]
Machine learning is a subset of artificial intelligence that enables 
systems to learn and improve from experience without being explicitly 
programmed. It uses algorithms to identify patterns in data...

[DETAILS]
  Confidence: 78.0%
  Uncertainty: LOW
  Evidence count: 3 pieces
  Sources:
    - duckduckgo: 2 queries
    - wikipedia: 1 query

======================================================================

[2] Your question: _
```

---

## Example Queries

### Factual Questions

```
What is quantum computing?
Who invented Python?
Explain neural networks
```

### Code Generation

```
write python code
create fibonacci function
javascript example
```

### Comparative Analysis

```
compare Python vs JavaScript
difference between SQL and NoSQL
React vs Vue
```

### Procedural Questions

```
how to learn machine learning
steps to deploy web app
how does encryption work
```

---

## Configuration (Optional)

### Adding API Keys

For enhanced search results:

```bash
# Google Custom Search (optional)
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_CSE_ID="your-cse-id"

# Bing Search (optional)
export BING_API_KEY="your-bing-key"
```

**Note**: Without API keys, DuckDuckGo HTML scraping works automatically.

---

## Understanding Output

### Answer Format

```
[ANSWER]
<Main answer content>

[DETAILS]
  Confidence: 0-100% (How certain is Velocity?)
  Uncertainty: LOW/MEDIUM/HIGH (Epistemic uncertainty)
  Evidence count: Number of supporting evidence pieces
  Sources: Where information came from
```

### Confidence Levels

- **70-100%**: High confidence (multiple sources agree)
- **50-70%**: Medium confidence (some sources, limited evidence)
- **0-50%**: Low confidence (conflicting sources, high uncertainty)

### Uncertainty Levels

- **LOW**: Clear answer, sources agree
- **MEDIUM**: Some ambiguity, minor conflicts
- **HIGH**: Significant uncertainty, major contradictions

---

## Running Demos

### Simple Demo

```bash
python demo_simple.py
```

Quick test with one question.

### Multiple Questions Demo

```bash
python demo_quick.py
```

Several example questions.

---

## Troubleshooting

### "Module not found" Error

```bash
# Ensure Velocity is installed
pip install -e .
```

### Slow Performance

- First query is slower (initializes NLP models)
- Subsequent queries are faster (~1-3 seconds)

### Network Errors

- Check internet connection
- DuckDuckGo/Wikipedia may be temporarily unavailable
- Fallback systems will activate automatically

---

## Next Steps

### Further Documentation

- **[README.md](README.md)** - Full documentation
- **[PARADIGM.md](PARADIGM.md)** - The Velocity paradigm
- **[REAL_WEB_SEARCH.md](REAL_WEB_SEARCH.md)** - Web search details
- **[ALGORITHMIC_CORE.md](ALGORITHMIC_CORE.md)** - Algorithm details

### Python API

```python
from velocity.core.velocity_core import VelocityCore

# Initialize
core = VelocityCore(
    max_hypotheses=2,
    confidence_threshold=0.6,
    max_iterations=3
)

# Ask question
result = await core.execute("What is AI?")

# Access result
print(result['decision'])        # Answer
print(result['confidence'])      # 0.0-1.0
print(result['uncertainty'])     # LOW/MEDIUM/HIGH
print(result['source_breakdown']) # Sources used
```

### Customization

```python
# More hypotheses = more thorough (but slower)
core = VelocityCore(max_hypotheses=5)

# Higher threshold = only high-confidence answers
core = VelocityCore(confidence_threshold=0.8)

# More iterations = deeper search
core = VelocityCore(max_iterations=5)
```

---

## Command Reference

### Installation Commands

- `python -m venv venv` - Create virtual environment
- `pip install -r requirements.txt` - Install dependencies
- `pip install -e .` - Install Velocity
- `pytest tests/` - Run tests

### Runtime Commands

- `python interactive_velocity.py` - Start interactive mode
- `python demo_simple.py` - Quick demo

### Interactive Commands

- Type question → Get answer
- `help` → Show help
- `exit` or `quit` → Exit

---

## Key Features

- **No LLM dependency**: No hallucinations, only real sources
- **Real-time web search**: Always current information
- **7-step cognitive loop**: Transparent, auditable reasoning
- **Confidence calibration**: Honest about uncertainty
- **Multi-language support**: English, Turkish, and code generation

---

## Ready to Start

```bash
python interactive_velocity.py
```

**Velocity is ready to answer your questions**

---

*"Intelligence lives in the speed of interrogation, not in the size of memory."*

**Velocity - Network-Native Intelligence**
