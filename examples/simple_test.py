"""
Simple Test - Velocity Algorithmic Core

Basit test - emoji yok, ozel karakter yok.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from velocity.core.velocity_core import VelocityCore


async def main():
    print("\n" + "=" * 70)
    print("VELOCITY ALGORITHMIC CORE - SIMPLE TEST")
    print("=" * 70)
    
    # Initialize
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=3,
        budget_per_hypothesis=3.0
    )
    
    # Test query
    query = "What is Python programming language?"
    
    print(f"\n[Q] Query: {query}")
    print("-" * 70)
    
    # Execute
    print("\n[*] Executing Velocity Core...")
    result = await core.execute(query)
    
    # Results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\nDecision: {result['decision'][:200]}...")
    print(f"\nConfidence: {result['confidence']:.2%}")
    print(f"Uncertainty: {result['uncertainty']}")
    print(f"Evidence pieces: {result['evidence'].__len__()}")
    print(f"Contradictions: {result['contradictions'].__len__()}")
    print(f"Hypotheses (total/surviving/eliminated): "
          f"{result['hypotheses']['total']}/"
          f"{result['hypotheses']['surviving']}/"
          f"{result['hypotheses']['eliminated']}")
    
    print("\n" + "=" * 70)
    print("[OK] TEST COMPLETE")
    print("=" * 70)
    
    print("\nKEY INSIGHT:")
    print("  LLM:      'Bu soruya cevap uret'")
    print("  Velocity: 'Bu soruya cevap uretilebilir mi?'")
    print("\nVelocity:")
    print("  [+] Daha az konusur")
    print("  [+] Daha cok hesaplar")
    print("  [+] Daha az emin gorunur")
    print("  [+] Ama epistemik olarak daha saglamdir")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted")
