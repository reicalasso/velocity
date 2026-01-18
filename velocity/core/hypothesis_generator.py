"""
PARALLEL HYPOTHESIS GENERATION
===============================

Velocity tek cevap aramaz.
Hipotez uzayı üretir.

H = {h1, h2, h3, ..., hn}

Her hipotez:
- Farklı varsayıma dayanır
- Farklı kaynak stratejisi kullanır
- Farklı çözüm yolu dener

GPU'lar burada:
- Aynı anda n hipotezi yürütür
- Her biri kendi "dünya modeli"ne sahiptir
- Bu training değil, paralel evaluation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid
import time

from .intent_parser import IntentGraph
from .epistemic_router import SourceStrategy
from .state import CognitiveState


@dataclass
class Hypothesis:
    """
    Bir hipotez
    
    Bu bir "cevap adayı" değil, "araştırma yolu"dur
    """
    id: str
    description: str                    # Bu hipotez ne iddia ediyor
    assumptions: List[str]              # Hangi varsayımlara dayanıyor
    source_strategy: SourceStrategy     # Hangi kaynak stratejisini kullanıyor
    state: CognitiveState              # Kendi cognitive state'i
    confidence: float = 0.0            # Mevcut güven skoru
    cost: float = 0.0                  # Harcanmış maliyet
    eliminated: bool = False           # Elendi mi?
    elimination_reason: str = ""       # Neden elendi
    
    def __repr__(self) -> str:
        status = "ELIMINATED" if self.eliminated else "ACTIVE"
        return (
            f"Hypothesis({self.id[:8]}, '{self.description[:40]}...', "
            f"confidence={self.confidence:.2f}, {status})"
        )


class HypothesisGenerator:
    """
    Hypothesis Generator
    
    Intent ve routing stratejilerine göre hipotez uzayı üretir.
    """
    
    def __init__(self, max_hypotheses: int = 5):
        """
        Args:
            max_hypotheses: Maksimum paralel hipotez sayısı
        """
        self.max_hypotheses = max_hypotheses
    
    def generate(
        self,
        intent: IntentGraph,
        strategies: List[SourceStrategy]
    ) -> List[Hypothesis]:
        """
        Hipotez uzayı üret
        
        Args:
            intent: Parse edilmiş intent
            strategies: Routing stratejileri
            
        Returns:
            Hipotez listesi
        """
        hypotheses = []
        
        # Strateji 1: Her kaynak stratejisi için bir hipotez
        for i, strategy in enumerate(strategies[:self.max_hypotheses]):
            hypothesis = self._create_hypothesis_from_strategy(
                intent, strategy, i
            )
            hypotheses.append(hypothesis)
        
        # Strateji 2: Karar tipine göre ek hipotezler
        if len(hypotheses) < self.max_hypotheses:
            additional = self._generate_decision_type_hypotheses(
                intent, strategies
            )
            hypotheses.extend(additional[:self.max_hypotheses - len(hypotheses)])
        
        # Strateji 3: Belirsizlik yüksekse, zıt hipotezler üret
        if intent.uncertainty > 0.7 and len(hypotheses) < self.max_hypotheses:
            contrarian = self._generate_contrarian_hypotheses(
                intent, strategies
            )
            hypotheses.extend(contrarian[:self.max_hypotheses - len(hypotheses)])
        
        return hypotheses
    
    def _create_hypothesis_from_strategy(
        self,
        intent: IntentGraph,
        strategy: SourceStrategy,
        index: int
    ) -> Hypothesis:
        """Kaynak stratejisinden hipotez oluştur"""
        
        # Hipotez açıklaması
        description = (
            f"Hypothesis {index + 1}: Use {strategy.source_type.value} "
            f"to answer '{intent.goal[:50]}...'"
        )
        
        # Varsayımlar
        assumptions = [
            f"{strategy.source_type.value} is reliable for this query",
            f"Trust level: {strategy.trust_score:.2f}",
            f"Freshness requirement: {strategy.freshness_requirement}",
        ]
        
        # Başlangıç state'i
        state = CognitiveState()
        state.uncertainty = intent.uncertainty
        
        return Hypothesis(
            id=str(uuid.uuid4()),
            description=description,
            assumptions=assumptions,
            source_strategy=strategy,
            state=state,
            confidence=0.0,
            cost=0.0
        )
    
    def _generate_decision_type_hypotheses(
        self,
        intent: IntentGraph,
        strategies: List[SourceStrategy]
    ) -> List[Hypothesis]:
        """
        Karar tipine özgü hipotezler üret
        
        Örneğin comparative sorular için:
        - H1: "A daha iyidir"
        - H2: "B daha iyidir"
        - H3: "Karşılaştırılamaz"
        """
        hypotheses = []
        
        from .intent_parser import DecisionType
        
        if intent.decision_type == DecisionType.COMPARATIVE:
            # Comparative için alternatif sonuçlar
            if strategies:
                base_strategy = strategies[0]
                
                # H: "First option is better"
                h1 = Hypothesis(
                    id=str(uuid.uuid4()),
                    description="Hypothesis: First option is superior",
                    assumptions=["Assuming first option advantages outweigh second"],
                    source_strategy=base_strategy,
                    state=CognitiveState(),
                )
                
                # H: "Second option is better"
                h2 = Hypothesis(
                    id=str(uuid.uuid4()),
                    description="Hypothesis: Second option is superior",
                    assumptions=["Assuming second option advantages outweigh first"],
                    source_strategy=base_strategy,
                    state=CognitiveState(),
                )
                
                hypotheses.extend([h1, h2])
        
        elif intent.decision_type == DecisionType.PREDICTIVE:
            # Predictive için olumlu/olumsuz senaryolar
            if strategies:
                base_strategy = strategies[0]
                
                h_positive = Hypothesis(
                    id=str(uuid.uuid4()),
                    description="Hypothesis: Positive outcome scenario",
                    assumptions=["Optimistic scenario assumptions"],
                    source_strategy=base_strategy,
                    state=CognitiveState(),
                )
                
                h_negative = Hypothesis(
                    id=str(uuid.uuid4()),
                    description="Hypothesis: Negative outcome scenario",
                    assumptions=["Pessimistic scenario assumptions"],
                    source_strategy=base_strategy,
                    state=CognitiveState(),
                )
                
                hypotheses.extend([h_positive, h_negative])
        
        return hypotheses
    
    def _generate_contrarian_hypotheses(
        self,
        intent: IntentGraph,
        strategies: List[SourceStrategy]
    ) -> List[Hypothesis]:
        """
        Zıt hipotezler üret (devil's advocate)
        
        Yüksek belirsizlik durumlarında, ana hipotezlere
        meydan okuyan alternatif hipotezler üret
        """
        hypotheses = []
        
        if strategies:
            base_strategy = strategies[0]
            
            # Contrarian hypothesis
            contrarian = Hypothesis(
                id=str(uuid.uuid4()),
                description=f"Contrarian: Opposite view on '{intent.goal[:40]}...'",
                assumptions=[
                    "Assuming conventional wisdom is wrong",
                    "Looking for contradictory evidence",
                ],
                source_strategy=base_strategy,
                state=CognitiveState(),
            )
            
            hypotheses.append(contrarian)
        
        return hypotheses
    
    def fork_hypothesis(self, hypothesis: Hypothesis) -> Hypothesis:
        """
        Hipotezi fork'la (state dallanması)
        
        Çelişki durumlarında state çatallanır
        """
        forked = Hypothesis(
            id=str(uuid.uuid4()),
            description=f"Forked from: {hypothesis.description}",
            assumptions=hypothesis.assumptions.copy(),
            source_strategy=hypothesis.source_strategy,
            state=hypothesis.state.fork(),
            confidence=hypothesis.confidence,
            cost=hypothesis.cost,
        )
        
        return forked
