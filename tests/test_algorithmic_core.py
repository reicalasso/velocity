"""
Tests for Algorithmic Core Components

Her modül bağımsız test edilebilir.
"""

import pytest
import asyncio
from velocity.core.intent_parser import IntentParser, DecisionType
from velocity.core.epistemic_router import EpistemicRouter, SourceType
from velocity.core.hypothesis_generator import HypothesisGenerator
from velocity.core.hypothesis_eliminator import HypothesisEliminator, EliminationCriteria
from velocity.core.state_synthesizer import StateSynthesizer
from velocity.core.state import CognitiveState, Evidence


class TestIntentParser:
    """Test Intent Parsing"""
    
    def test_parse_factual_query(self):
        """Test factual query parsing"""
        parser = IntentParser()
        intent = parser.parse("What is quantum computing?")
        
        assert intent.decision_type == DecisionType.FACTUAL
        assert intent.uncertainty > 0.0
        assert "quantum computing" in intent.goal.lower()
    
    def test_parse_comparative_query(self):
        """Test comparative query parsing"""
        parser = IntentParser()
        intent = parser.parse("Compare Python vs JavaScript")
        
        assert intent.decision_type == DecisionType.COMPARATIVE
        assert len(intent.subgoals) >= 0
    
    def test_parse_predictive_query(self):
        """Test predictive query parsing"""
        parser = IntentParser()
        intent = parser.parse("Will AI replace programmers?")
        
        assert intent.decision_type == DecisionType.PREDICTIVE
        assert intent.uncertainty > 0.5  # Predictive queries should have high uncertainty
    
    def test_uncertainty_calculation(self):
        """Test uncertainty calculation"""
        parser = IntentParser()
        
        # Simple factual should have lower uncertainty
        intent1 = parser.parse("What is 2+2?")
        
        # Complex predictive should have higher uncertainty
        intent2 = parser.parse("Maybe AI will probably transform society?")
        
        assert intent2.uncertainty > intent1.uncertainty
    
    def test_subgoal_extraction(self):
        """Test subgoal extraction"""
        parser = IntentParser()
        intent = parser.parse("What is AI? How does it work? What are its applications?")
        
        # Should detect multiple questions
        assert len(intent.subgoals) > 0


class TestEpistemicRouter:
    """Test Epistemic Routing"""
    
    def test_route_factual_query(self):
        """Test routing for factual query"""
        parser = IntentParser()
        router = EpistemicRouter()
        
        intent = parser.parse("What is machine learning?")
        strategies = router.route(intent, max_strategies=5)
        
        assert len(strategies) > 0
        assert len(strategies) <= 5
        
        # Should prioritize encyclopedic and academic for factual
        source_types = [s.source_type for s in strategies]
        assert SourceType.ENCYCLOPEDIC in source_types or SourceType.ACADEMIC in source_types
    
    def test_route_predictive_query(self):
        """Test routing for predictive query"""
        parser = IntentParser()
        router = EpistemicRouter()
        
        intent = parser.parse("Will quantum computing replace classical computing?")
        strategies = router.route(intent, max_strategies=5)
        
        assert len(strategies) > 0
        
        # Predictive should include news and live data
        source_types = [s.source_type for s in strategies]
        # At least some current sources
        assert any(st in [SourceType.NEWS, SourceType.LIVE_DATA, SourceType.SOCIAL] 
                  for st in source_types)
    
    def test_strategy_scoring(self):
        """Test strategy scoring"""
        parser = IntentParser()
        router = EpistemicRouter()
        
        intent = parser.parse("What is Python?")
        strategies = router.route(intent, max_strategies=3)
        
        # Strategies should have scores
        for strategy in strategies:
            score = strategy.compute_score()
            assert 0.0 <= score <= 1.0
        
        # Should be sorted by score
        scores = [s.compute_score() for s in strategies]
        assert scores == sorted(scores, reverse=True)
    
    def test_budget_constraint(self):
        """Test budget constraint"""
        parser = IntentParser()
        router = EpistemicRouter()
        
        intent = parser.parse("What is AI?")
        strategies = router.route(intent, max_strategies=10, budget=5.0)
        
        # Total cost should not exceed budget
        total_cost = sum(s.cost for s in strategies)
        assert total_cost <= 5.0


class TestHypothesisGenerator:
    """Test Hypothesis Generation"""
    
    def test_generate_basic_hypotheses(self):
        """Test basic hypothesis generation"""
        parser = IntentParser()
        router = EpistemicRouter()
        generator = HypothesisGenerator(max_hypotheses=3)
        
        intent = parser.parse("What is quantum computing?")
        strategies = router.route(intent, max_strategies=3)
        
        hypotheses = generator.generate(intent, strategies)
        
        assert len(hypotheses) > 0
        assert len(hypotheses) <= 3
        
        # Each hypothesis should have required fields
        for h in hypotheses:
            assert h.id
            assert h.description
            assert h.assumptions
            assert h.source_strategy
            assert h.state
    
    def test_comparative_hypotheses(self):
        """Test hypothesis generation for comparative queries"""
        parser = IntentParser()
        router = EpistemicRouter()
        generator = HypothesisGenerator(max_hypotheses=5)
        
        intent = parser.parse("Python vs JavaScript: which is better?")
        strategies = router.route(intent, max_strategies=3)
        
        hypotheses = generator.generate(intent, strategies)
        
        # Should generate opposing hypotheses for comparative
        assert len(hypotheses) >= 2
    
    def test_hypothesis_forking(self):
        """Test hypothesis forking"""
        parser = IntentParser()
        router = EpistemicRouter()
        generator = HypothesisGenerator(max_hypotheses=3)
        
        intent = parser.parse("Is coffee healthy?")
        strategies = router.route(intent, max_strategies=2)
        
        hypotheses = generator.generate(intent, strategies)
        original = hypotheses[0]
        
        # Fork
        forked = generator.fork_hypothesis(original)
        
        assert forked.id != original.id
        assert forked.description != original.description
        assert "Forked from" in forked.description


