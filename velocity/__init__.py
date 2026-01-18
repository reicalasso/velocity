"""
VELOCITY PARADIGM
Network-Native, Dataset-Free General Intelligence

Where knowledge lives in the world,
and intelligence lives in the speed of interrogation.

Algoritmik Çekirdek:
1. Intent Parsing - Problemi tanımla
2. Epistemic Routing - Hangi kaynaklara bakılacağına karar ver
3. Hypothesis Generation - Paralel hipotez uzayı oluştur
4. Network Interrogation - Dinamik sorgu döngüsü
5. Contradiction Handling - State forking
6. Hypothesis Elimination - Zayıf hipotezleri ele
7. State Synthesis - Final kararı oluştur
"""

# New Core (Algorithmic Kernel)
from .core.velocity_core import VelocityCore
from .core.intent_parser import IntentParser, IntentGraph
from .core.epistemic_router import EpistemicRouter, SourceStrategy
from .core.hypothesis_generator import HypothesisGenerator, Hypothesis
from .core.interrogation_loop import InterrogationLoop, ParallelInterrogationEngine
from .core.hypothesis_eliminator import HypothesisEliminator, EliminationCriteria
from .core.state_synthesizer import StateSynthesizer, SynthesizedState

# Legacy (for compatibility)
from .core.engine import VelocityEngine
from .core.state import CognitiveState
from .network.interrogator import NetworkInterrogator
from .evaluation.hypothesis import HypothesisEvaluator

__version__ = "0.2.0"  # Algorithmic Core
__all__ = [
    # New Core
    "VelocityCore",
    "IntentParser",
    "IntentGraph",
    "EpistemicRouter",
    "SourceStrategy",
    "HypothesisGenerator",
    "Hypothesis",
    "InterrogationLoop",
    "ParallelInterrogationEngine",
    "HypothesisEliminator",
    "EliminationCriteria",
    "StateSynthesizer",
    "SynthesizedState",
    
    # Legacy
    "VelocityEngine",
    "CognitiveState",
    "NetworkInterrogator",
    "HypothesisEvaluator",
]
