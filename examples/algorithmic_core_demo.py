"""
Velocity Algorithmic Core Demo

Bu "yüksek seviye laf" değil, çalışan koddur.

Algoritmik adımlar:
1. Intent Parsing
2. Epistemic Routing
3. Hypothesis Generation
4. Network Interrogation Loop
5. Contradiction Handling
6. Hypothesis Elimination
7. State Synthesis
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from velocity.core.velocity_core import VelocityCore
from loguru import logger


async def main():
    """Algoritmik çekirdeği göster"""
    
    print("\n" + "=" * 70)
    print(" " * 15 + "VELOCITY ALGORITHMIC CORE")
    print(" " * 10 + "Gerçek Algoritmik İmplementasyon")
    print("=" * 70)
    
    # Initialize Core
    core = VelocityCore(
        max_hypotheses=3,                # 3 paralel hipotez
        confidence_threshold=0.7,        # %70 confidence'ta dur
        max_iterations=5,                # Hipotez başına max 5 iterasyon
        budget_per_hypothesis=5.0,       # Her hipotez için 5 birim bütçe
        routing_budget=10.0              # Routing için 10 birim bütçe
    )
    
    # Test query
    query = "What is quantum computing and how does it differ from classical computing?"
    
    print(f"\n📝 Query: {query}")
    print("\n" + "-" * 70)
    
    # ============================================
    # STEP 0: Can this be answered?
    # ============================================
    print("\n[0] PRE-CHECK: Can this be answered?")
    print("-" * 70)
    
    can_answer_result = await core.can_answer(query)
    
    print(f"Answerable: {can_answer_result['answerable']}")
    print(f"Confidence: {can_answer_result['confidence']:.2f}")
    print(f"Reason: {can_answer_result['reason']}")
    print(f"Estimated cost: {can_answer_result['estimated_cost']:.2f}")
    print(f"Estimated time: {can_answer_result['estimated_time']:.2f}s")
    print(f"Strategies: {', '.join(can_answer_result['strategies'])}")
    
    if not can_answer_result['answerable']:
        print("\n❌ Query cannot be answered with available resources.")
        return
    
    print("\n✅ Query can be answered. Proceeding with execution...")
    
    # ============================================
    # MAIN EXECUTION
    # ============================================
    print("\n" + "=" * 70)
    print("MAIN EXECUTION")
    print("=" * 70)
    
    result = await core.execute(query, system_goal="answer")
    
    # ============================================
    # RESULTS DISPLAY
    # ============================================
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\n📊 Decision:")
    print("-" * 70)
    print(result['decision'])
    
    print(f"\n📈 Confidence Metrics:")
    print("-" * 70)
    print(f"  Overall Confidence: {result['confidence']:.2%}")
    print(f"  Confidence Interval: {result['confidence_interval'][0]:.2%} - {result['confidence_interval'][1]:.2%}")
    print(f"  Uncertainty Level: {result['uncertainty']}")
    
    print(f"\n🔬 Evidence:")
    print("-" * 70)
    print(f"  Total pieces: {len(result['evidence'])}")
    for i, evidence in enumerate(result['evidence'][:5], 1):
        print(f"\n  {i}. [{evidence['source']}] (confidence: {evidence['confidence']:.2%})")
        print(f"     {evidence['content']}")
    
    if result['contradictions']:
        print(f"\n⚠️  Contradictions:")
        print("-" * 70)
        print(f"  Found: {len(result['contradictions'])}")
        for i, contradiction in enumerate(result['contradictions'], 1):
            print(f"\n  {i}. Severity: {contradiction['severity']:.2f}")
            print(f"     A: {contradiction['claim_a']}")
            print(f"        (from {contradiction['source_a']})")
            print(f"     B: {contradiction['claim_b']}")
            print(f"        (from {contradiction['source_b']})")
    else:
        print(f"\n✅ No contradictions detected")
    
    if result['alternatives']:
        print(f"\n🔀 Alternatives:")
        print("-" * 70)
        for i, alternative in enumerate(result['alternatives'], 1):
            print(f"  {i}. {alternative}")
    
    print(f"\n📚 Sources:")
    print("-" * 70)
    for source, count in result['source_breakdown'].items():
        print(f"  • {source}: {count} queries")
    
    print(f"\n🧪 Hypotheses:")
    print("-" * 70)
    print(f"  Total generated: {result['hypotheses']['total']}")
    print(f"  Survived: {result['hypotheses']['surviving']}")
    print(f"  Eliminated: {result['hypotheses']['eliminated']}")
    
    print(f"\n🎯 Intent Analysis:")
    print("-" * 70)
    print(f"  Goal: {result['intent']['goal']}")
    print(f"  Type: {result['intent']['type']}")
    print(f"  Initial Uncertainty: {result['intent']['uncertainty']:.2f}")
    print(f"  Subgoals: {len(result['intent']['subgoals'])}")
    
    # ============================================
    # KEY INSIGHT
    # ============================================
    print("\n" + "=" * 70)
    print("KEY INSIGHT")
    print("=" * 70)
    print("""
