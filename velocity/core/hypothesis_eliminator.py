"""
HYPOTHESIS ELIMINATION
======================

Doğal seleksiyon.

for h in hypotheses:
    if confidence(h) < min_conf OR cost(h) too high:
        eliminate(h)

Geriye:
- 1 güçlü hipotez
veya
- Birkaç dengeli aday
kalır
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass

from .hypothesis_generator import Hypothesis


@dataclass
class EliminationCriteria:
    """Eleme kriterleri"""
    min_confidence: float = 0.3        # Minimum güven skoru
    max_cost: float = 10.0             # Maksimum maliyet
    min_evidence: int = 2              # Minimum evidence sayısı
    max_contradictions: int = 5        # Maksimum çelişki sayısı
    convergence_required: bool = False # Convergence zorunlu mu?


class HypothesisEliminator:
    """
    Hypothesis Eliminator
    
    Zayıf hipotezleri eler, güçlü olanları tutar.
    Bu bir "doğal seleksiyon" sürecidir.
    """
    
    def __init__(self, criteria: Optional[EliminationCriteria] = None):
        """
        Args:
            criteria: Eleme kriterleri (default kullanılabilir)
        """
        self.criteria = criteria or EliminationCriteria()
    
    def eliminate_weak(
        self,
        hypotheses: List[Hypothesis],
        results: Optional[List] = None
    ) -> Tuple[List[Hypothesis], List[Hypothesis]]:
        """
        Zayıf hipotezleri ele
        
        Args:
            hypotheses: Tüm hipotezler
            results: Interrogation sonuçları (opsiyonel)
            
        Returns:
            (surviving_hypotheses, eliminated_hypotheses)
        """
        surviving = []
        eliminated = []
        
        for i, hypothesis in enumerate(hypotheses):
            # Zaten elenmişse atla
            if hypothesis.eliminated:
                eliminated.append(hypothesis)
                continue
            
            # Eleme kriterlerini kontrol et
            should_eliminate, reason = self._should_eliminate(
                hypothesis,
                results[i] if results and i < len(results) else None
            )
            
            if should_eliminate:
                hypothesis.eliminated = True
                hypothesis.elimination_reason = reason
                eliminated.append(hypothesis)
            else:
                surviving.append(hypothesis)
        
        return surviving, eliminated
    
    def _should_eliminate(
        self,
        hypothesis: Hypothesis,
        result = None
    ) -> Tuple[bool, str]:
        """
        Bu hipotez elenmeli mi?
        
        Returns:
            (should_eliminate, reason)
        """
        # 1. Confidence çok düşük
        if hypothesis.confidence < self.criteria.min_confidence:
            return True, f"Low confidence: {hypothesis.confidence:.2f} < {self.criteria.min_confidence}"
        
        # 2. Maliyet çok yüksek
        if hypothesis.cost > self.criteria.max_cost:
            return True, f"Cost too high: {hypothesis.cost:.2f} > {self.criteria.max_cost}"
        
        # 3. Yeterli evidence yok
        total_evidence = sum(
            len(evidence_list)
            for evidence_list in hypothesis.state.knowledge.values()
        )
        if total_evidence < self.criteria.min_evidence:
            return True, f"Insufficient evidence: {total_evidence} < {self.criteria.min_evidence}"
        
        # 4. Çelişki sayısı çok fazla
        if len(hypothesis.state.contradictions) > self.criteria.max_contradictions:
            return True, f"Too many contradictions: {len(hypothesis.state.contradictions)}"
        
        # 5. Convergence gerekiyorsa ve olmamışsa
        if self.criteria.convergence_required and result:
            if not result.converged:
                return True, f"Did not converge: {result.convergence_reason}"
        
        # 6. State quality check
        if hypothesis.state.uncertainty.value >= 4:  # UNKNOWN
            if hypothesis.confidence < 0.5:
                return True, "High uncertainty with low confidence"
        
        # Hayatta kalır
        return False, ""
    
    def rank_hypotheses(
        self,
        hypotheses: List[Hypothesis]
    ) -> List[Hypothesis]:
        """
        Hipotezleri skorla ve sırala
        
        Sıralama faktörleri:
        1. Confidence (40%)
        2. Evidence quality (30%)
        3. Cost efficiency (20%)
        4. Contradiction handling (10%)
        """
        scored = []
        
        for hypothesis in hypotheses:
            if hypothesis.eliminated:
                continue
            
            score = self._compute_hypothesis_score(hypothesis)
            scored.append((score, hypothesis))
        
        # Skora göre sırala (yüksekten düşüğe)
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return [h for score, h in scored]
    
    def _compute_hypothesis_score(self, hypothesis: Hypothesis) -> float:
        """
        Hipotez skoru hesapla
        
        Yüksek skor = daha güçlü hipotez
        """
        score = 0.0
        
        # 1. Confidence (40%)
        score += hypothesis.confidence * 0.4
        
        # 2. Evidence quality (30%)
        if hypothesis.state.knowledge:
            all_evidence = []
            for evidence_list in hypothesis.state.knowledge.values():
                all_evidence.extend(evidence_list)
            
            if all_evidence:
                avg_evidence_quality = sum(
                    e.confidence for e in all_evidence
                ) / len(all_evidence)
                score += avg_evidence_quality * 0.3
        
        # 3. Cost efficiency (20%)
        # Düşük maliyet + yüksek confidence = yüksek efficiency
        if hypothesis.cost > 0:
            efficiency = hypothesis.confidence / (hypothesis.cost + 0.1)
            normalized_efficiency = min(1.0, efficiency)
            score += normalized_efficiency * 0.2
        else:
            score += 0.2  # Bedava evidence!
        
        # 4. Contradiction handling (10%)
        # Az çelişki = daha iyi
        contradiction_penalty = min(
            0.1,
            len(hypothesis.state.contradictions) * 0.02
        )
        score += (0.1 - contradiction_penalty)
        
        return score
    
    def select_best(
        self,
        hypotheses: List[Hypothesis],
        n: int = 1
    ) -> List[Hypothesis]:
        """
        En iyi n hipotezi seç
        
        Args:
            hypotheses: Hipotez listesi
            n: Seçilecek sayı
            
        Returns:
            En iyi n hipotez
        """
        ranked = self.rank_hypotheses(hypotheses)
        return ranked[:n]
    
    def should_continue_search(
        self,
        hypotheses: List[Hypothesis],
        threshold: float = 0.8
    ) -> bool:
        """
        Aramaya devam edilmeli mi?
        
        Eğer en iyi hipotez yeterince güçlüyse, dur.
        """
        if not hypotheses:
            return True  # Hipotez yoksa devam et
        
        active = [h for h in hypotheses if not h.eliminated]
        if not active:
            return False  # Hiç aktif hipotez kalmadı
        
        # En iyi hipotezin confidence'ına bak
        best = self.select_best(active, n=1)
        if best and best[0].confidence >= threshold:
            return False  # Yeterince iyi
        
        return True
    
    def get_elimination_report(
        self,
        eliminated: List[Hypothesis]
    ) -> str:
        """Eleme raporu oluştur"""
        if not eliminated:
            return "No hypotheses eliminated."
        
        report = [f"Eliminated {len(eliminated)} hypotheses:\n"]
        
        for i, h in enumerate(eliminated, 1):
            report.append(
                f"{i}. {h.description[:60]}...\n"
                f"   Reason: {h.elimination_reason}\n"
                f"   Final confidence: {h.confidence:.2f}\n"
                f"   Cost: {h.cost:.2f}\n"
            )
        
        return "".join(report)
