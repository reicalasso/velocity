"""
Cognitive State Management

State-driven intelligence that carries:
- Current knowledge state
- Uncertainty levels
- Contradiction distribution
- Confidence intervals
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional
from enum import Enum
import time


class UncertaintyLevel(Enum):
    """Uncertainty classification"""
    CERTAIN = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    UNKNOWN = 4


@dataclass
class Contradiction:
    """Represents a contradiction in information"""
    claim_a: str
    claim_b: str
    source_a: str
    source_b: str
    severity: float  # 0.0 to 1.0
    timestamp: float = field(default_factory=time.time)
    
    def __repr__(self) -> str:
        return f"Contradiction(severity={self.severity:.2f}, '{self.claim_a}' vs '{self.claim_b}')"


@dataclass
class Evidence:
    """Evidence from network interrogation"""
    content: str
    source: str
    confidence: float  # 0.0 to 1.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"Evidence(confidence={self.confidence:.2f}, source='{self.source}')"


class CognitiveState:
    """
    State-Driven Intelligence
    
    Velocity doesn't progress token-by-token.
    It carries cognitive state that updates as new information arrives.
    """
    
    def __init__(self):
        # Knowledge state
        self.knowledge: Dict[str, List[Evidence]] = {}
        
        # Uncertainty tracking
        self.uncertainty: UncertaintyLevel = UncertaintyLevel.UNKNOWN
        self.uncertainty_map: Dict[str, float] = {}
        
        # Contradiction detection
        self.contradictions: List[Contradiction] = []
        
        # Confidence scoring
        self.confidence: float = 0.0
        self.confidence_history: List[float] = []
        
        # Query history
        self.queries_made: List[str] = []
        self.sources_accessed: Set[str] = set()
        
        # Metadata
        self.creation_time: float = time.time()
        self.last_update: float = time.time()
        
    def add_evidence(self, topic: str, evidence: Evidence) -> None:
        """Add evidence to knowledge state"""
        if topic not in self.knowledge:
            self.knowledge[topic] = []
        self.knowledge[topic].append(evidence)
        self.sources_accessed.add(evidence.source)
        self.last_update = time.time()
        self._update_confidence()
        
    def detect_contradictions(self, topic: str) -> List[Contradiction]:
        """
        Detect contradictions in evidence.
        
        In Velocity, contradictions are not errors—
        they are signals of information density.
        """
        if topic not in self.knowledge:
            return []
        
        evidence_list = self.knowledge[topic]
        new_contradictions = []
        
        # Simple contradiction detection
        # (In production, this would use semantic similarity)
        for i, ev1 in enumerate(evidence_list):
            for ev2 in evidence_list[i+1:]:
                # Check if evidence contradicts
                if self._is_contradictory(ev1, ev2):
                    severity = abs(ev1.confidence - ev2.confidence)
                    contradiction = Contradiction(
                        claim_a=ev1.content[:100],
                        claim_b=ev2.content[:100],
                        source_a=ev1.source,
                        source_b=ev2.source,
                        severity=severity
                    )
                    new_contradictions.append(contradiction)
                    
        self.contradictions.extend(new_contradictions)
        return new_contradictions
    
    def _is_contradictory(self, ev1: Evidence, ev2: Evidence) -> bool:
        """
        Determine if two pieces of evidence contradict.
        
        This is a placeholder - real implementation would use
        semantic similarity and logical reasoning.
        """
        # Placeholder: check for negation words
        negation_words = {"not", "no", "never", "neither", "none", "nobody"}
        
        words1 = set(ev1.content.lower().split())
        words2 = set(ev2.content.lower().split())
        
        # Simple heuristic: if one has negation and other doesn't
        has_neg1 = bool(words1 & negation_words)
        has_neg2 = bool(words2 & negation_words)
        
        return has_neg1 != has_neg2 and len(words1 & words2) > 3
    
    def _update_confidence(self) -> None:
        """Update overall confidence based on evidence quality"""
        if not self.knowledge:
            self.confidence = 0.0
            return
        
        total_confidence = 0.0
        total_evidence = 0
        
        for evidence_list in self.knowledge.values():
            for evidence in evidence_list:
                total_confidence += evidence.confidence
                total_evidence += 1
        
        if total_evidence > 0:
            self.confidence = total_confidence / total_evidence
            self.confidence_history.append(self.confidence)
        
        # Reduce confidence if there are contradictions
        if self.contradictions:
            penalty = min(0.3, len(self.contradictions) * 0.05)
            self.confidence *= (1 - penalty)
    
    def update_uncertainty(self, topic: str) -> UncertaintyLevel:
        """
        Update uncertainty level for a topic.
        
        Uncertainty is not an error—it's a signal for more interrogation.
        """
        if topic not in self.knowledge:
            self.uncertainty_map[topic] = 1.0
            return UncertaintyLevel.UNKNOWN
        
        evidence_list = self.knowledge[topic]
        
        # Calculate uncertainty based on:
        # 1. Number of sources
        # 2. Confidence variance
        # 3. Presence of contradictions
        
        num_sources = len(set(ev.source for ev in evidence_list))
        avg_confidence = sum(ev.confidence for ev in evidence_list) / len(evidence_list)
        contradiction_count = len([c for c in self.contradictions 
                                   if topic in c.claim_a or topic in c.claim_b])
        
        # Uncertainty calculation
        uncertainty_score = 1.0 - avg_confidence
        uncertainty_score += contradiction_count * 0.1
        uncertainty_score -= num_sources * 0.05
        uncertainty_score = max(0.0, min(1.0, uncertainty_score))
        
        self.uncertainty_map[topic] = uncertainty_score
        
        # Classify uncertainty level
        if uncertainty_score < 0.2:
            level = UncertaintyLevel.CERTAIN
        elif uncertainty_score < 0.4:
            level = UncertaintyLevel.LOW
        elif uncertainty_score < 0.6:
            level = UncertaintyLevel.MEDIUM
        elif uncertainty_score < 0.8:
            level = UncertaintyLevel.HIGH
        else:
            level = UncertaintyLevel.UNKNOWN
        
        return level
    
    def should_continue_search(self, topic: str, max_queries: int = 10) -> bool:
        """
        Decide if more interrogation is needed.
        
        This is a cognitive decision:
        - Is uncertainty too high?
        - Are there unresolved contradictions?
        - Have we queried enough sources?
        """
        # Check query limit
        topic_queries = sum(1 for q in self.queries_made if topic in q)
        if topic_queries >= max_queries:
            return False
        
        # Check uncertainty
        if topic in self.uncertainty_map:
            if self.uncertainty_map[topic] < 0.3:  # Low uncertainty
                return False
        
        # Check if we have enough diverse sources
        if topic in self.knowledge:
            sources = set(ev.source for ev in self.knowledge[topic])
            if len(sources) >= 5 and self.confidence > 0.7:
                return False
        
        # Default: continue searching
        return True
    
    def fork(self) -> 'CognitiveState':
        """
        Fork the state for parallel hypothesis exploration.
        
        State can branch when exploring multiple hypotheses.
        """
        new_state = CognitiveState()
        new_state.knowledge = self.knowledge.copy()
        new_state.uncertainty = self.uncertainty
        new_state.uncertainty_map = self.uncertainty_map.copy()
        new_state.contradictions = self.contradictions.copy()
        new_state.confidence = self.confidence
        new_state.queries_made = self.queries_made.copy()
        new_state.sources_accessed = self.sources_accessed.copy()
        return new_state
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the cognitive state"""
        return {
            "confidence": round(self.confidence, 3),
            "uncertainty": self.uncertainty.name,
            "knowledge_topics": len(self.knowledge),
            "total_evidence": sum(len(ev) for ev in self.knowledge.values()),
            "contradictions": len(self.contradictions),
            "sources_accessed": len(self.sources_accessed),
            "queries_made": len(self.queries_made),
            "age_seconds": time.time() - self.creation_time,
        }
    
    def __repr__(self) -> str:
        summary = self.get_summary()
        return (
            f"CognitiveState(confidence={summary['confidence']}, "
            f"topics={summary['knowledge_topics']}, "
            f"evidence={summary['total_evidence']}, "
            f"contradictions={summary['contradictions']})"
        )
