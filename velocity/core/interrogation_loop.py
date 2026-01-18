"""
NETWORK INTERROGATION LOOP
===========================

Asıl zeka burada.

while confidence < threshold AND budget_not_exceeded:
    source = select_next_source(state)
    evidence = query(source)
    state = update(state, evidence)
    confidence = recompute_confidence(state)

Bu döngü:
- Aramayı
- Karar vermeyi
- Akıl yürütmeyi
aynı şey haline getirir.
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import time

from .hypothesis_generator import Hypothesis
from .state import CognitiveState, Evidence
from ..network.interrogator import NetworkInterrogator


@dataclass
class InterrogationResult:
    """Bir interrogation loop'un sonucu"""
    hypothesis: Hypothesis
    iterations: int
    total_cost: float
    final_confidence: float
    converged: bool
    convergence_reason: str


class InterrogationLoop:
    """
    Network Interrogation Loop
    
    Her hipotez için bağımsız sorgu döngüsü çalıştırır.
    Bu döngü dinamiktir: state'e göre bir sonraki adımı belirler.
    """
    
    def __init__(
        self,
        interrogator: NetworkInterrogator,
        confidence_threshold: float = 0.7,
        max_iterations: int = 10,
        budget: float = 10.0
    ):
        """
        Args:
            interrogator: Network interrogator instance
            confidence_threshold: Durma kriteri (confidence)
            max_iterations: Maksimum iterasyon
            budget: Maksimum maliyet
        """
        self.interrogator = interrogator
        self.confidence_threshold = confidence_threshold
        self.max_iterations = max_iterations
        self.budget = budget
    
    async def run(self, hypothesis: Hypothesis) -> InterrogationResult:
        """
        Bir hipotez için interrogation loop çalıştır
        
        Args:
            hypothesis: İşlenecek hipotez
            
        Returns:
            InterrogationResult
        """
        iteration = 0
        total_cost = 0.0
        converged = False
        convergence_reason = ""
        
        while True:
            iteration += 1
            
            # Durma kriterleri
            if hypothesis.state.confidence >= self.confidence_threshold:
                converged = True
                convergence_reason = "confidence_threshold_reached"
                break
            
            if iteration > self.max_iterations:
                converged = False
                convergence_reason = "max_iterations_exceeded"
                break
            
            if total_cost >= self.budget:
                converged = False
                convergence_reason = "budget_exceeded"
                break
            
            # State bazlı karar: bir sonraki kaynak
            next_query = self._select_next_query(hypothesis)
            if not next_query:
                converged = False
                convergence_reason = "no_more_queries"
                break
            
            # Network'ü sorgula
            try:
                evidence_list = await self._query_network(
                    next_query,
                    hypothesis.source_strategy.source_type
                )
                
                # Cost hesapla
                query_cost = hypothesis.source_strategy.cost
                total_cost += query_cost
                hypothesis.cost = total_cost
                
                # State'i güncelle
                for evidence in evidence_list:
                    hypothesis.state.add_evidence(
                        hypothesis.description,
                        evidence
                    )
                
                # Confidence'ı yeniden hesapla
                hypothesis.confidence = self._recompute_confidence(hypothesis.state)
                
                # Çelişki kontrolü
                contradictions = hypothesis.state.detect_contradictions(
                    hypothesis.description
                )
                
                # Çelişki varsa ve ciddi ise, forking gerekebilir
                # (Bu bir üst seviyede handle edilir)
                if contradictions:
                    # Flag set et
                    hypothesis.state.contradictions.extend(contradictions)
            
            except Exception as e:
                # Query başarısız, ama devam et
                print(f"Query failed: {e}")
                continue
        
        return InterrogationResult(
            hypothesis=hypothesis,
            iterations=iteration,
            total_cost=total_cost,
            final_confidence=hypothesis.confidence,
            converged=converged,
            convergence_reason=convergence_reason
        )
    
    def _select_next_query(self, hypothesis: Hypothesis) -> Optional[str]:
        """
        State bazlı karar: bir sonraki sorgu ne olmalı?
        
        Bu kritik: Neyi bildiğimize ve neyi bilmediğimize göre
        bir sonraki sorguyu seçer.
        """
        from .state import UncertaintyLevel
        
        state = hypothesis.state
        
        # 1. Hiç evidence yoksa, base query
        if not state.knowledge:
            return hypothesis.source_strategy.query_template
        
        # 2. Uncertainty hala yüksekse, daha fazla kaynak
        if state.uncertainty == UncertaintyLevel.HIGH:
            # Farklı açıdan sor
            return f"alternative view {hypothesis.source_strategy.query_template}"
        
        # 3. Contradictions varsa, çözümlemeye çalış
        if state.contradictions:
            latest_contradiction = state.contradictions[-1]
            return f"clarify {latest_contradiction.claim_a[:50]}"
        
        # 4. Confidence düşükse, derinleştir
        if state.confidence < 0.5:
            return f"detailed {hypothesis.source_strategy.query_template}"
        
        # 5. Yeterli bilgi toplandı
        return None
    
    async def _query_network(
        self,
        query: str,
        source_type
    ) -> List[Evidence]:
        """Network'ü sorgula ve evidence'a çevir"""
        
        # NetworkInterrogator kullanarak paralel sorgula
        results = await self.interrogator.search_parallel([query])
        
        # Results'ı Evidence'a çevir
        evidence_list = []
        for result in results:
            if not result.get("success"):
                continue
            
            evidence = Evidence(
                content=result.get("content", ""),
                source=result.get("source", "unknown"),
                confidence=self._estimate_evidence_confidence(result),
                metadata=result.get("metadata", {})
            )
            evidence_list.append(evidence)
        
        return evidence_list
    
    def _estimate_evidence_confidence(self, result: Dict[str, Any]) -> float:
        """Evidence için confidence tahmini"""
        confidence = 0.5  # Base
        
        # Source quality
        source = result.get("source", "")
        if any(domain in source for domain in [".edu", ".gov", ".org"]):
            confidence += 0.2
        
        # Content length (daha uzun genelde daha kapsamlı)
        content_length = len(result.get("content", ""))
        if content_length > 500:
            confidence += 0.1
        elif content_length < 100:
            confidence -= 0.1
        
        # Metadata'dan ek sinyaller
        metadata = result.get("metadata", {})
        if metadata.get("verified"):
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _recompute_confidence(self, state: CognitiveState) -> float:
        """
        State'e göre confidence'ı yeniden hesapla
        
        Bu basit değil: Birden fazla faktörü dikkate alır
        """
        if not state.knowledge:
            return 0.0
        
        # 1. Evidence quality ortalaması
        all_evidence = []
        for evidence_list in state.knowledge.values():
            all_evidence.extend(evidence_list)
        
        if not all_evidence:
            return 0.0
        
        avg_evidence_conf = sum(e.confidence for e in all_evidence) / len(all_evidence)
        
        # 2. Source diversity bonusu
        unique_sources = len(state.sources_accessed)
        diversity_bonus = min(0.2, unique_sources * 0.04)  # Max 0.2
        
        # 3. Contradiction cezası
        contradiction_penalty = min(0.3, len(state.contradictions) * 0.05)
        
        # Final confidence
        confidence = avg_evidence_conf + diversity_bonus - contradiction_penalty
        
        return min(1.0, max(0.0, confidence))


