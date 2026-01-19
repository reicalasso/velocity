"""
VELOCITY CORE ENGINE
====================

Tam algoritmik çekirdek:

intent = parse_intent(input)
routes = epistemic_routing(intent)
hypotheses = generate_hypotheses(routes)

parallel_for h in hypotheses:
    while not done(h):
        evidence = interrogate_network(h.state)
        h.state = update_state(h.state, evidence)

hypotheses = eliminate_weak(hypotheses)
final_state = synthesize(hypotheses)
output = render(final_state)

Bu tek bir algoritma değil, bir yürütme döngüsü (cognitive loop).
"""

import asyncio
from typing import Dict, Any, Optional, List
from loguru import logger

from .intent_parser import IntentParser, IntentGraph, DecisionType
from .epistemic_router import EpistemicRouter, SourceStrategy
from .hypothesis_generator import HypothesisGenerator, Hypothesis
from .interrogation_loop import ParallelInterrogationEngine, InterrogationResult
from .hypothesis_eliminator import HypothesisEliminator, EliminationCriteria
from .state_synthesizer import StateSynthesizer, SynthesizedState
from .network_gate import NetworkGate, generate_local_response
from ..network.interrogator import NetworkInterrogator


class VelocityCore:
    """
    Velocity Core Engine
    
    Bu "model" değil, "cognitive execution loop"tur.
    
    LLM'ler: "Bu soruya cevap üret"
    Velocity: "Bu soruya cevap üretilebilir mi?"
    
    Bu yüzden Velocity:
    - Daha az konuşur
    - Daha çok hesaplar
    - Daha az emin görünür
    - Ama epistemik olarak daha sağlamdır
    """
    
    def __init__(
        self,
        max_hypotheses: int = 5,
        confidence_threshold: float = 0.7,
        max_iterations: int = 10,
        budget_per_hypothesis: float = 5.0,
        routing_budget: float = 10.0,
        elimination_criteria: Optional[EliminationCriteria] = None
    ):
        """
        Args:
            max_hypotheses: Maksimum paralel hipotez sayısı
            confidence_threshold: Durma threshold'u
            max_iterations: Hipotez başına max iterasyon
            budget_per_hypothesis: Hipotez başına maliyet bütçesi
            routing_budget: Routing için toplam bütçe
            elimination_criteria: Eleme kriterleri
        """
        # Components
        self.intent_parser = IntentParser()
        self.network_gate = NetworkGate()
        self.epistemic_router = EpistemicRouter()
        self.hypothesis_generator = HypothesisGenerator(max_hypotheses=max_hypotheses)
        
        # Network
        self.network_interrogator = NetworkInterrogator(
            max_parallel=max_hypotheses,
            timeout=10.0
        )
        
        # Parallel execution
        self.parallel_engine = ParallelInterrogationEngine(
            interrogator=self.network_interrogator,
            confidence_threshold=confidence_threshold,
            max_iterations=max_iterations,
            budget_per_hypothesis=budget_per_hypothesis
        )
        
        # Elimination
        self.eliminator = HypothesisEliminator(
            criteria=elimination_criteria or EliminationCriteria()
        )
        
        # Synthesis
        self.synthesizer = StateSynthesizer()
        
        # Config
        self.max_hypotheses = max_hypotheses
        self.confidence_threshold = confidence_threshold
        self.routing_budget = routing_budget
        
        logger.info("Velocity Core Engine initialized")
    
    async def execute(
        self,
        user_input: str,
        system_goal: str = "answer"
    ) -> Dict[str, Any]:
        """
        Ana execution loop
        
        Args:
            user_input: Kullanıcı girdisi
            system_goal: Sistem hedefi (answer, decide, suggest, generate, plan)
            
        Returns:
            Complete result dictionary
        """
        logger.info(f"=" * 70)
        logger.info(f"VELOCITY EXECUTION START")
        logger.info(f"Input: {user_input[:100]}...")
        logger.info(f"=" * 70)
        
        # ============================================
        # STEP 1: INTENT PARSING
        # ============================================
        logger.info("\n[1/7] INTENT PARSING")
        intent = self.intent_parser.parse(user_input, system_goal)
        logger.info(f"  Goal: {intent.goal[:60]}...")
        logger.info(f"  Type: {intent.decision_type.value}")
        logger.info(f"  Uncertainty: {intent.uncertainty:.2f}")
        logger.info(f"  Subgoals: {len(intent.subgoals)}")
        
        # ============================================
        # NETWORK GATE: Do we need the network?
        # ============================================
        gate_decision = self.network_gate.should_interrogate(intent)
        
        if not gate_decision['interrogate']:
            # Local response mode - skip network
            logger.info(f"\n[NETWORK GATE] SKIP: {gate_decision['reason']}")
            local_answer = generate_local_response(intent, gate_decision['response_mode'])
            
            return {
                'decision': local_answer,
                'confidence': 1.0,  # Local responses are certain
                'confidence_interval': (1.0, 1.0),
                'uncertainty': 'CERTAIN',
                'evidence': [],
                'contradictions': [],
                'alternatives': [],
                'intent': {
                    'goal': intent.goal,
                    'type': intent.decision_type.value,
                    'uncertainty': intent.uncertainty,
                    'subgoals': intent.subgoals
                },
                'source_breakdown': {},
                'hypotheses': {
                    'total': 0,
                    'surviving': 0,
                    'eliminated': 0
                },
                'execution_metadata': {
                    'mode': 'local_response',
                    'reason': gate_decision['reason'],
                    'network_used': False
                }
            }
        
        logger.info(f"\n[NETWORK GATE] INTERROGATE: {gate_decision['reason']}")
        
        # ============================================
        # STEP 2: EPISTEMIC ROUTING
        # ============================================
        logger.info("\n[2/7] EPISTEMIC ROUTING")
        strategies = self.epistemic_router.route(
            intent,
            max_strategies=self.max_hypotheses,
            budget=self.routing_budget
        )
        logger.info(f"  Selected {len(strategies)} source strategies:")
        for i, strategy in enumerate(strategies, 1):
            logger.info(f"    {i}. {strategy.source_type.value} "
                       f"(score: {strategy.compute_score():.2f}, "
                       f"trust: {strategy.trust_score:.2f})")
        
        if not strategies:
            logger.warning("  No strategies selected. Returning empty result.")
            return self._create_empty_result(intent, "no_strategies")
        
        # ============================================
        # STEP 3: HYPOTHESIS GENERATION
        # ============================================
        logger.info("\n[3/7] HYPOTHESIS GENERATION")
        hypotheses = self.hypothesis_generator.generate(intent, strategies)
        logger.info(f"  Generated {len(hypotheses)} hypotheses:")
        for i, h in enumerate(hypotheses, 1):
            logger.info(f"    {i}. {h.description[:60]}...")
        
        # ============================================
        # STEP 4: PARALLEL NETWORK INTERROGATION
        # ============================================
        logger.info("\n[4/7] PARALLEL NETWORK INTERROGATION")
        logger.info(f"  Running {len(hypotheses)} hypotheses in parallel...")
        
        results = await self.parallel_engine.run_parallel(hypotheses)
        
        logger.info(f"  Interrogation complete:")
        for i, result in enumerate(results, 1):
            logger.info(f"    {i}. {result.hypothesis.id[:8]}: "
                       f"confidence={result.final_confidence:.2f}, "
                       f"iterations={result.iterations}, "
                       f"converged={result.converged}")
        
        # ============================================
        # STEP 5: CONTRADICTION HANDLING & FORKING
        # ============================================
        logger.info("\n[5/7] CONTRADICTION HANDLING")
        
        # Fork hypotheses if needed
        forked_hypotheses = []
        for hypothesis in hypotheses:
            if self._should_fork(hypothesis):
                logger.info(f"  Forking hypothesis: {hypothesis.id[:8]}")
                forked = self.hypothesis_generator.fork_hypothesis(hypothesis)
                forked_hypotheses.append(forked)
        
        if forked_hypotheses:
            logger.info(f"  Created {len(forked_hypotheses)} forked hypotheses")
            # Re-run forked hypotheses
            fork_results = await self.parallel_engine.run_parallel(forked_hypotheses)
            results.extend(fork_results)
            hypotheses.extend(forked_hypotheses)
        else:
            logger.info("  No forking required")
        
        # ============================================
        # STEP 6: HYPOTHESIS ELIMINATION
        # ============================================
        logger.info("\n[6/7] HYPOTHESIS ELIMINATION")
        
        surviving, eliminated = self.eliminator.eliminate_weak(hypotheses, results)
        
        logger.info(f"  Surviving: {len(surviving)}")
        logger.info(f"  Eliminated: {len(eliminated)}")
        
        if eliminated:
            logger.info("  Elimination reasons:")
            for h in eliminated:
                logger.info(f"    - {h.id[:8]}: {h.elimination_reason}")
        
        if not surviving:
            logger.warning("  No hypotheses survived. Returning failure result.")
            return self._create_empty_result(intent, "all_eliminated")
        
        # Rank surviving
        ranked = self.eliminator.rank_hypotheses(surviving)
        logger.info(f"  Best hypothesis: {ranked[0].id[:8]} "
                   f"(confidence: {ranked[0].confidence:.2f})")
        
        # ============================================
        # STEP 7: STATE SYNTHESIS
        # ============================================
        logger.info("\n[7/7] STATE SYNTHESIS")
        
        final_state = self.synthesizer.synthesize(surviving, eliminated)
        
        logger.info(f"  Final confidence: {final_state.confidence:.2f}")
        logger.info(f"  Confidence interval: {final_state.confidence_interval}")
        logger.info(f"  Uncertainty: {final_state.uncertainty_level}")
        logger.info(f"  Evidence summary: {len(final_state.evidence_summary)} pieces")
        logger.info(f"  Contradictions: {len(final_state.contradictions)}")
        logger.info(f"  Alternatives: {len(final_state.alternatives)}")
        
        # ============================================
        # RESULT PACKAGING
        # ============================================
        logger.info(f"\n" + "=" * 70)
        logger.info(f"VELOCITY EXECUTION COMPLETE")
        logger.info(f"=" * 70)
        
        result = {
            # Core output
            "decision": final_state.decision,
            "confidence": final_state.confidence,
            "confidence_interval": final_state.confidence_interval,
            "uncertainty": final_state.uncertainty_level,
            
            # Supporting information
            "evidence": [
                {
                    "content": e.content[:200] + "...",
                    "source": e.source,
                    "confidence": e.confidence
                }
                for e in final_state.evidence_summary
            ],
            "contradictions": [
                {
                    "claim_a": c.claim_a[:100],
                    "claim_b": c.claim_b[:100],
                    "severity": c.severity,
                    "source_a": c.source_a,
                    "source_b": c.source_b
                }
                for c in final_state.contradictions
            ],
            "alternatives": final_state.alternatives,
            
            # Metadata
            "intent": {
                "goal": intent.goal,
                "type": intent.decision_type.value,
                "uncertainty": intent.uncertainty,
                "subgoals": intent.subgoals
            },
            "source_breakdown": final_state.source_breakdown,
            "hypotheses": {
                "total": len(hypotheses),
                "surviving": len(surviving),
                "eliminated": len(eliminated)
            },
            
            # Process info
            "synthesized_state": final_state,
            "execution_metadata": {
                "strategies_used": len(strategies),
                "total_evidence": final_state.metadata.get("total_evidence", 0),
                "synthesis_method": final_state.metadata.get("synthesis_method", "unknown")
            }
        }
        
        return result
    
    def _create_empty_result(
        self,
        intent: IntentGraph,
        reason: str
    ) -> Dict[str, Any]:
        """Başarısız durumlar için empty result oluştur"""
        return {
            "decision": f"Unable to process: {reason}",
            "confidence": 0.0,
            "confidence_interval": (0.0, 0.0),
            "uncertainty": "UNKNOWN",
            "evidence": [],
            "contradictions": [],
            "alternatives": [],
            "intent": {
                "goal": intent.goal,
                "type": intent.decision_type.value,
                "uncertainty": intent.uncertainty,
                "subgoals": intent.subgoals
            },
            "source_breakdown": {},
            "hypotheses": {
                "total": 0,
                "surviving": 0,
                "eliminated": 0
            },
            "execution_metadata": {
                "failure_reason": reason
            }
        }
    
    def _should_fork(self, hypothesis: Hypothesis) -> bool:
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
    
    async def can_answer(self, user_input: str) -> Dict[str, Any]:
        """
        "Bu soruya cevap üretilebilir mi?"
        
        Velocity'nin temel sorusu.
        LLM gibi "cevap üret" değil, "cevap üretilebilir mi?" diye sorar.
        
        Returns:
            {
                "answerable": bool,
                "confidence": float,
                "reason": str,
                "estimated_cost": float,
                "estimated_time": float
            }
        """
        # Intent parse et
        intent = self.intent_parser.parse(user_input)
        
        # Route et
        strategies = self.epistemic_router.route(
            intent,
            max_strategies=self.max_hypotheses
        )
        
        # Değerlendirme
        if not strategies:
            return {
                "answerable": False,
                "confidence": 0.0,
                "reason": "No suitable information sources found",
                "estimated_cost": 0.0,
                "estimated_time": 0.0
            }
        
        # Tahmini maliyet ve süre
        estimated_cost = sum(s.cost for s in strategies)
        estimated_time = len(strategies) * 2.0  # Her strateji ~2 saniye
        
        # Answerable ise yüksek expected value gerekir
        avg_expected_value = sum(s.expected_value for s in strategies) / len(strategies)
        
        answerable = avg_expected_value > 0.5 and intent.uncertainty < 0.9
        
        return {
            "answerable": answerable,
            "confidence": avg_expected_value,
            "reason": "Sufficient sources available" if answerable else "Insufficient information sources",
            "estimated_cost": estimated_cost,
            "estimated_time": estimated_time,
            "strategies": [s.source_type.value for s in strategies]
        }
