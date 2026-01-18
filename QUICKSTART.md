# Velocity Quick Start Guide

Get started with the Velocity Paradigm in 5 minutes.

## Installation

### 1. Clone or Download

```bash
cd velocity
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Install GPU Support

```bash
pip install torch torchvision
```

## Basic Usage

### Example 1: Simple Query

Create a file `my_first_query.py`:

```python
import asyncio
from velocity import VelocityEngine

async def main():
    # Initialize engine
    engine = VelocityEngine()
    
    # Ask a question
    result = await engine.interrogate("What is machine learning?")
    
    # Print answer
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']:.1%}")

asyncio.run(main())
```

Run it:

```bash
python my_first_query.py
```

### Example 2: With State Inspection

```python
import asyncio
from velocity import VelocityEngine

async def main():
    engine = VelocityEngine(
        max_parallel_queries=3,
        confidence_threshold=0.7
    )
    
    result = await engine.interrogate("How does photosynthesis work?")
    
    # Inspect cognitive state
    state = result['state']
    print(f"\nCognitive State:")
    print(f"  Confidence: {state.confidence:.2%}")
    print(f"  Sources: {len(state.sources_accessed)}")
    print(f"  Contradictions: {len(state.contradictions)}")
    print(f"  Uncertainty: {state.uncertainty.name}")
    
    # Show evidence
    for topic, evidence_list in state.knowledge.items():
        print(f"\n{topic}:")
        for evidence in evidence_list[:3]:
            print(f"  - {evidence.source}: {evidence.confidence:.1%}")

asyncio.run(main())
```

### Example 3: Exploring Contradictions

```python
import asyncio
from velocity import VelocityEngine

async def main():
    engine = VelocityEngine()
    
    # Query a controversial topic
    result = await engine.interrogate("Is coffee healthy?")
    
    state = result['state']
    
    print(f"Found {len(state.contradictions)} contradictions:\n")
    
    for contradiction in state.contradictions:
        print(f"Severity: {contradiction.severity:.2f}")
        print(f"  A: {contradiction.claim_a[:80]}...")
        print(f"     (from {contradiction.source_a})")
        print(f"  B: {contradiction.claim_b[:80]}...")
        print(f"     (from {contradiction.source_b})")
        print()

asyncio.run(main())
```

## Configuration

### Via Code

```python
engine = VelocityEngine(
    max_parallel_queries=5,      # Number of parallel searches
    max_iterations=10,            # Maximum search iterations
    confidence_threshold=0.7,     # Stop when confidence > this
    use_gpu=True                  # Use GPU for evaluation
)
```

### Via Environment Variables

Create `config.env`:

```bash
MAX_PARALLEL_QUERIES=5
MAX_ITERATIONS=10
CONFIDENCE_THRESHOLD=0.7
USE_GPU=true
```

Load in code:

```python
from dotenv import load_dotenv
import os

load_dotenv('config.env')

engine = VelocityEngine(
    max_parallel_queries=int(os.getenv('MAX_PARALLEL_QUERIES', 5)),
    use_gpu=os.getenv('USE_GPU', 'false').lower() == 'true'
)
```

## Understanding Results

### Result Structure

```python
{
    "query": "Your question",
    "answer": "Synthesized answer",
    "confidence": 0.75,                    # 0.0 to 1.0
    "evidence_count": 12,                  # Number of evidence pieces
    "sources": ["source1", "source2"],     # Sources accessed
    "contradictions": 2,                   # Number of contradictions
    "iterations": 5,                       # Search iterations used
    "state": CognitiveState(...)           # Full cognitive state
}
```

### Interpreting Confidence

- **0.0 - 0.3**: Low confidence, uncertain
- **0.3 - 0.6**: Moderate confidence
- **0.6 - 0.8**: Good confidence
- **0.8 - 1.0**: High confidence

### Working with State

```python
state = result['state']

# Check what was searched
print(state.queries_made)

# Check uncertainty for a topic
uncertainty = state.update_uncertainty("topic")
print(uncertainty.name)  # CERTAIN, LOW, MEDIUM, HIGH, UNKNOWN

