"""
Test natural, ChatGPT-like answers

After improvements, answers should be:
1. Readable (proper spacing)
2. Natural (flowing sentences)
3. Formatted (word-wrapped, clean)
4. No concatenated words
"""

import asyncio
from velocity.core.velocity_core import VelocityCore


async def test_natural_answers():
    """Test improved answer quality"""
    
    print("="*70)
    print("TESTING NATURAL ANSWER GENERATION")
    print("="*70)
    print("\nGoal: Answers like ChatGPT/Claude (no LLM used!)")
    print()
    
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=3
    )
    
    tests = [
        ("What is Python?", "English technical"),
        ("Python nedir?", "Turkish technical"),
        ("What is quantum computing?", "English scientific"),
        ("Ankara Üniversitesi nedir?", "Turkish factual"),
    ]
    
    for i, (question, category) in enumerate(tests, 1):
        print("\n" + "="*70)
        print(f"TEST {i}: {category}")
        print(f"Question: {question}")
        print("="*70)
        
        try:
            result = await core.execute(question)
            
            answer = result['decision']
            
            # Check quality
            issues = []
            
            # Check for concatenated words
            import re
            if re.search(r'[a-z][A-Z]', answer):
                issues.append("- Concatenated camelCase words found")
            
            # Check for missing spaces after punctuation
            if re.search(r'[,;:][A-Z]', answer):
                issues.append("- Missing spaces after punctuation")
            
            # Check for very long words (likely concatenation)
            words = answer.split()
            long_words = [w for w in words if len(w) > 30]
            if long_words:
                issues.append(f"- Very long words found: {len(long_words)}")
            
            # Display answer
            print("\n[ANSWER]")
            print("-" * 70)
            
            import textwrap
            wrapped = textwrap.fill(answer, width=68)
            print(wrapped)
            print("-" * 70)
            
            # Quality assessment
            print("\n[QUALITY CHECK]")
            if issues:
                print("Issues found:")
                for issue in issues:
                    print(issue)
            else:
                print("✓ No issues found - natural and readable!")
            
            # Confidence
            conf = result['confidence']
            print(f"Confidence: {conf:.0%}")
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
    print("\nExpected improvements:")
    print("1. No concatenated words (Quantumcomputing → Quantum computing)")
    print("2. Proper spacing after punctuation")
    print("3. Natural sentence flow")
    print("4. Readable, word-wrapped output")
    print("5. ChatGPT-like quality (without LLM!)")


if __name__ == "__main__":
    asyncio.run(test_natural_answers())
