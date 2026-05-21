"""
Query Parser for Canonicalization and Intent Detection.

Provides URL-agnostic syntactic and future-ready LLM query manipulation capabilities:
1. Canonicalizing identical queries for higher hit rates.
2. Splitting queries that consist of multiple intents.
"""

import re
import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    COMPARISON = "comparison"
    EXPLANATION = "explanation"
    HOW_TO = "how_to"
    FACT_LOOKUP = "fact_lookup"
    OPINION = "opinion"
    UNKNOWN = "unknown"

@dataclass
class SubQuery:
    """Individual intent component"""
    id: str
    text: str
    intent_type: IntentType
    embedding: Optional[List[float]] = None
    cache_key: str = ""
    
    def generate_cache_key(self) -> str:
        content = f"{self.intent_type.value}:{self.text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

@dataclass
class MultiIntentQuery:
    """Original query with decomposition"""
    original_query: str
    sub_queries: List[SubQuery]
    decomposition_confidence: float

class QueryNormalizer:
    """Normalizes overlapping query styles to boost cache hits."""
    
    def __init__(self):
        # Normalization patterns: (pattern, replacement)
        self.patterns = [
            (r'^what is (an? )?(.*?)\??$', r'Explain \2'),
            (r'^how to (.*?)\??$', r'How to \1'),
            (r'^(.*?)\s+vs\.?\s+(.*?)\??$', r'Compare \1 and \2'),
            (r'^who is (.*?)\??$', r'Fact lookup \1'),
        ]
        # Compile for speed
        self._compiled = [(re.compile(p, re.IGNORECASE), r) for p, r in self.patterns]

    def normalize(self, query: str) -> str:
        """Apply rule-based canonicalization across the query."""
        normalized = query.strip()
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        # Apply patterns
        for pattern, replacement in self._compiled:
            match = pattern.match(normalized)
            if match:
                # Capitalize first letter properly
                res = pattern.sub(replacement, normalized)
                return res.capitalize()
        # Fallback: Just return as is but clean punctuation
        if normalized.endswith("?"):
             normalized = normalized[:-1]
        return normalized.capitalize()

class BaseIntentDetector:
    def decompose(self, query: str) -> MultiIntentQuery:
        raise NotImplementedError

    def synthesize(self, original_query: str, responses: List[str]) -> str:
        raise NotImplementedError

class RuleBasedIntentDetector(BaseIntentDetector):
    """Syntactic-based splitting using conjunctions."""
    
    def __init__(self):
        # Split tokens: comma+and, periods, question marks, explicit phrases
        self.split_regex = re.compile(r',\s*and\s+|\s+as well as\s+|\s+along with\s+|\.\s+|\?\s+(?=[A-Z])', re.IGNORECASE)

    def _determine_intent(self, text: str) -> IntentType:
        t = text.lower()
        if "compare" in t or "vs" in t or "difference" in t:
            return IntentType.COMPARISON
        if "how to" in t or "guide" in t or "steps" in t:
            return IntentType.HOW_TO
        if "what is" in t or "explain" in t:
            return IntentType.EXPLANATION
        return IntentType.UNKNOWN

    def decompose(self, query: str) -> MultiIntentQuery:
        parts = self.split_regex.split(query.strip())
        sub_queries = []
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            intent_type = self._determine_intent(part)
            sq_id = f"sq_{hashlib.sha256(part.encode()).hexdigest()[:8]}"
            sq = SubQuery(id=sq_id, text=part, intent_type=intent_type)
            sq.cache_key = sq.generate_cache_key()
            sub_queries.append(sq)
        
        confidence = 1.0 if len(sub_queries) == 1 else 0.8
        return MultiIntentQuery(
            original_query=query, 
            sub_queries=sub_queries, 
            decomposition_confidence=confidence
        )

    def synthesize(self, original_query: str, responses: List[str]) -> str:
        # Simple concat synthesis for rules
        if not responses:
            return ""
        if len(responses) == 1:
            return responses[0]
        
        combined = "Here are the answers to the parts of your query:\n\n"
        for i, r in enumerate(responses):
            combined += f"{i+1}. {r}\n"
        return combined

import logging
from src.ml.local_llm_service import LocalLLMService

logger = logging.getLogger(__name__)

class HybridIntentDetector(BaseIntentDetector):
    """
    Implements a 'Local LLM First' execution path.
    Falls back to RuleBasedIntentDetector if LLM fails or is unavailable.
    """
    def __init__(self, local_llm: Optional['LocalLLMService'] = None):
        self.local_llm = local_llm or LocalLLMService()
        self.rule_based = RuleBasedIntentDetector()

    async def decompose_async(self, query: str) -> MultiIntentQuery:
        try:
            # Attempt Local LLM First
            sub_queries_texts = await self.local_llm.decompose_query(query)
            if not isinstance(sub_queries_texts, list) or not sub_queries_texts:
                raise ValueError("Invalid decomposition result from LLM")

            # Map to exact MultiIntentQuery payload
            sub_queries = []
            for part in sub_queries_texts:
                part = part.strip()
                if not part: continue
                intent_type = self.rule_based._determine_intent(part)
                sq_id = f"sq_{hashlib.sha256(part.encode()).hexdigest()[:8]}"
                sq = SubQuery(id=sq_id, text=part, intent_type=intent_type)
                sq.cache_key = sq.generate_cache_key()
                sub_queries.append(sq)
            
            confidence = 1.0 if len(sub_queries) == 1 else 0.9
            return MultiIntentQuery(
                original_query=query, 
                sub_queries=sub_queries, 
                decomposition_confidence=confidence
            )
        except Exception as e:
            logger.warning(f"Local LLM decomposition failed, falling back to rule-based: {e}")
            return self.rule_based.decompose(query)

    async def synthesize_async(self, original_query: str, responses: List[str]) -> str:
        try:
            # Attempt Local LLM First
            result = await self.local_llm.synthesize_response(original_query, responses)
            if not result:
                raise ValueError("Empty synthesis result")
            return result
        except Exception as e:
            logger.warning(f"Local LLM synthesis failed, falling back to rule-based: {e}")
            return self.rule_based.synthesize(original_query, responses)