class ParallelInterrogationEngine:
    """
    Paralel Interrogation Engine
    
    Birden fazla hipotezi AYNI ANDA çalıştırır.
    GPU paralelliği burada devreye girer.
    """
    
    def __init__(
        self,
        interrogator: NetworkInterrogator,
        confidence_threshold: float = 0.7,
        max_iterations: int = 10,
        budget_per_hypothesis: float = 5.0
    ):
        self.loop = InterrogationLoop(
            interrogator=interrogator,
            confidence_threshold=confidence_threshold,
            max_iterations=max_iterations,
            budget=budget_per_hypothesis
        )
    
    async def run_parallel(
        self,
        hypotheses: List[Hypothesis]
    ) -> List[InterrogationResult]:
        """
        Tüm hipotezleri paralel olarak çalıştır
        
        Args:
            hypotheses: Hipotez listesi
            
        Returns:
            Her hipotez için sonuç listesi
        """
        # Asyncio ile paralel execution
        tasks = [
            self.loop.run(hypothesis)
            for hypothesis in hypotheses
            if not hypothesis.eliminated
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Exception'ları handle et
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Hypothesis failed: {result}")
                continue
            valid_results.append(result)
        
        return valid_results
    
    def should_fork(self, hypothesis: Hypothesis) -> bool:
        """
        Bu hipotez fork edilmeli mi?
        
        Çelişki varsa ve ciddi ise, fork gerekebilir
        """
        if not hypothesis.state.contradictions:
            return False
        
        # En son çelişkinin severity'sine bak
        latest_contradiction = hypothesis.state.contradictions[-1]
        
        # Severity yüksekse ve confidence orta seviyedeyse, fork
        if latest_contradiction.severity > 0.6 and 0.3 < hypothesis.confidence < 0.7:
            return True
        
        return False
