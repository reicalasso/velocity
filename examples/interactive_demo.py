"""
Interactive Velocity Demo

An interactive demonstration of the Velocity Paradigm.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from velocity import VelocityEngine
from loguru import logger


class VelocityDemo:
    """Interactive Velocity demonstration"""
    
    def __init__(self):
        self.engine = VelocityEngine(
            max_parallel_queries=3,
            max_iterations=5,
            confidence_threshold=0.7,
            use_gpu=False
        )
    
    def print_header(self):
        """Print demo header"""
        print("\n" + "=" * 70)
        print(" " * 20 + "VELOCITY PARADIGM")
        print(" " * 10 + "Network-Native, Dataset-Free General Intelligence")
        print("=" * 70)
        print("\nKey Concepts:")
        print("  • Intelligence = Speed of interrogation, not size of memory")
        print("  • Knowledge lives in the network, not in weights")
        print("  • Contradictions are signals, not errors")
        print("  • State-driven, not token-driven")
        print("=" * 70)
    
    def print_menu(self):
        """Print menu options"""
        print("\n" + "-" * 70)
        print("Options:")
        print("  1. Quick query (default)")
        print("  2. Detailed query (with state inspection)")
        print("  3. Contradiction demo (controversial topic)")
        print("  4. Uncertainty demo (ambiguous topic)")
        print("  5. Custom configuration")
        print("  q. Quit")
        print("-" * 70)
    
    async def quick_query(self, query: str = None):
        """Execute a quick query"""
        if not query:
            query = input("\nEnter your question: ").strip()
        
        if not query:
            return
        
        print(f"\n🔍 Interrogating network for: '{query}'")
        print("⏳ Processing...\n")
        
        result = await self.engine.interrogate(query)
        
        print("=" * 70)
        print("RESULT")
        print("=" * 70)
        print(f"\n{result['answer']}")
        print(f"\n📊 Confidence: {result['confidence']:.1%}")
        print(f"📚 Sources: {len(result['sources'])}")
        print(f"🔬 Evidence pieces: {result['evidence_count']}")
        print(f"⚠️  Contradictions: {result['contradictions']}")
        print(f"🔄 Iterations: {result['iterations']}")
    
    async def detailed_query(self, query: str = None):
        """Execute query with detailed state inspection"""
        if not query:
            query = input("\nEnter your question: ").strip()
        
        if not query:
            return
        
        print(f"\n🔍 Interrogating network for: '{query}'")
        print("⏳ Processing with state tracking...\n")
        
        result = await self.engine.interrogate(query)
        state = result['state']
        
        print("=" * 70)
        print("RESULT")
        print("=" * 70)
        print(f"\n{result['answer']}")
        
        print("\n" + "-" * 70)
        print("COGNITIVE STATE")
        print("-" * 70)
        print(f"\n📊 Overall Confidence: {state.confidence:.1%}")
        print(f"🎯 Uncertainty Level: {state.uncertainty.name}")
        print(f"📚 Topics Explored: {len(state.knowledge)}")
        print(f"🔍 Queries Made: {len(state.queries_made)}")
        print(f"🌐 Sources Accessed: {len(state.sources_accessed)}")
        
        if state.contradictions:
            print(f"\n⚠️  Contradictions Detected: {len(state.contradictions)}")
            for i, contradiction in enumerate(state.contradictions[:3], 1):
                print(f"\n  {i}. Severity: {contradiction.severity:.2f}")
                print(f"     A: {contradiction.claim_a[:60]}...")
                print(f"        (from {contradiction.source_a})")
                print(f"     B: {contradiction.claim_b[:60]}...")
                print(f"        (from {contradiction.source_b})")
        
        print("\n" + "-" * 70)
        print("EVIDENCE BREAKDOWN")
        print("-" * 70)
        for topic, evidence_list in state.knowledge.items():
            print(f"\n📂 {topic}:")
            for i, evidence in enumerate(evidence_list[:5], 1):
                print(f"  {i}. [{evidence.source}] "
                      f"Confidence: {evidence.confidence:.1%}")
                print(f"     {evidence.content[:80]}...")
        
        print("\n" + "-" * 70)
        print("ENGINE STATISTICS")
        print("-" * 70)
        stats = self.engine.get_state_summary()
        print(f"\nNetwork Interrogator:")
        print(f"  • Queries executed: {stats['interrogator']['queries_executed']}")
        print(f"  • Avg latency: {stats['interrogator']['avg_latency']:.3f}s")
        print(f"  • Success rate: {stats['interrogator']['success_rate']:.1%}")
        print(f"\nHypothesis Evaluator:")
        print(f"  • Hypotheses evaluated: {stats['evaluator']['hypotheses_evaluated']}")
        print(f"  • Using GPU: {stats['evaluator']['using_gpu']}")
    
    async def contradiction_demo(self):
        """Demonstrate contradiction handling"""
        print("\n" + "=" * 70)
        print("CONTRADICTION DETECTION DEMO")
        print("=" * 70)
        print("\nContradictions are not errors in Velocity.")
        print("They are signals of information density and multiple perspectives.")
        
        topics = [
            "Is coffee healthy?",
            "Is nuclear energy safe?",
            "Should AI be regulated?"
        ]
        
        print("\nSuggested controversial topics:")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic}")
        print(f"  {len(topics)+1}. Custom topic")
        
        choice = input("\nSelect topic (1-4): ").strip()
        
        if choice == str(len(topics)+1):
            query = input("Enter your controversial question: ").strip()
        elif choice.isdigit() and 1 <= int(choice) <= len(topics):
            query = topics[int(choice)-1]
        else:
            query = topics[0]
        
        print(f"\n🔍 Interrogating: '{query}'")
        print("⏳ Searching for different perspectives...\n")
        
        result = await self.engine.interrogate(query)
        state = result['state']
        
        print("=" * 70)
        print("CONTRADICTIONS FOUND")
        print("=" * 70)
        
        if state.contradictions:
            print(f"\n✓ Found {len(state.contradictions)} contradictions")
            print("(This shows multiple perspectives exist - not a bug!)\n")
            
            for i, contradiction in enumerate(state.contradictions, 1):
                print(f"\n{i}. Severity: {contradiction.severity:.2f}")
                print(f"   Position A: {contradiction.claim_a[:70]}...")
                print(f"   Source: {contradiction.source_a}")
                print(f"\n   Position B: {contradiction.claim_b[:70]}...")
                print(f"   Source: {contradiction.source_b}")
                print()
        else:
            print("\n✗ No contradictions detected")
            print("(Topic may have consensus or need more diverse sources)")
        
        print(f"\n📊 Overall Confidence: {state.confidence:.1%}")
        print("(Lower confidence expected when contradictions exist)")
    
    async def uncertainty_demo(self):
        """Demonstrate uncertainty tracking"""
        print("\n" + "=" * 70)
        print("UNCERTAINTY TRACKING DEMO")
        print("=" * 70)
        print("\nVelocity explicitly tracks uncertainty.")
        print("Uncertainty guides when to search more vs when to conclude.")
        
        query = input("\nEnter your question: ").strip()
        
        if not query:
            query = "What is the meaning of life?"
        
        print(f"\n🔍 Interrogating: '{query}'")
        print("⏳ Tracking uncertainty...\n")
        
        result = await self.engine.interrogate(query)
        state = result['state']
        
        print("=" * 70)
        print("UNCERTAINTY ANALYSIS")
        print("=" * 70)
        
        print(f"\n📊 Confidence: {state.confidence:.1%}")
        print(f"🎯 Uncertainty: {state.uncertainty.name}")
        
        print("\nUncertainty breakdown:")
        for topic, uncertainty_value in state.uncertainty_map.items():
            print(f"  • {topic}: {uncertainty_value:.2f}")
        
        print(f"\n📚 Evidence collected: {result['evidence_count']}")
        print(f"🌐 Sources accessed: {len(state.sources_accessed)}")
        print(f"🔄 Iterations used: {result['iterations']}")
        
        print("\n💡 Interpretation:")
        if state.confidence > 0.7:
            print("  High confidence - strong evidence from multiple sources")
        elif state.confidence > 0.4:
            print("  Moderate confidence - some evidence but gaps remain")
        else:
            print("  Low confidence - limited or conflicting evidence")
    
    async def custom_config(self):
        """Configure engine parameters"""
        print("\n" + "=" * 70)
        print("CUSTOM CONFIGURATION")
        print("=" * 70)
        
        print("\nCurrent configuration:")
        print(f"  • Max parallel queries: {self.engine.max_parallel_queries}")
        print(f"  • Max iterations: {self.engine.max_iterations}")
        print(f"  • Confidence threshold: {self.engine.confidence_threshold}")
        print(f"  • Use GPU: {self.engine.evaluator.use_gpu}")
        
        print("\nNew configuration (press Enter to keep current):")
        
        parallel = input(f"  Max parallel queries [{self.engine.max_parallel_queries}]: ").strip()
        iterations = input(f"  Max iterations [{self.engine.max_iterations}]: ").strip()
        threshold = input(f"  Confidence threshold [{self.engine.confidence_threshold}]: ").strip()
        
        # Apply new configuration
        if parallel:
            self.engine.max_parallel_queries = int(parallel)
        if iterations:
            self.engine.max_iterations = int(iterations)
        if threshold:
            self.engine.confidence_threshold = float(threshold)
        
        print("\n✓ Configuration updated!")
        print("\nNew configuration:")
        print(f"  • Max parallel queries: {self.engine.max_parallel_queries}")
        print(f"  • Max iterations: {self.engine.max_iterations}")
        print(f"  • Confidence threshold: {self.engine.confidence_threshold}")
    
    async def run(self):
        """Run interactive demo"""
        self.print_header()
        
        while True:
            self.print_menu()
            choice = input("\nSelect option [1]: ").strip() or "1"
            
            try:
                if choice == "q" or choice.lower() == "quit":
                    print("\n👋 Goodbye! Remember: Intelligence = Speed of interrogation")
                    break
                elif choice == "1":
                    await self.quick_query()
                elif choice == "2":
                    await self.detailed_query()
                elif choice == "3":
                    await self.contradiction_demo()
                elif choice == "4":
                    await self.uncertainty_demo()
                elif choice == "5":
                    await self.custom_config()
                else:
                    print("\n❌ Invalid option. Please try again.")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\n❌ Error occurred: {e}")
        
        print()


async def main():
    """Main entry point"""
    demo = VelocityDemo()
    await demo.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
