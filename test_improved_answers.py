"""
Test improved answer synthesis

System should now provide:
1. User-friendly answers (not just raw scraping)
2. Multi-source synthesis
3. NLP summarization
4. Different answers for repeated queries (varied sources)
"""

import asyncio
from velocity.core.velocity_core import VelocityCore


async def test_improved_answers():
    """Test improved answer synthesis"""
    
    print("="*70)
    print("TESTING IMPROVED ANSWER SYNTHESIS")
    print("="*70)
    
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=3
    )
    
    # Test 1: Factual question
    print("\n" + "="*70)
    print("TEST 1: Factual Question")
    print("="*70)
    
    result = await core.execute("What is Python programming language?")
    
    print("\n[ANSWER]")
    print(result['decision'])
    print(f"\nConfidence: {result['confidence']:.1%}")
    print(f"Uncertainty: {result['uncertainty']}")
    
    # Test 2: Same question again (should get varied answer)
    print("\n\n" + "="*70)
    print("TEST 2: Same Question (Checking Variation)")
    print("="*70)
    
    result2 = await core.execute("What is Python programming language?")
    
    print("\n[ANSWER]")
    print(result2['decision'])
    print(f"\nConfidence: {result2['confidence']:.1%}")
    print(f"Uncertainty: {result2['uncertainty']}")
    
    # Compare answers
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    
    if result['decision'] == result2['decision']:
        print("WARNING: Answers are identical (no variation)")
    else:
        print("GOOD: Answers show variation")
        
        # Check if they're meaningfully different
        words1 = set(result['decision'].lower().split())
        words2 = set(result2['decision'].lower().split())
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        print(f"Word overlap: {overlap:.1%}")
    
    # Test 3: Turkish question
    print("\n\n" + "="*70)
    print("TEST 3: Turkish Question")
    print("="*70)
    
    result3 = await core.execute("Python nedir?")
    
    print("\n[ANSWER]")
    print(result3['decision'])
    print(f"\nConfidence: {result3['confidence']:.1%}")
    print(f"Uncertainty: {result3['uncertainty']}")
    
    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70)
    
    print("\nKey improvements to check:")
    print("1. Answers are readable and user-friendly")
    print("2. Not just raw URLs and snippets")
    print("3. Multi-source synthesis")
    print("4. Some variation in repeated queries")


if __name__ == "__main__":
    asyncio.run(test_improved_answers())
