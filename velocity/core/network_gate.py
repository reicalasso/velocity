"""
Network Interrogation Gate

"Do I need the network?" decision logic.

Velocity is smart: doesn't interrogate when not needed.
"""

from .intent_parser import IntentGraph, DecisionType
from typing import Dict, Any
from loguru import logger


class NetworkGate:
    """
    Decides whether network interrogation is necessary
    
    Key insight: Not every query needs the network.
    Social, meta, and high-confidence local queries can skip it.
    """
    
    # Intent types that NEVER need network
    NO_NETWORK_INTENTS = {
        DecisionType.SOCIAL,
        DecisionType.META,
        DecisionType.CREATIVE
    }
    
    def __init__(self):
        pass
    
    def should_interrogate(
        self,
        intent: IntentGraph,
        local_confidence: float = 0.0
    ) -> Dict[str, Any]:
        """
        Decide if network interrogation is needed
        
        Args:
            intent: Parsed intent
            local_confidence: Confidence in local response (0-1)
            
        Returns:
            Decision dict with 'interrogate' (bool) and 'reason' (str)
        """
        
        # Rule 1: Social intents → No network
        if intent.decision_type == DecisionType.SOCIAL:
            logger.info("Network gate: SKIP (social intent)")
            return {
                'interrogate': False,
                'reason': 'social_intent',
                'response_mode': 'local_social'
            }
        
        # Rule 2: Meta intents → No network (answer about Velocity)
        if intent.decision_type == DecisionType.META:
            logger.info("Network gate: SKIP (meta intent)")
            return {
                'interrogate': False,
                'reason': 'meta_intent',
                'response_mode': 'local_meta'
            }
        
        # Rule 3: Creative intents → No network (Velocity doesn't tell stories)
        if intent.decision_type == DecisionType.CREATIVE:
            logger.info("Network gate: SKIP (creative intent)")
            return {
                'interrogate': False,
                'reason': 'creative_intent',
                'response_mode': 'local_decline'
            }
        
        # Rule 4: High local confidence → Skip network
        if local_confidence > 0.8:
            logger.info(f"Network gate: SKIP (high local confidence: {local_confidence:.2f})")
            return {
                'interrogate': False,
                'reason': 'high_local_confidence',
                'response_mode': 'local_answer'
            }
        
        # Rule 5: Factual, comparative, analytical → Network needed
        logger.info(f"Network gate: INTERROGATE ({intent.decision_type.value})")
        return {
            'interrogate': True,
            'reason': f'{intent.decision_type.value}_requires_network',
            'response_mode': 'network_interrogation'
        }


def generate_local_response(
    intent: IntentGraph,
    response_mode: str
) -> str:
    """
    Generate local response without network
    
    For social, meta, and declined creative requests
    """
    
    if response_mode == 'local_social':
        # Social responses (contextual, natural)
        return _social_response(intent.goal)
    
    elif response_mode == 'local_meta':
        # About Velocity itself
        return _meta_response(intent.goal)
    
    elif response_mode == 'local_decline':
        # Politely decline creative requests
        return _decline_creative(intent.goal)
    
    else:
        return "I couldn't determine how to respond to your query."


def _social_response(query: str) -> str:
    """Generate social response"""
    query_lower = query.lower()
    
    # Greetings
    if any(word in query_lower for word in ['hi', 'hello', 'hey', 'selam', 'merhaba']):
        return "Hello! I'm Velocity, a network-native cognitive engine. How can I help you today?"
    
    # How are you
    if any(phrase in query_lower for phrase in ['how are you', 'nasılsın', 'naber']):
        return "I'm functioning well, thank you! I'm ready to search the web and answer your questions. What would you like to know?"
    
    # Thanks
    if any(word in query_lower for word in ['thanks', 'thank', 'teşekkür']):
        return "You're welcome! Feel free to ask anything else."
    
    # Goodbye
    if any(word in query_lower for word in ['bye', 'goodbye', 'hoşça', 'görüşürüz']):
        return "Goodbye! Come back anytime you need information."
    
    # Default
    return "Hello! How can I assist you today?"


def _meta_response(query: str) -> str:
    """Generate response about Velocity itself"""
    return """I'm Velocity, a network-native cognitive engine. I answer questions by:

1. Parsing your intent
2. Searching the web in real-time
3. Synthesizing information from multiple sources
4. Providing calibrated answers with confidence scores

I don't use LLMs - just NLP and real web search. Ask me anything factual!"""


def _decline_creative(query: str) -> str:
    """Politely decline creative requests"""
    return """I'm designed for factual information retrieval, not creative content generation. 

I can help you with:
- Factual questions (What is X?)
- Comparisons (X vs Y)
- Technical information
- Current events
- Code examples

Try asking me something factual instead!"""
