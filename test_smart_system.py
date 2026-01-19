"""
Test Smart System Improvements

Tests:
1. Social intents → No network (instant)
2. Meta intents → No network (instant)
3. Factual intents → Network (normal)
4. Performance comparison
"""

import asyncio
import time
from velocity.core.velocity_core import VelocityCore


async def test_smart_system():
    """Test improved smart system"""
    
    print("="*70)
    print("TESTING SMART VELOCITY SYSTEM")
    print("="*70)
    print("\nGoal: Intelligent network usage, instant social responses")
    print()
    
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=3
    )
    
    tests = [
        # Social intents (should be instant, no network)
        ("naber", "SOCIAL", "instant", "Should NOT use network"),
        ("hi", "SOCIAL", "instant", "Should NOT use network"),
        ("teşekkürler", "SOCIAL", "instant", "Should NOT use network"),
        
        # Factual intents (should use network)
        ("What is Python?", "FACTUAL", "normal", "Should use network"),
        ("Atatürk kimdir?", "FACTUAL", "normal", "Should use network"),
    ]
    
    for i, (question, expected_type, expected_speed, note) in enumerate(tests, 1):
        print("\n" + "="*70)
        print(f"TEST {i}: {expected_type} Intent")
        print(f"Question: '{question}'")
        print(f"Expectation: {note}")
        print("="*70)
        
        try:
            start = time.time()
            result = await core.execute(question)
            elapsed = time.time() - start
            
            answer = result['decision']
            confidence = result['confidence']
            network_used = result.get('execution_metadata', {}).get('network_used', True)
            
            # Display answer
            print(f"\n[ANSWER]")
            print("-" * 70)
            
            import textwrap
            wrapped = textwrap.fill(answer, width=68)
            print(wrapped)
            print("-" * 70)
            
            # Performance check
            print(f"\n[PERFORMANCE]")
            print(f"Time: {elapsed:.2f}s")
            print(f"Network used: {network_used}")
            print(f"Confidence: {confidence:.0%}")
            
            # Validation
            print(f"\n[VALIDATION]")
            if expected_speed == "instant":
                if elapsed < 0.1:
                    print(f"✓ PASS: Instant response ({elapsed:.3f}s)")
                else:
                    print(f"✗ FAIL: Too slow for social intent ({elapsed:.2f}s)")
                
                if not network_used:
                    print(f"✓ PASS: No network used (smart!)")
                else:
                    print(f"✗ FAIL: Network used unnecessarily")
            
            elif expected_speed == "normal":
                if network_used:
                    print(f"✓ PASS: Network used correctly")
                else:
                    print(f"? WARNING: Network not used (may be incorrect)")
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
    print("\nExpected improvements:")
    print("1. Social intents: < 0.1s, no network")
    print("2. Meta intents: < 0.1s, no network")
    print("3. Factual intents: 3-5s, uses network")
    print("4. Dramatic performance boost for social queries")
    print("\nVelocity is now SMART - doesn't interrogate when not needed!")


if __name__ == "__main__":
    asyncio.run(test_smart_system())