class TestHypothesisEliminator:
    """Test Hypothesis Elimination"""
    
    def test_eliminate_low_confidence(self):
        """Test elimination of low confidence hypotheses"""
        from velocity.core.hypothesis_generator import Hypothesis
        from velocity.core.epistemic_router import SourceStrategy, SourceType
        
        # Create test hypotheses
        strategy = SourceStrategy(
            source_type=SourceType.ENCYCLOPEDIC,
            priority=0.5,
            query_template="test",
            trust_score=0.5,
            freshness_requirement="any",
            cost=1.0,
            expected_value=0.5
        )
        
        state1 = CognitiveState()
        # Add evidence to h1 so it passes min_evidence check
        state1.add_evidence("test", Evidence(content="test1", source="s1", confidence=0.8))
        state1.add_evidence("test", Evidence(content="test2", source="s2", confidence=0.8))
        
        h1 = Hypothesis(
            id="h1",
            description="Good hypothesis",
            assumptions=[],
            source_strategy=strategy,
            state=state1,
            confidence=0.8
        )
        
        state2 = CognitiveState()
        # Add evidence to h2 so it passes min_evidence check, but low confidence
        state2.add_evidence("test", Evidence(content="test3", source="s3", confidence=0.1))
        state2.add_evidence("test", Evidence(content="test4", source="s4", confidence=0.1))
        
        h2 = Hypothesis(
            id="h2",
            description="Bad hypothesis",
            assumptions=[],
            source_strategy=strategy,
            state=state2,
            confidence=0.1  # Very low
        )
        
        criteria = EliminationCriteria(min_confidence=0.3)
        eliminator = HypothesisEliminator(criteria)
        
        surviving, eliminated = eliminator.eliminate_weak([h1, h2])
        
        assert len(surviving) == 1
        assert len(eliminated) == 1
        assert surviving[0].id == "h1"
        assert eliminated[0].id == "h2"
    
    def test_ranking(self):
        """Test hypothesis ranking"""
        from velocity.core.hypothesis_generator import Hypothesis
        from velocity.core.epistemic_router import SourceStrategy, SourceType
        
        strategy = SourceStrategy(
            source_type=SourceType.ENCYCLOPEDIC,
            priority=0.5,
            query_template="test",
            trust_score=0.5,
            freshness_requirement="any",
            cost=1.0,
            expected_value=0.5
        )
        
        hypotheses = [
            Hypothesis(
                id=f"h{i}",
                description=f"Hypothesis {i}",
                assumptions=[],
                source_strategy=strategy,
                state=CognitiveState(),
                confidence=0.3 + i * 0.1  # Increasing confidence
            )
            for i in range(5)
        ]
        
        eliminator = HypothesisEliminator()
        ranked = eliminator.rank_hypotheses(hypotheses)
        
        # Should be sorted by score (roughly by confidence)
        confidences = [h.confidence for h in ranked]
        assert confidences == sorted(confidences, reverse=True)


class TestStateSynthesizer:
    """Test State Synthesis"""
    
    def test_synthesize_single_hypothesis(self):
        """Test synthesis with single hypothesis"""
        from velocity.core.hypothesis_generator import Hypothesis
        from velocity.core.epistemic_router import SourceStrategy, SourceType
        
        strategy = SourceStrategy(
            source_type=SourceType.ENCYCLOPEDIC,
            priority=0.5,
            query_template="test",
            trust_score=0.8,
            freshness_requirement="any",
            cost=1.0,
            expected_value=0.7
        )
        
        state = CognitiveState()
        evidence = Evidence(
            content="Test evidence content",
            source="test_source",
            confidence=0.8
        )
        state.add_evidence("test_topic", evidence)
        
        h = Hypothesis(
            id="h1",
            description="Test hypothesis",
            assumptions=["test assumption"],
            source_strategy=strategy,
            state=state,
            confidence=0.8
        )
        
        synthesizer = StateSynthesizer()
        final_state = synthesizer.synthesize([h], [])
        
        assert final_state.decision
        assert final_state.confidence > 0.0
        assert len(final_state.evidence_summary) > 0
    
    def test_synthesize_empty(self):
        """Test synthesis with no hypotheses"""
        synthesizer = StateSynthesizer()
        final_state = synthesizer.synthesize([], [])
        
        assert final_state.confidence == 0.0
        assert final_state.uncertainty_level == "UNKNOWN"
        assert "Unable to reach decision" in final_state.decision


@pytest.mark.asyncio
async def test_full_integration():
    """Integration test: full pipeline"""
    from velocity import VelocityCore
    
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.5,
        max_iterations=2,
        budget_per_hypothesis=2.0
    )
    
    # Simple query
    result = await core.execute("What is Python?")
    
    # Should have result
    assert result
    assert "decision" in result
    assert "confidence" in result
    assert "uncertainty" in result
    assert "intent" in result


@pytest.mark.asyncio
async def test_can_answer():
    """Test can_answer check"""
    from velocity import VelocityCore
    
    core = VelocityCore()
    
    result = await core.can_answer("What is machine learning?")
    
    assert "answerable" in result
    assert "confidence" in result
    assert "reason" in result
    assert isinstance(result["answerable"], bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
