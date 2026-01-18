"""
EPISTEMIC ROUTING
=================

"Bu problemi çözmek için hangi epistemik alanlara bakmalıyım?"

Burada retrieval yok, KARAR var.
Tek tek site değil, STRATEJI seçilir.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import time

from .intent_parser import IntentGraph, DecisionType


class SourceType(Enum):
    """Epistemik kaynak tipleri"""
    FORMAL_DOCS = "formal_documentation"      # Resmi dokümantasyon
    ACADEMIC = "academic_papers"              # Akademik yayınlar
    FORUMS = "community_forums"               # Topluluk forumları
    LIVE_DATA = "live_system_data"           # Canlı sistem verileri
    SOCIAL = "social_signals"                 # Sosyal sinyaller
    CODE_REPOS = "code_repositories"          # Kod repoları
    NEWS = "news_sources"                     # Haber kaynakları
    ENCYCLOPEDIC = "encyclopedic"            # Ansiklopedik (Wikipedia vb.)
    QA_SITES = "qa_sites"                    # Q&A siteleri (StackOverflow vb.)
    GOVERNMENT = "government_data"           # Hükümet verileri


@dataclass
class SourceStrategy:
    """
    Kaynak stratejisi
    
    Bu tek bir URL değil, bir sorgu stratejisidir
    """
    source_type: SourceType
    priority: float                    # 0-1, yüksek = öncelikli
    query_template: str                # Nasıl sorgulanacak
    trust_score: float                 # Bu kaynağa ne kadar güven
    freshness_requirement: str         # 'any', 'recent', 'realtime'
    cost: float                        # Sorgu maliyeti (zaman/para)
    expected_value: float              # Beklenen değer
    
    def compute_score(self) -> float:
        """
        Epistemik skor hesapla
        
        Score = f(trust, freshness, relevance, diversity, cost)
        """
        score = 0.0
        
        # Trust component (40%)
        score += self.trust_score * 0.4
        
        # Expected value (30%)
        score += self.expected_value * 0.3
        
        # Priority (20%)
        score += self.priority * 0.2
        
        # Cost efficiency (10%) - düşük maliyet daha iyi
        cost_efficiency = 1.0 - min(1.0, self.cost / 10.0)
        score += cost_efficiency * 0.1
        
        return score


class EpistemicRouter:
    """
    Epistemic Router
    
    Intent graph'ı alır, sorgulanacak kaynak stratejilerini döner.
    Bu bir "arama" değil, "yönlendirme" işlemidir.
    """
    
    def __init__(self):
        # Kaynak tiplerinin özellikleri
        self.source_characteristics = {
            SourceType.FORMAL_DOCS: {
                'trust': 0.9,
                'freshness': 0.6,
                'depth': 0.9,
                'cost': 2.0,
            },
            SourceType.ACADEMIC: {
                'trust': 0.95,
                'freshness': 0.4,
                'depth': 0.95,
                'cost': 5.0,
            },
            SourceType.FORUMS: {
                'trust': 0.5,
                'freshness': 0.8,
                'depth': 0.6,
                'cost': 1.0,
            },
            SourceType.LIVE_DATA: {
                'trust': 0.85,
                'freshness': 1.0,
                'depth': 0.5,
                'cost': 3.0,
            },
            SourceType.SOCIAL: {
                'trust': 0.3,
                'freshness': 0.95,
                'depth': 0.3,
                'cost': 1.0,
            },
            SourceType.CODE_REPOS: {
                'trust': 0.7,
                'freshness': 0.7,
                'depth': 0.8,
                'cost': 2.0,
            },
            SourceType.NEWS: {
                'trust': 0.6,
                'freshness': 0.9,
                'depth': 0.5,
                'cost': 1.5,
            },
            SourceType.ENCYCLOPEDIC: {
                'trust': 0.8,
                'freshness': 0.5,
                'depth': 0.7,
                'cost': 1.0,
            },
            SourceType.QA_SITES: {
                'trust': 0.65,
                'freshness': 0.7,
                'depth': 0.7,
                'cost': 1.5,
            },
            SourceType.GOVERNMENT: {
                'trust': 0.9,
                'freshness': 0.5,
                'depth': 0.8,
                'cost': 3.0,
            },
        }
    
    def route(
        self,
        intent: IntentGraph,
        max_strategies: int = 5,
        budget: float = 10.0
    ) -> List[SourceStrategy]:
        """
        Intent'e göre kaynak stratejilerini belirle
        
        Args:
            intent: Parse edilmiş intent
            max_strategies: Maksimum strateji sayısı
            budget: Toplam maliyet bütçesi
            
        Returns:
            Sıralı kaynak stratejileri listesi
        """
        # 1. Intent'e uygun kaynak tiplerini belirle
        candidate_types = self._select_candidate_types(intent)
        
        # 2. Her tip için strateji oluştur
        strategies = []
        for source_type in candidate_types:
            strategy = self._create_strategy(source_type, intent)
            if strategy:
                strategies.append(strategy)
        
        # 3. Stratejileri skorla ve sırala
        for strategy in strategies:
            strategy.expected_value = self._estimate_expected_value(
                strategy, intent
            )
        
        strategies.sort(key=lambda s: s.compute_score(), reverse=True)
        
        # 4. Bütçe ve limit dahilinde seç
        selected = []
        total_cost = 0.0
        
        for strategy in strategies:
            if len(selected) >= max_strategies:
                break
            if total_cost + strategy.cost > budget:
                continue
            
            selected.append(strategy)
            total_cost += strategy.cost
        
        return selected
    
    def _select_candidate_types(self, intent: IntentGraph) -> List[SourceType]:
        """
        Intent'e göre uygun kaynak tiplerini seç
        
        Bu adım kritik: Hangi epistemik alanlara bakılacağına karar verir
        """
        candidates = []
        
        # Karar tipine göre kaynak seçimi
        if intent.decision_type == DecisionType.FACTUAL:
            # Olgu temelli → Güvenilir kaynaklar
            candidates.extend([
                SourceType.ENCYCLOPEDIC,
                SourceType.FORMAL_DOCS,
                SourceType.ACADEMIC,
            ])
        
        elif intent.decision_type == DecisionType.COMPARATIVE:
            # Karşılaştırmalı → Çeşitli perspektifler
            candidates.extend([
                SourceType.ENCYCLOPEDIC,
                SourceType.QA_SITES,
                SourceType.FORUMS,
                SourceType.ACADEMIC,
            ])
        
        elif intent.decision_type == DecisionType.PREDICTIVE:
            # Öngörüsel → Güncel veriler + analiz
            candidates.extend([
                SourceType.LIVE_DATA,
                SourceType.NEWS,
                SourceType.SOCIAL,
                SourceType.ACADEMIC,
            ])
        
        elif intent.decision_type == DecisionType.STRATEGIC:
            # Stratejik → Çeşitli kaynaklardan sentez
            candidates.extend([
                SourceType.ACADEMIC,
                SourceType.FORMAL_DOCS,
                SourceType.QA_SITES,
                SourceType.FORUMS,
            ])
        
        elif intent.decision_type == DecisionType.ANALYTICAL:
            # Analitik → Derinlikli kaynaklar
            candidates.extend([
                SourceType.ACADEMIC,
                SourceType.FORMAL_DOCS,
                SourceType.ENCYCLOPEDIC,
            ])
        
        elif intent.decision_type == DecisionType.PROCEDURAL:
            # Prosedürel → Pratik rehberler
            candidates.extend([
                SourceType.FORMAL_DOCS,
                SourceType.QA_SITES,
                SourceType.FORUMS,
                SourceType.CODE_REPOS,
            ])
        
        # Kısıtlara göre ek seçimler
        if 'temporal' in intent.constraints:
            if intent.constraints['temporal'] == 'recent':
                # Güncel bilgi gerekli
                candidates.extend([
                    SourceType.NEWS,
                    SourceType.LIVE_DATA,
                ])
        
        if 'source_type' in intent.constraints:
            if intent.constraints['source_type'] == 'academic':
                # Akademik kaynak zorunlu
                candidates = [
                    st for st in candidates 
                    if st in [SourceType.ACADEMIC, SourceType.FORMAL_DOCS]
                ]
        
        # Duplicates'leri kaldır, önceliği koru
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    def _create_strategy(
        self,
        source_type: SourceType,
        intent: IntentGraph
    ) -> Optional[SourceStrategy]:
        """Kaynak tipi için strateji oluştur"""
        
        chars = self.source_characteristics.get(source_type)
        if not chars:
            return None
        
        # Query template oluştur
        query_template = self._generate_query_template(source_type, intent)
        
        # Freshness requirement
        freshness_req = 'any'
        if 'temporal' in intent.constraints:
            if intent.constraints['temporal'] == 'recent':
                freshness_req = 'recent'
        
        # Priority hesapla (uncertainty'ye göre ayarla)
        base_priority = self._calculate_base_priority(source_type, intent)
        
        return SourceStrategy(
            source_type=source_type,
            priority=base_priority,
            query_template=query_template,
            trust_score=chars['trust'],
            freshness_requirement=freshness_req,
            cost=chars['cost'],
            expected_value=0.0  # Sonra hesaplanacak
        )
    
    def _generate_query_template(
        self,
        source_type: SourceType,
        intent: IntentGraph
    ) -> str:
        """
        Kaynak tipi ve intent'e göre query template oluştur
        
        Bu, gerçek sorgu sırasında doldurulacak bir şablondur
        """
        goal = intent.goal
        
        templates = {
            SourceType.ENCYCLOPEDIC: f"{goal}",
            SourceType.ACADEMIC: f"scholarly {goal}",
            SourceType.FORUMS: f"discussion {goal}",
            SourceType.NEWS: f"latest {goal}",
            SourceType.QA_SITES: f"how to {goal}",
            SourceType.FORMAL_DOCS: f"documentation {goal}",
            SourceType.CODE_REPOS: f"code {goal}",
            SourceType.LIVE_DATA: f"current {goal}",
            SourceType.SOCIAL: f"opinion {goal}",
            SourceType.GOVERNMENT: f"official {goal}",
        }
        
        return templates.get(source_type, goal)
    
    def _calculate_base_priority(
        self,
        source_type: SourceType,
        intent: IntentGraph
    ) -> float:
        """Base priority hesapla"""
        
        chars = self.source_characteristics[source_type]
        
        # Uncertainty'ye göre priority ayarla
        if intent.uncertainty > 0.7:
            # Yüksek belirsizlik → Güvenilir kaynaklara öncelik
            return chars['trust']
        elif intent.uncertainty < 0.3:
            # Düşük belirsizlik → Freshness'e öncelik
            return chars['freshness']
        else:
            # Orta → Dengeli
            return (chars['trust'] + chars['freshness']) / 2
    
    def _estimate_expected_value(
        self,
        strategy: SourceStrategy,
        intent: IntentGraph
    ) -> float:
        """
        Bu stratejiden beklenen değeri tahmin et
        
        Faktörler:
        - Kaynak tipi intent'e ne kadar uygun?
        - Trust vs cost trade-off
        - Freshness requirement match
        """
        value = 0.0
        
        # 1. Intent alignment (en önemli)
        alignment = self._calculate_alignment(strategy.source_type, intent)
        value += alignment * 0.5
        
        # 2. Trust-cost ratio
        trust_cost_ratio = strategy.trust_score / (strategy.cost + 0.1)
        value += min(1.0, trust_cost_ratio) * 0.3
        
        # 3. Freshness match
        if intent.constraints.get('temporal') == 'recent':
            chars = self.source_characteristics[strategy.source_type]
            value += chars['freshness'] * 0.2
        else:
            value += 0.2  # Freshness gerekli değilse bonus
        
        return min(1.0, value)
    
    def _calculate_alignment(
        self,
        source_type: SourceType,
        intent: IntentGraph
    ) -> float:
        """Kaynak tipi intent'e ne kadar uygun?"""
        
        # Decision type bazlı alignment matrix
        alignment_matrix = {
            DecisionType.FACTUAL: {
                SourceType.ENCYCLOPEDIC: 0.9,
                SourceType.ACADEMIC: 0.85,
                SourceType.FORMAL_DOCS: 0.8,
                SourceType.QA_SITES: 0.6,
            },
            DecisionType.PREDICTIVE: {
                SourceType.LIVE_DATA: 0.9,
                SourceType.NEWS: 0.8,
                SourceType.ACADEMIC: 0.7,
                SourceType.SOCIAL: 0.5,
            },
            DecisionType.PROCEDURAL: {
                SourceType.FORMAL_DOCS: 0.9,
                SourceType.QA_SITES: 0.85,
                SourceType.CODE_REPOS: 0.8,
                SourceType.FORUMS: 0.6,
            },
            # ... diğer tipler için
        }
        
        type_alignments = alignment_matrix.get(intent.decision_type, {})
        return type_alignments.get(source_type, 0.5)  # Default: 0.5