Bu bir LLM cevabı değil, HESAPLANMIŞ bir sonuçtur.

Fark:
  LLM:      "Bu soruya cevap üret"
  Velocity: "Bu soruya cevap üretilebilir mi?"

Velocity:
  ✓ Daha az konuşur
  ✓ Daha çok hesaplar  
  ✓ Daha az emin görünür
  ✓ Ama epistemik olarak daha sağlamdır

Her iddia:
  • Kaynaklıdır
  • Güven skorlu
  • Çelişkiler not edilmiş
  • Alternatifler belirtilmiş

Bu "yüksek seviye laf" değil.
Bu çalışan, modüler, ölçeklenebilir bir algoritmik iskelet.
    """)
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)


async def demonstrate_each_step():
    """Her adımı ayrı ayrı göster"""
    
    print("\n" + "=" * 70)
    print("STEP-BY-STEP DEMONSTRATION")
    print("=" * 70)
    
    query = "Is coffee healthy?"
    
    from velocity import (
        IntentParser,
        EpistemicRouter,
        HypothesisGenerator
    )
    
    # Step 1: Intent Parsing
    print("\n[1] INTENT PARSING")
    print("-" * 70)
    parser = IntentParser()
    intent = parser.parse(query)
    print(f"Goal: {intent.goal}")
    print(f"Type: {intent.decision_type.value}")
    print(f"Uncertainty: {intent.uncertainty:.2f}")
    print(f"Subgoals: {intent.subgoals}")
    
    # Step 2: Epistemic Routing
    print("\n[2] EPISTEMIC ROUTING")
    print("-" * 70)
    router = EpistemicRouter()
    strategies = router.route(intent, max_strategies=3)
    print(f"Selected {len(strategies)} strategies:")
    for s in strategies:
        print(f"  • {s.source_type.value}")
        print(f"    Score: {s.compute_score():.2f}")
        print(f"    Trust: {s.trust_score:.2f}")
        print(f"    Cost: {s.cost:.2f}")
    
    # Step 3: Hypothesis Generation
    print("\n[3] HYPOTHESIS GENERATION")
    print("-" * 70)
    generator = HypothesisGenerator(max_hypotheses=3)
    hypotheses = generator.generate(intent, strategies)
    print(f"Generated {len(hypotheses)} hypotheses:")
    for h in hypotheses:
        print(f"  • {h.description}")
        print(f"    Assumptions: {', '.join(h.assumptions[:2])}")
    
    print("\n✅ Individual steps demonstrated")


if __name__ == "__main__":
    print("""
======================================================================
                 VELOCITY ALGORITHMIC CORE
                                                                      
  This is not "high-level talk".                                     
  This is working, modular, scalable algorithmic skeleton.           
======================================================================
    """)
    
    choice = input("\nSelect demo:\n  1. Full execution\n  2. Step-by-step\n  3. Both\n\nChoice [1]: ").strip() or "1"
    
    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        asyncio.run(demonstrate_each_step())
    elif choice == "3":
        asyncio.run(demonstrate_each_step())
        print("\n" + "=" * 70 + "\n")
        asyncio.run(main())
    else:
        print("Invalid choice")