# Get state summary
summary = state.get_summary()
print(summary)
```

## Advanced Usage

### Custom Network Sources

```python
from velocity.network.interrogator import NetworkInterrogator

class MyInterrogator(NetworkInterrogator):
    async def _execute_query(self, query, search_engine):
        if search_engine == "my_custom_source":
            # Implement custom source
            return await self._query_my_source(query)
        return await super()._execute_query(query, search_engine)

# Use custom interrogator
engine = VelocityEngine()
engine.interrogator = MyInterrogator()
```

### State Forking for Parallel Exploration

```python
state = CognitiveState()

# Fork for parallel hypothesis testing
branch1 = state.fork()
branch2 = state.fork()

# Explore different paths
await explore_hypothesis(branch1, "hypothesis_a")
await explore_hypothesis(branch2, "hypothesis_b")

# Compare results
if branch1.confidence > branch2.confidence:
    state = branch1
else:
    state = branch2
```

### Custom Hypothesis Evaluation

```python
from velocity.evaluation.hypothesis import HypothesisEvaluator

class MyEvaluator(HypothesisEvaluator):
    async def _score_hypothesis(self, hypothesis, state):
        # Custom scoring logic
        score = custom_score(hypothesis, state)
        return score

engine = VelocityEngine()
engine.evaluator = MyEvaluator()
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run specific test
pytest tests/test_state.py -v

# Run with coverage
pytest --cov=velocity tests/
```

## Example: Complete Application

```python
import asyncio
from velocity import VelocityEngine
from loguru import logger

class VelocityAssistant:
    def __init__(self):
        self.engine = VelocityEngine(
            max_parallel_queries=5,
            confidence_threshold=0.7,
            use_gpu=False
        )
    
    async def ask(self, question: str):
        """Ask a question and get detailed response"""
        logger.info(f"Question: {question}")
        
        result = await self.engine.interrogate(question)
        
        response = {
            "answer": result['answer'],
            "confidence": result['confidence'],
            "sources": result['sources'],
            "has_contradictions": result['contradictions'] > 0,
            "evidence_count": result['evidence_count']
        }
        
        return response
    
    async def interactive(self):
        """Interactive mode"""
        print("Velocity Assistant (type 'quit' to exit)")
        print("=" * 60)
        
        while True:
            question = input("\nYou: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
            
            result = await self.ask(question)
            
            print(f"\nVelocity: {result['answer']}")
            print(f"\n[Confidence: {result['confidence']:.1%} | "
                  f"Sources: {len(result['sources'])} | "
                  f"Evidence: {result['evidence_count']}]")

async def main():
    assistant = VelocityAssistant()
    await assistant.interactive()

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Issue: Slow queries

**Solution**: Increase parallel queries or reduce timeout

```python
engine = VelocityEngine(
    max_parallel_queries=10,  # More parallel
    timeout=5.0                # Shorter timeout
)
```

### Issue: Low confidence

**Solution**: Increase iterations or lower threshold

```python
engine = VelocityEngine(
    max_iterations=15,         # More iterations
    confidence_threshold=0.6   # Lower threshold
)
```

### Issue: GPU not working

**Solution**: Check PyTorch installation

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If False, install CUDA-enabled PyTorch:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

## Next Steps

1. **Read the paradigm**: `PARADIGM.md`
2. **Understand architecture**: `ARCHITECTURE.md`
3. **Explore examples**: `examples/`
4. **Run tests**: `pytest tests/`
5. **Build something!**

## Key Concepts to Remember

1. **Intelligence ≠ Storage**: Velocity doesn't store knowledge
2. **Speed Matters**: Fast interrogation > big memory
3. **Contradictions are OK**: They signal information density
4. **State-Driven**: Not token-by-token, but state-by-state
5. **Always Current**: Network updates automatically

## Getting Help

- Check `PARADIGM.md` for conceptual questions
- Check `ARCHITECTURE.md` for technical details
- Read code comments for implementation details
- Run examples for practical usage patterns

**Welcome to the Velocity Paradigm!**

> Intelligence lives in the speed of interrogation,
> not in the size of memory.
