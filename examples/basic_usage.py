"""
Basic Usage Example

Demonstrates the Velocity Paradigm in action.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from velocity import VelocityEngine
from loguru import logger


async def main():
    """Basic usage example"""
    
    logger.info("=" * 60)
    logger.info("VELOCITY PARADIGM - Basic Usage Example")
    logger.info("=" * 60)
    
    # Initialize Velocity Engine
    engine = VelocityEngine(
        max_parallel_queries=3,
        max_iterations=5,
        confidence_threshold=0.7,
        use_gpu=False  # Set to True if you have GPU
    )
    
    # Example query
    query = "What is quantum computing?"
    
    logger.info(f"\nQuery: {query}\n")
    
    # Interrogate the network
    result = await engine.interrogate(query)
    
    # Display results
    logger.info("\n" + "=" * 60)
    logger.info("RESULTS")
    logger.info("=" * 60)
    
    print(f"\nQuery: {result['query']}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nConfidence: {result['confidence']:.1%}")
    print(f"Evidence pieces: {result['evidence_count']}")
    print(f"Sources accessed: {len(result['sources'])}")
    print(f"Contradictions found: {result['contradictions']}")
    print(f"Iterations: {result['iterations']}")
    
    # Display cognitive state
    state = result['state']
    print(f"\nCognitive State:")
    print(f"  - Topics explored: {len(state.knowledge)}")
    print(f"  - Queries made: {len(state.queries_made)}")
    print(f"  - Uncertainty level: {state.uncertainty.name}")
    
    # Display engine statistics
    stats = engine.get_state_summary()
    print(f"\nEngine Statistics:")
    print(f"  Network Interrogator:")
    print(f"    - Queries executed: {stats['interrogator']['queries_executed']}")
    print(f"    - Avg latency: {stats['interrogator']['avg_latency']:.3f}s")
    print(f"    - Success rate: {stats['interrogator']['success_rate']:.1%}")
    print(f"  Hypothesis Evaluator:")
    print(f"    - Hypotheses evaluated: {stats['evaluator']['hypotheses_evaluated']}")
    print(f"    - Using GPU: {stats['evaluator']['using_gpu']}")
    
    logger.success("\nVelocity Paradigm demonstration complete!")
    
    # Show key insight
    print("\n" + "=" * 60)
    print("KEY INSIGHT:")
    print("=" * 60)
    print("""
Intelligence didn't come from training on data.
It came from:
  1. Speed of network interrogation
  2. Quality of hypothesis evaluation
  3. Sophisticated state management

This is the Velocity Paradigm:
Network-native, dataset-free general intelligence.
    """)


if __name__ == "__main__":
    asyncio.run(main())
