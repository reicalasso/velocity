"""
INTENT PARSING
===============

LLM'ler burada hemen cevap üretir.
Velocity önce problemi tanımlar.

Input → Intent Graph
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
import re


class DecisionType(Enum):
    """Karar türleri"""
    FACTUAL = "factual"           # Olgu temelli (What is X?)
    COMPARATIVE = "comparative"   # Karşılaştırmalı (X vs Y?)
    PREDICTIVE = "predictive"     # Öngörüsel (Will X happen?)
    STRATEGIC = "strategic"       # Stratejik (How to achieve X?)
    ANALYTICAL = "analytical"     # Analitik (Why does X?)
    PROCEDURAL = "procedural"     # Prosedürel (How to do X?)
    GENERATIVE = "generative"     # Üretici (Write X, Create Y, Generate Z)
    SOCIAL = "social"              # Sosyal (Hi, How are you, Thanks)
    META = "meta"                  # Meta (About Velocity itself)
    CREATIVE = "creative"          # Yaratıcı (Tell me a story)


@dataclass
class IntentGraph:
    """
    Parsed intent representation
    
    Bu bir "cevap" değil, "problem tanımı"dır
    """
    goal: str                          # Ana hedef
    subgoals: List[str]               # Alt hedefler
    uncertainty: float                # Belirsizlik (0-1)
    decision_type: DecisionType       # Karar türü
    constraints: Dict[str, Any]       # Kısıtlar
    context: Dict[str, Any]           # Bağlam
    
    def __repr__(self) -> str:
        return (
            f"IntentGraph(goal='{self.goal[:50]}...', "
            f"type={self.decision_type.value}, "
            f"uncertainty={self.uncertainty:.2f}, "
            f"subgoals={len(self.subgoals)})"
        )


class IntentParser:
    """
    Intent Parser
    
    Kullanıcı girdisini alır, problem yapısını çıkarır.
    Bu bir "anlama" değil, "yapılandırma" işlemidir.
    """
    
    def __init__(self):
        # Karar tipi tanıma için pattern'ler (order matters - check specific first!)
        self.patterns = {
            # SOCIAL - Check FIRST (most specific, short phrases)
            DecisionType.SOCIAL: [
                r'^\b(hi|hello|hey|naber|selam|merhaba|nasılsın|how are you|thanks|thank you|teşekkür)\b$',
                r'^\b(good morning|good night|iyi günler|günaydın|iyi geceler)\b$',
                r'^\b(bye|goodbye|see you|hoşça kal|görüşürüz)\b$'
            ],
            # META - Questions about Velocity itself
            DecisionType.META: [
                r'\b(velocity|sen|you|your|senin)\b.*\b(what|who|how|ne|nasıl|kimsin)\b',
                r'\bwhat (are|is) you\b', r'\bsen (ne|kim)\b'
            ],
            # CREATIVE - Story, poem, joke requests
            DecisionType.CREATIVE: [
                r'\b(story|poem|joke|şiir|hikaye|fıkra)\b',
                r'\btell me (a|about)\b', r'\banla\b.*\b(hikaye|fıkra)\b'
            ],
            # GENERATIVE - Code, document generation
            DecisionType.GENERATIVE: [
                r'\bwrite\b', r'\bcreate\b', r'\bgenerate\b', r'\bmake\b',
                r'\byaz\b', r'\boluştur\b', r'\büret\b', r'\byap\b',
                r'\bkod\b', r'\bcode\b', r'\bexample\b', r'\börnek\b'
            ],
            # FACTUAL - What is X?
            DecisionType.FACTUAL: [
                r'\bwhat is\b', r'\bdefine\b', r'\bexplain\b',
                r'\bnedir\b', r'\btanımla\b', r'\banla\b', r'\bkimdir\b'
            ],
            DecisionType.COMPARATIVE: [
                r'\bcompare\b', r'\bvs\b', r'\bdifference\b',
                r'\bkarşılaştır\b', r'\bfark\b'
            ],
            DecisionType.PREDICTIVE: [
                r'\bwill\b', r'\bpredict\b', r'\bforecast\b',
                r'\bolacak\b', r'\btahmin\b'
            ],
            DecisionType.STRATEGIC: [
                r'\bhow to achieve\b', r'\bstrategy\b', r'\bplan\b',
                r'\bnasıl\b', r'\bstrateji\b'
            ],
            DecisionType.ANALYTICAL: [
                r'\bwhy\b', r'\bcause\b', r'\breason\b',
                r'\bneden\b', r'\bsebep\b'
            ],
            DecisionType.PROCEDURAL: [
                r'\bhow to\b', r'\bsteps\b', r'\bprocedure\b',
                r'\badımlar\b', r'\bişlem\b'
            ],
        }
        
        # Belirsizlik göstergeleri
        self.uncertainty_indicators = [
            'maybe', 'possibly', 'probably', 'might', 'could',
            'belki', 'muhtemelen', 'olabilir'
        ]
    
    def parse(self, user_input: str, system_goal: str = "answer") -> IntentGraph:
        """
        Parse user input into intent graph
        
        Args:
            user_input: Kullanıcı girdisi
            system_goal: Sistem hedefi (answer, decide, suggest, generate, plan)
            
        Returns:
            IntentGraph
        """
        # 1. Ana hedefi belirle
        goal = self._extract_goal(user_input, system_goal)
        
        # 2. Alt hedefleri çıkar
        subgoals = self._extract_subgoals(user_input, goal)
        
        # 3. Karar tipini tespit et
        decision_type = self._detect_decision_type(user_input)
        
        # 4. Belirsizlik seviyesini hesapla
        uncertainty = self._calculate_uncertainty(user_input, decision_type)
        
        # 5. Kısıtları çıkar
        constraints = self._extract_constraints(user_input)
        
        # 6. Bağlamı oluştur
        context = {
            "input_length": len(user_input),
            "system_goal": system_goal,
            "language": self._detect_language(user_input),
        }
        
        return IntentGraph(
            goal=goal,
            subgoals=subgoals,
            uncertainty=uncertainty,
            decision_type=decision_type,
            constraints=constraints,
            context=context
        )
    
    def _extract_goal(self, user_input: str, system_goal: str) -> str:
        """Ana hedefi çıkar"""
        # Basit: ilk cümle veya tüm input
        sentences = user_input.split('.')
        main_sentence = sentences[0].strip()
        
        return f"{system_goal}: {main_sentence}"
    
    def _extract_subgoals(self, user_input: str, goal: str) -> List[str]:
        """Alt hedefleri çıkar"""
        subgoals = []
        
        # Soru işaretlerine göre ayır
        questions = [q.strip() for q in user_input.split('?') if q.strip()]
        
        if len(questions) > 1:
            # Birden fazla soru var, her biri bir alt hedef
            subgoals = questions
        else:
            # Tek soru, bileşenlerine ayır
            # "and", "or", "also" gibi bağlaçlara göre
            parts = re.split(r'\band\b|\bor\b|\balso\b|\bve\b|\bveya\b', user_input)
            if len(parts) > 1:
                subgoals = [p.strip() for p in parts if p.strip()]
        
        return subgoals[:5]  # Max 5 alt hedef
    
    def _detect_decision_type(self, user_input: str) -> DecisionType:
        """Karar tipini tespit et"""
        text_lower = user_input.lower()
        
        # Her tip için pattern'leri kontrol et
        scores = {}
        for decision_type, patterns in self.patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, text_lower))
            scores[decision_type] = score
        
        # En yüksek skoru al
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # Default: factual
        return DecisionType.FACTUAL
    
    def _calculate_uncertainty(self, user_input: str, decision_type: DecisionType) -> float:
        """
        Belirsizlik seviyesini hesapla
        
        Faktörler:
        1. Belirsizlik göstergeleri
        2. Karar tipi (predictive daha belirsiz)
        3. Soru karmaşıklığı
        """
        uncertainty = 0.0
        text_lower = user_input.lower()
        
        # 1. Belirsizlik göstergeleri
        indicator_count = sum(
            1 for indicator in self.uncertainty_indicators
            if indicator in text_lower
        )
        uncertainty += indicator_count * 0.15
        
        # 2. Karar tipine göre baseline
        type_uncertainty = {
            DecisionType.FACTUAL: 0.2,
            DecisionType.COMPARATIVE: 0.3,
            DecisionType.ANALYTICAL: 0.4,
            DecisionType.PROCEDURAL: 0.3,
            DecisionType.STRATEGIC: 0.5,
            DecisionType.PREDICTIVE: 0.7,
        }
        uncertainty += type_uncertainty.get(decision_type, 0.3)
        
        # 3. Karmaşıklık (kelime sayısı)
        word_count = len(user_input.split())
        if word_count > 50:
            uncertainty += 0.1
        elif word_count < 5:
            uncertainty += 0.2  # Çok kısa sorular belirsiz
        
        # Normalize (0-1)
        return min(1.0, uncertainty)
    
    def _extract_constraints(self, user_input: str) -> Dict[str, Any]:
        """Kısıtları çıkar"""
        constraints = {}
        text_lower = user_input.lower()
        
        # Zaman kısıtları
        if any(word in text_lower for word in ['latest', 'current', 'recent', 'today', 'güncel', 'son']):
            constraints['temporal'] = 'recent'
        
        # Kaynak kısıtları
        if any(word in text_lower for word in ['scientific', 'academic', 'research', 'akademik', 'bilimsel']):
            constraints['source_type'] = 'academic'
        
        # Derinlik kısıtları
        if any(word in text_lower for word in ['detailed', 'comprehensive', 'in-depth', 'detaylı', 'kapsamlı']):
            constraints['depth'] = 'deep'
        elif any(word in text_lower for word in ['brief', 'summary', 'quick', 'kısa', 'özet']):
            constraints['depth'] = 'shallow'
        
        return constraints
    
    def _detect_language(self, text: str) -> str:
        """Dil tespiti (basit)"""
        turkish_chars = set('çğıöşüÇĞİÖŞÜ')
        if any(char in text for char in turkish_chars):
            return 'tr'
        return 'en'
    
    def decompose_goal(self, intent: IntentGraph) -> List[str]:
        """
        Ana hedefi sorgulanabilir parçalara ayır
        
        Bu, network interrogation için query'leri hazırlar
        """
        queries = [intent.goal]
        
        # Alt hedefler varsa ekle
        queries.extend(intent.subgoals)
        
        # Karar tipine göre ek query'ler
        if intent.decision_type == DecisionType.COMPARATIVE:
            # "A vs B" → "A nedir", "B nedir", "A B farkı"
            parts = re.split(r'\bvs\b|\bversus\b|\bkarşı\b', intent.goal)
            if len(parts) == 2:
                queries.append(f"what is {parts[0].strip()}")
                queries.append(f"what is {parts[1].strip()}")
                queries.append(f"difference between {parts[0].strip()} and {parts[1].strip()}")
        
        elif intent.decision_type == DecisionType.ANALYTICAL:
            # "Why X?" → "X causes", "X reasons", "X explanation"
            topic = intent.goal.replace("why", "").strip()
            queries.append(f"{topic} causes")
            queries.append(f"{topic} reasons")
            queries.append(f"{topic} explanation")
        
        return queries
