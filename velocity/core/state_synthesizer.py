"""
STATE SYNTHESIS
===============

Remaining hypotheses are synthesized into a final answer.

FinalState = aggregate(states)

This state contains:
- Decision (user-friendly answer)
- Evidence
- Uncertainty
- Alternatives
- Confidence interval

This is not model output, but computed result.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import statistics

from .hypothesis_generator import Hypothesis
from .state import CognitiveState, Evidence, Contradiction


# Simple NLP for answer synthesis
def simple_summarize(texts: List[str], max_sentences: int = 3) -> str:
    """
    Simple extractive summarization
    
    Selects most important sentences from texts
    """
    if not texts:
        return "No information available."
    
    # Combine all texts
    combined = " ".join(texts)
    
    # Split into sentences
    import re
    sentences = re.split(r'[.!?]+', combined)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if not sentences:
        return combined[:300]
    
    # Score sentences by length and position (early sentences are better)
    scored = []
    for i, sent in enumerate(sentences):
        # Score: longer sentences + earlier position
        score = len(sent.split()) / (i + 1)
        scored.append((score, sent))
    
    # Sort by score, take top N
    scored.sort(reverse=True)
    top_sentences = [sent for _, sent in scored[:max_sentences]]
    
    return " ".join(top_sentences)


@dataclass
class SynthesizedState:
    """
    Birleştirilmiş final state
    
    Bu bir "cevap" değil, "decision artifact"tır
    """
    decision: str                               # Ana karar/cevap
    confidence: float                           # Genel güven skoru
    confidence_interval: tuple                  # (min, max)
    
    evidence_summary: List[Evidence]            # En önemli evidence'lar
    contradictions: List[Contradiction]         # Tespit edilen çelişkiler
    alternatives: List[str]                     # Alternatif açıklamalar
    
    uncertainty_level: str                      # CERTAIN, LOW, MEDIUM, HIGH, UNKNOWN
    source_breakdown: Dict[str, int]           # Kaynak dağılımı
    
    contributing_hypotheses: List[str]         # Katkıda bulunan hipotezler
    eliminated_hypotheses: List[str]           # Elenen hipotezler
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return (
            f"SynthesizedState(decision='{self.decision[:50]}...', "
            f"confidence={self.confidence:.2f}, "
            f"alternatives={len(self.alternatives)})"
        )


class StateSynthesizer:
    """
    State Synthesizer
    
    Birden fazla hipotezin state'lerini birleştirir.
    Bu bir "voting" değil, "evidence aggregation"dır.
    """
    
    def __init__(self):
        pass
    
    def synthesize(
        self,
        hypotheses: List[Hypothesis],
        eliminated: List[Hypothesis]
    ) -> SynthesizedState:
        """
        Hipotezleri birleştir ve final state oluştur
        
        Args:
            hypotheses: Hayatta kalan hipotezler
            eliminated: Elenen hipotezler
            
        Returns:
            SynthesizedState
        """
        if not hypotheses:
            # Hiç hipotez kalmadı
            return self._create_empty_state(eliminated)
        
        # 1. Ana kararı belirle
        decision = self._determine_decision(hypotheses)
        
        # 2. Güven skorunu hesapla
        confidence = self._aggregate_confidence(hypotheses)
        confidence_interval = self._calculate_confidence_interval(hypotheses)
        
        # 3. Evidence'ları topla ve sırala
        evidence_summary = self._aggregate_evidence(hypotheses)
        
        # 4. Çelişkileri birleştir
        contradictions = self._aggregate_contradictions(hypotheses)
        
        # 5. Alternatifleri belirle
        alternatives = self._extract_alternatives(hypotheses)
        
        # 6. Uncertainty seviyesini belirle
        uncertainty_level = self._determine_uncertainty(hypotheses, confidence)
        
        # 7. Kaynak dağılımı
        source_breakdown = self._calculate_source_breakdown(hypotheses)
        
        # 8. Metadata
        metadata = {
            "total_hypotheses": len(hypotheses) + len(eliminated),
            "surviving_hypotheses": len(hypotheses),
            "total_evidence": sum(
                sum(len(ev_list) for ev_list in h.state.knowledge.values())
                for h in hypotheses
            ),
            "synthesis_method": "weighted_aggregation",
        }
        
        return SynthesizedState(
            decision=decision,
            confidence=confidence,
            confidence_interval=confidence_interval,
            evidence_summary=evidence_summary,
            contradictions=contradictions,
            alternatives=alternatives,
            uncertainty_level=uncertainty_level,
            source_breakdown=source_breakdown,
            contributing_hypotheses=[h.id for h in hypotheses],
            eliminated_hypotheses=[h.id for h in eliminated],
            metadata=metadata
        )
    
    def _determine_decision(self, hypotheses: List[Hypothesis]) -> str:
        """
        Determine final decision with natural, ChatGPT-like answer
        
        Synthesizes evidence into coherent answer using NLP
        """
        if not hypotheses:
            return "I couldn't find enough information to answer your question."
        
        # Get best hypothesis
        best = max(hypotheses, key=lambda h: h.confidence)
        
        # Collect all evidence content
        all_evidence_texts = []
        all_evidence = []
        
        for evidence_list in best.state.knowledge.values():
            for evidence in evidence_list:
                all_evidence.append(evidence)
                # Extract and clean text
                clean_content = self._clean_evidence_text(evidence.content)
                if clean_content:
                    all_evidence_texts.append(clean_content)
        
        # Sort evidence by confidence
        all_evidence.sort(key=lambda e: e.confidence, reverse=True)
        
        # Create natural answer
        if not all_evidence_texts:
            return "I found some results but couldn't extract clear information."
        
        # Combine and clean all content
        combined_text = ' '.join(all_evidence_texts)
        combined_text = self._deep_clean_text(combined_text)
        
        # Generate summary (4-5 sentences for richer answer)
        summary = simple_summarize([combined_text], max_sentences=4)
        
        # Format naturally (add spacing, clean up)
        natural_answer = self._naturalize_answer(summary)
        
        # Add subtle source attribution
        source_note = self._format_sources(all_evidence[:3])
        
        return f"{natural_answer}\n\n{source_note}"
    
    def _clean_evidence_text(self, text: str) -> str:
        """Initial cleaning of evidence text"""
        import re
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Remove reference markers [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove very short or very long chunks
        if len(text) < 30 or len(text) > 1000:
            return ""
        
        return text.strip()
    
    def _deep_clean_text(self, text: str) -> str:
        """Deep cleaning for natural readability"""
        import re
        
        # Fix concatenated words (camelCase)
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Fix word-number concatenation
        text = re.sub(r'([a-z])(\d)', r'\1 \2', text)
        text = re.sub(r'(\d)([a-z])', r'\1 \2', text)
        
        # Fix punctuation spacing
        text = re.sub(r'\s*,\s*', ', ', text)
        text = re.sub(r'\s*\.\s*', '. ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove fragments that are too short
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
        
        return '. '.join(sentences)
    
    def _naturalize_answer(self, text: str) -> str:
        """Make answer more natural and readable"""
        import re
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text
        
        # Join sentences naturally (no forced transitions)
        natural_text = ' '.join(sentences)
        
        # Ensure proper capitalization
        if natural_text and natural_text[0].islower():
            natural_text = natural_text[0].upper() + natural_text[1:]
        
        # Ensure ends with punctuation
        if natural_text and not natural_text[-1] in '.!?':
            natural_text += '.'
        
        return natural_text
    
    def _format_sources(self, evidence_list: List[Evidence]) -> str:
        """Format source attribution naturally"""
        if not evidence_list:
            return ""
        
        # Extract domains from sources
        sources = set()
        for ev in evidence_list:
            src = ev.source
            if '://' in src:
                # Extract domain
                domain = src.split('://')[1].split('/')[0]
                # Remove www. prefix
                domain = domain.replace('www.', '')
                sources.add(domain)
            elif ':' in src:
                # Handle other formats like "duckduckgo:url"
                source_type = src.split(':')[0]
                sources.add(source_type)
        
        if not sources:
            return ""
        
        # Format nicely
        source_list = ', '.join(sorted(list(sources))[:3])
        return f"_Information from: {source_list}_"
    
    def _aggregate_confidence(self, hypotheses: List[Hypothesis]) -> float:
        """
        Confidence'ı birleştir
        
        Weighted average: daha iyi hipotezler daha fazla ağırlık alır
        """
        if not hypotheses:
            return 0.0
        
        # Confidence'ların weighted average'ı
        total_weight = 0.0
        weighted_sum = 0.0
        
        for h in hypotheses:
            # Weight = confidence * (evidence_count / cost)
            evidence_count = sum(
                len(ev_list) for ev_list in h.state.knowledge.values()
            )
            weight = h.confidence * (evidence_count / (h.cost + 1.0))
            
            weighted_sum += h.confidence * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    def _calculate_confidence_interval(
        self,
        hypotheses: List[Hypothesis]
    ) -> tuple:
        """
        Güven aralığını hesapla
        
        Min ve max confidence değerleri
        """
        if not hypotheses:
            return (0.0, 0.0)
        
        confidences = [h.confidence for h in hypotheses]
        
        return (min(confidences), max(confidences))
    
    def _aggregate_evidence(
        self,
        hypotheses: List[Hypothesis],
        max_evidence: int = 10
    ) -> List[Evidence]:
        """
        Tüm hipotezlerden evidence'ları topla ve en iyileri seç
        """
        all_evidence = []
        
        for h in hypotheses:
            for evidence_list in h.state.knowledge.values():
                all_evidence.extend(evidence_list)
        
        # Duplicates'leri kaldır (source + content bazlı)
        unique_evidence = []
        seen = set()
        
        for evidence in all_evidence:
            key = (evidence.source, evidence.content[:100])
            if key not in seen:
                seen.add(key)
                unique_evidence.append(evidence)
        
        # Confidence'a göre sırala
        unique_evidence.sort(key=lambda e: e.confidence, reverse=True)
        
        return unique_evidence[:max_evidence]
    
    def _aggregate_contradictions(
        self,
        hypotheses: List[Hypothesis]
    ) -> List[Contradiction]:
        """Tüm çelişkileri topla"""
        all_contradictions = []
        
        for h in hypotheses:
            all_contradictions.extend(h.state.contradictions)
        
        # Severity'ye göre sırala
        all_contradictions.sort(key=lambda c: c.severity, reverse=True)
        
        # Duplicates'leri kaldır (benzer çelişkiler)
        unique = []
        for c in all_contradictions:
            # Basit duplicate check (gerçekte daha sofistike olmalı)
            is_duplicate = any(
                self._contradictions_similar(c, existing)
                for existing in unique
            )
            if not is_duplicate:
                unique.append(c)
        
        return unique
    
    def _contradictions_similar(
        self,
        c1: Contradiction,
        c2: Contradiction
    ) -> bool:
        """İki çelişki benzer mi?"""
        # Basit: claim'lerin örtüşmesi
        words1 = set(c1.claim_a.lower().split() + c1.claim_b.lower().split())
        words2 = set(c2.claim_a.lower().split() + c2.claim_b.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1 & words2) / min(len(words1), len(words2))
        
        return overlap > 0.5
    
    def _extract_alternatives(
        self,
        hypotheses: List[Hypothesis],
        max_alternatives: int = 3
    ) -> List[str]:
        """
        Alternatif açıklamaları çıkar
        
        En iyi hipotezden sonraki güçlü alternatifler
        """
        if len(hypotheses) <= 1:
            return []
        
        # Confidence'a göre sırala
        sorted_h = sorted(hypotheses, key=lambda h: h.confidence, reverse=True)
        
        # İlk hipotez zaten ana karar, diğerleri alternatif
        alternatives = []
        for h in sorted_h[1:max_alternatives+1]:
            alternatives.append(
                f"{h.description} (confidence: {h.confidence:.2f})"
            )
        
        return alternatives
    
    def _determine_uncertainty(
        self,
        hypotheses: List[Hypothesis],
        overall_confidence: float
    ) -> str:
        """Uncertainty seviyesini belirle"""
        
        # Confidence'a göre
        if overall_confidence >= 0.8:
            return "CERTAIN"
        elif overall_confidence >= 0.6:
            return "LOW"
        elif overall_confidence >= 0.4:
            return "MEDIUM"
        elif overall_confidence >= 0.2:
            return "HIGH"
        else:
            return "UNKNOWN"
    
    def _calculate_source_breakdown(
        self,
        hypotheses: List[Hypothesis]
    ) -> Dict[str, int]:
        """Kaynak dağılımını hesapla"""
        breakdown = {}
        
        for h in hypotheses:
            for source in h.state.sources_accessed:
                breakdown[source] = breakdown.get(source, 0) + 1
        
        return breakdown
    
    def _create_empty_state(
        self,
        eliminated: List[Hypothesis]
    ) -> SynthesizedState:
        """Hiç hipotez kalmadığında empty state oluştur"""
        return SynthesizedState(
            decision="Unable to reach decision. All hypotheses eliminated.",
            confidence=0.0,
            confidence_interval=(0.0, 0.0),
            evidence_summary=[],
            contradictions=[],
            alternatives=[],
            uncertainty_level="UNKNOWN",
            source_breakdown={},
            contributing_hypotheses=[],
            eliminated_hypotheses=[h.id for h in eliminated],
            metadata={
                "reason": "all_hypotheses_eliminated",
                "elimination_count": len(eliminated),
            }
        )
