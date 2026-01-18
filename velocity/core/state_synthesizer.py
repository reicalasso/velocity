"""
STATE SYNTHESIS
===============

Kalan hipotezler birleştirilir:

FinalState = aggregate(states)

Bu state şunları içerir:
- Karar
- Dayanaklar
- Belirsizlik
- Alternatifler
- Güven aralığı

Bu nokta:
- Model cevabı değil
- Hesaplanmış sonuçtur
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import statistics

from .hypothesis_generator import Hypothesis
from .state import CognitiveState, Evidence, Contradiction


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
        Ana kararı belirle
        
        En yüksek confidence'a sahip hipotezin açıklaması + evidence sentezi
        """
        if not hypotheses:
            return "Unable to determine decision."
        
        # En iyi hipotezi bul
        best = max(hypotheses, key=lambda h: h.confidence)
        
        # Evidence'dan özet çıkar
        decision_parts = [best.description]
        
        # En iyi evidence'ları ekle
        all_evidence = []
        for evidence_list in best.state.knowledge.values():
            all_evidence.extend(evidence_list)
        
        # Confidence'a göre sırala, en iyi 3'ü al
        all_evidence.sort(key=lambda e: e.confidence, reverse=True)
        for evidence in all_evidence[:3]:
            decision_parts.append(f"[{evidence.source}]: {evidence.content[:150]}...")
        
        return "\n\n".join(decision_parts)
    
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
