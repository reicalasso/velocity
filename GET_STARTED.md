# Get Started with Velocity

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Environment

```powershell
# Navigate to project
cd velocity

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Or activate (Linux/Mac)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Your First Query

```powershell
python examples\basic_usage.py
```

You should see Velocity interrogating the network and providing an answer!

### Step 3: Try Interactive Demo

```powershell
python examples\interactive_demo.py
```

This gives you a menu-driven interface to explore Velocity's capabilities.

## 📚 What to Read First

### New to Velocity?
1. **README.md** - Overview of the project
2. **PARADIGM.md** - The core philosophy (Turkish)
3. **QUICKSTART.md** - Detailed quick start guide

### Want to Understand Deeply?
1. **PHILOSOPHY.md** - Philosophical foundations
2. **ARCHITECTURE.md** - Technical architecture
3. **COMPARISON.md** - Velocity vs Traditional AI

### Ready to Code?
1. **examples/basic_usage.py** - Simple example
2. **examples/interactive_demo.py** - Full demo
3. **velocity/** - Source code

## 🎯 Your First Custom Query

Create a file `my_query.py`:

```python
import asyncio
from velocity import VelocityEngine

async def main():
    # Initialize engine
    engine = VelocityEngine(
        max_parallel_queries=3,
        max_iterations=5,
        confidence_threshold=0.7
    )
    
    # Your question here
    result = await engine.interrogate("What is artificial intelligence?")
    
    # Display result
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nConfidence: {result['confidence']:.1%}")
    print(f"Sources: {len(result['sources'])}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```powershell
python my_query.py
```

## 🔧 Configuration Options

### Via Code

```python
engine = VelocityEngine(
    max_parallel_queries=5,      # More = faster but more network load
    max_iterations=10,            # More = more thorough but slower
    confidence_threshold=0.7,     # Higher = more confident answers required
    use_gpu=False                # True if you have CUDA-enabled GPU
)
```

### Via Environment File

Copy `env.example` to `.env` and modify:

```bash
MAX_PARALLEL_QUERIES=5
MAX_ITERATIONS=10
CONFIDENCE_THRESHOLD=0.7
USE_GPU=false
```

Then in code:
```python
from dotenv import load_dotenv
import os

load_dotenv()

engine = VelocityEngine(
    max_parallel_queries=int(os.getenv('MAX_PARALLEL_QUERIES', 5)),
    # ... etc
)
```

## 🧪 Running Tests

```powershell
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_state.py -v

# Run with output
pytest tests/ -v -s
```

## 📊 Understanding Results

### Result Structure

Every interrogation returns:

```python
{
    "query": str,              # Your question
    "answer": str,             # Synthesized answer
    "confidence": float,       # 0.0 to 1.0
    "evidence_count": int,     # Number of evidence pieces
    "sources": List[str],      # Sources accessed
    "contradictions": int,     # Number of contradictions found
    "iterations": int,         # Search iterations used
    "state": CognitiveState    # Full cognitive state
}
```

### Confidence Levels

- **0.0 - 0.3**: Low (uncertain)
- **0.3 - 0.6**: Moderate
- **0.6 - 0.8**: Good
- **0.8 - 1.0**: High

### Inspecting State

```python
state = result['state']

# What was searched
print(state.queries_made)

# What sources were used
print(state.sources_accessed)

# What contradictions exist
for contradiction in state.contradictions:
    print(f"{contradiction.claim_a} vs {contradiction.claim_b}")

# Uncertainty level
print(state.uncertainty.name)  # CERTAIN, LOW, MEDIUM, HIGH, UNKNOWN
```

## 🎨 Example Use Cases

### 1. Fact Checking

```python
result = await engine.interrogate("Did event X happen on date Y?")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Sources: {result['sources']}")
```

### 2. Research Synthesis

```python
result = await engine.interrogate("What are the main theories about topic X?")
state = result['state']
for evidence in state.knowledge.values():
    print(f"Source: {evidence.source}")
    print(f"Content: {evidence.content}")
```

### 3. Contradiction Detection

```python
result = await engine.interrogate("Is coffee healthy?")
if result['contradictions'] > 0:
    print("Multiple perspectives found!")
    for c in result['state'].contradictions:
        print(f"View 1: {c.claim_a}")
        print(f"View 2: {c.claim_b}")
```

### 4. Current Events

```python
# Traditional AI would be outdated
# Velocity is always current
result = await engine.interrogate("What happened today in [topic]?")
```

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError

```powershell
# Make sure you're in the right directory
cd velocity

# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Slow Queries

```python
# Reduce timeout or increase parallel queries
engine = VelocityEngine(
    max_parallel_queries=10,  # More parallel
    timeout=5.0                # Shorter timeout
)
```

### Issue: Low Confidence

```python
# Increase iterations or lower threshold
engine = VelocityEngine(
    max_iterations=15,         # More thorough
    confidence_threshold=0.5   # Lower bar
)
```

### Issue: Network Errors

```python
# Add error handling
try:
    result = await engine.interrogate(query)
except Exception as e:
    print(f"Error: {e}")
    # Fall back to cached results or try again
```

## 🔌 Extending Velocity

### Add Custom Network Source

```python
from velocity.network.interrogator import NetworkInterrogator

class MyInterrogator(NetworkInterrogator):
    async def _query_custom_source(self, query):
        # Your custom API call
        data = await my_api.search(query)
        return {
            "success": True,
            "query": query,
            "source": "my_api",
            "content": data.text,
            "metadata": {"url": data.url}
        }

# Use it
engine = VelocityEngine()
engine.interrogator = MyInterrogator()
```

### Custom Hypothesis Evaluator

```python
from velocity.evaluation.hypothesis import HypothesisEvaluator

class MyEvaluator(HypothesisEvaluator):
    async def _score_hypothesis(self, hypothesis, state):
        # Your custom scoring logic
        score = my_scoring_function(hypothesis, state)
        return score

engine.evaluator = MyEvaluator()
```

## 📖 Learning Path

### Beginner
1. Run `basic_usage.py`
2. Read `QUICKSTART.md`
3. Modify `my_query.py` with your questions
4. Explore result structure

### Intermediate
1. Read `ARCHITECTURE.md`
2. Understand cognitive state
3. Try `interactive_demo.py`
4. Inspect state and contradictions

### Advanced
1. Read `PHILOSOPHY.md`
2. Study source code in `velocity/`
3. Add custom sources
4. Implement custom evaluators
5. Contribute improvements

## 🎯 Next Steps

### After Getting Started

1. **Experiment**: Try different queries and configurations
2. **Understand**: Read the philosophy and architecture docs
3. **Extend**: Add your own network sources
4. **Contribute**: Improve the codebase

### Ideas to Try

- Query controversial topics (see contradictions)
- Query current events (see freshness)
- Query obscure topics (see uncertainty)
- Query with different configurations (see trade-offs)

### Build Something

- Fact-checking tool
- Research assistant
- News aggregator
- Question-answering system
- Knowledge explorer

## 📞 Getting Help

### Documentation
- `QUICKSTART.md` - Quick start guide
- `ARCHITECTURE.md` - Technical details
- `PHILOSOPHY.md` - Conceptual foundations
- `COMPARISON.md` - Velocity vs Traditional AI

### Code
- `velocity/` - Source code (well-commented)
- `examples/` - Working examples
- `tests/` - Test cases

### Issues
- Check existing issues
- Create new issue with:
  - What you tried
  - What happened
  - What you expected
  - Your configuration

## 🌟 Remember

### The Core Principle

> Intelligence lives in the speed of interrogation,
> not in the size of memory.

### The Key Difference

Traditional AI: Store everything, recall when needed
Velocity: Access anything, evaluate in real-time

### The Advantage

- Always current
- Always transparent
- Always honest about uncertainty

## 🚀 Ready?

You now have everything you need to use Velocity!

Start with:
```powershell
python examples\basic_usage.py
```

Then explore from there.

**Welcome to the Velocity Paradigm!** 🎉
