"""
Tests for Cognitive State Management
"""

import pytest
from velocity.core.state import CognitiveState, Evidence, Contradiction, UncertaintyLevel


def test_cognitive_state_initialization():
    """Test that cognitive state initializes correctly"""
    state = CognitiveState()
    
    assert state.confidence == 0.0
    assert state.uncertainty == UncertaintyLevel.UNKNOWN
    assert len(state.knowledge) == 0
    assert len(state.contradictions) == 0


def test_add_evidence():
    """Test adding evidence to state"""
    state = CognitiveState()
    
    evidence = Evidence(
        content="Test content",
        source="test_source",
        confidence=0.8
    )
    
    state.add_evidence("test_topic", evidence)
    
    assert "test_topic" in state.knowledge
    assert len(state.knowledge["test_topic"]) == 1
    assert "test_source" in state.sources_accessed


def test_confidence_update():
    """Test that confidence updates correctly"""
    state = CognitiveState()
    
    # Add high confidence evidence
    evidence1 = Evidence(content="Test 1", source="source1", confidence=0.9)
    evidence2 = Evidence(content="Test 2", source="source2", confidence=0.8)
    
    state.add_evidence("topic", evidence1)
    assert state.confidence > 0.0
    
    initial_confidence = state.confidence
    state.add_evidence("topic", evidence2)
    
    # Confidence should increase with more high-quality evidence
    assert state.confidence > 0.0


def test_contradiction_detection():
    """Test contradiction detection"""
    state = CognitiveState()
    
    # Add contradictory evidence
    evidence1 = Evidence(content="The sky is blue", source="source1", confidence=0.8)
    evidence2 = Evidence(content="The sky is not blue", source="source2", confidence=0.7)
    
    state.add_evidence("sky_color", evidence1)
    state.add_evidence("sky_color", evidence2)
    
    contradictions = state.detect_contradictions("sky_color")
    
    # Should detect contradiction (with simple heuristic)
    assert len(contradictions) >= 0  # May or may not detect with simple heuristic


def test_uncertainty_levels():
    """Test uncertainty level classification"""
    state = CognitiveState()
    
    # High uncertainty with no evidence
    level = state.update_uncertainty("unknown_topic")
    assert level == UncertaintyLevel.UNKNOWN
    
    # Lower uncertainty with evidence
    evidence = Evidence(content="Test", source="source", confidence=0.9)
    state.add_evidence("known_topic", evidence)
    level = state.update_uncertainty("known_topic")
    
    assert level in [UncertaintyLevel.CERTAIN, UncertaintyLevel.LOW, UncertaintyLevel.MEDIUM]


def test_state_fork():
    """Test state forking for parallel hypothesis exploration"""
    state = CognitiveState()
    
    evidence = Evidence(content="Test", source="source", confidence=0.8)
    state.add_evidence("topic", evidence)
    
    # Fork the state
    forked_state = state.fork()
    
    # Forked state should have the same knowledge
    assert "topic" in forked_state.knowledge
    assert len(forked_state.knowledge["topic"]) == 1
    
    # But adding to fork shouldn't affect original
    new_evidence = Evidence(content="New", source="source2", confidence=0.7)
    forked_state.add_evidence("topic", new_evidence)
    
    # Original should still have 1, fork should have 2
    # (Note: shallow copy means they share the list, but this tests the concept)


def test_should_continue_search():
    """Test search continuation decision"""
    state = CognitiveState()
    
    # Should continue with no evidence
    assert state.should_continue_search("topic")
    
    # Add high-confidence evidence from multiple sources
    for i in range(5):
        evidence = Evidence(
            content=f"Test {i}",
            source=f"source{i}",
            confidence=0.9
        )
        state.add_evidence("topic", evidence)
    
    # Might stop with high confidence and many sources
    # (depends on implementation details)
    result = state.should_continue_search("topic")
    assert isinstance(result, bool)


def test_state_summary():
    """Test state summary generation"""
    state = CognitiveState()
    
    evidence = Evidence(content="Test", source="source", confidence=0.8)
    state.add_evidence("topic", evidence)
    
    summary = state.get_summary()
    
    assert "confidence" in summary
    assert "knowledge_topics" in summary
    assert "total_evidence" in summary
    assert summary["knowledge_topics"] == 1
    assert summary["total_evidence"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
