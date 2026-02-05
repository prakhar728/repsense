"""Structured output models for tracing.

These dataclasses provide rich, typed data structures that can be
serialized to Opik metadata. They're designed to capture decision
context for debugging and evaluation.

Usage:
    result = ResolutionResult(
        type="resolved",
        routine_id="abc123",
        ...
    )
    update_current_span(metadata=result.to_metadata())
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Literal


@dataclass
class ScoreBreakdown:
    """Breakdown of scoring factors for a routine candidate."""
    recency: float = 0.0
    same_chat: float = 0.0
    missing_outcome: float = 0.0
    target_match: float = 0.0
    negation: float = 0.0
    total: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class ScoredCandidate:
    """A routine candidate with its scoring breakdown."""
    routine_id: str
    title: str
    total_score: float
    score_breakdown: ScoreBreakdown
    muscles: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "routine_id": self.routine_id,
            "title": self.title,
            "total_score": self.total_score,
            "muscles": self.muscles,
            "score_breakdown": self.score_breakdown.to_dict()
        }


@dataclass
class ResolutionResult:
    """Result of routine resolution with full context for tracing."""
    type: Literal["resolved", "clarification", "ignore"]
    routine_id: Optional[str] = None
    outcome_type: Optional[str] = None
    outcome_text: Optional[str] = None
    candidates_considered: int = 0
    top_score: Optional[float] = None
    score_gap: Optional[float] = None
    signals_used: Dict[str, Any] = field(default_factory=dict)
    scored_candidates: List[ScoredCandidate] = field(default_factory=list)

    def to_metadata(self) -> Dict[str, Any]:
        """Convert to Opik metadata format."""
        return {
            "resolution_type": self.type,
            "resolved_routine_id": self.routine_id,
            "outcome_type": self.outcome_type,
            "outcome_text": self.outcome_text,
            "candidates_considered": self.candidates_considered,
            "top_score": self.top_score,
            "score_gap": self.score_gap,
            "signals_used": self.signals_used,
            "scored_candidates": [c.to_dict() for c in self.scored_candidates[:5]]
        }

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format (without tracing details)."""
        if self.type == "resolved":
            return {
                "type": "resolved",
                "routine_id": self.routine_id,
                "outcome_type": self.outcome_type,
                "outcome_text": self.outcome_text,
            }
        elif self.type == "clarification":
            return {
                "type": "clarification",
                "candidates": [
                    {"id": c.routine_id, "title": c.title}
                    for c in self.scored_candidates[:3]
                ]
            }
        else:
            return {"type": "ignore"}


@dataclass
class FeedbackDetectionResult:
    """Result of feedback detection stage."""
    is_feedback: bool
    detection_method: Literal["llm", "keyword"]

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "is_feedback": self.is_feedback,
            "detection_method": self.detection_method
        }


@dataclass
class OutcomeExtraction:
    """Extracted outcome from feedback."""
    outcome_type: Literal["positive", "negative", "injury", "abandoned"]
    outcome_text: str
    extraction_method: Literal["llm", "keyword"]

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "outcome_type": self.outcome_type,
            "outcome_text": self.outcome_text,
            "extraction_method": self.extraction_method
        }


@dataclass
class TargetSignals:
    """Extracted target signals from feedback message."""
    mentioned_muscles: List[str] = field(default_factory=list)
    mentioned_exercises: List[str] = field(default_factory=list)
    explicit_routine_refs: List[str] = field(default_factory=list)
    negations: List[str] = field(default_factory=list)
    extraction_method: Literal["llm", "keyword"] = "keyword"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mentioned_muscles": self.mentioned_muscles,
            "mentioned_exercises": self.mentioned_exercises,
            "explicit_routine_refs": self.explicit_routine_refs,
            "negations": self.negations
        }

    def to_metadata(self) -> Dict[str, Any]:
        return {
            **self.to_dict(),
            "extraction_method": self.extraction_method,
            "total_signals": len(self.mentioned_muscles) + len(self.mentioned_exercises)
        }


@dataclass
class IntentClassificationResult:
    """Result of intent classification."""
    intent: Literal["ROUTINE_GENERATION", "REASONING"]
    classification_method: Literal["llm", "keyword"]
    query_params: Optional[Dict[str, Any]] = None

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "classification_method": self.classification_method,
            "query_params": self.query_params
        }


@dataclass
class MemoryEnrichmentContext:
    """Context about memory enrichment for a query."""
    chat_messages_count: int
    episodic_memories_count: int
    enriched_query_length: int
    original_query_length: int

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "chat_messages_count": self.chat_messages_count,
            "episodic_memories_count": self.episodic_memories_count,
            "enriched_query_length": self.enriched_query_length,
            "original_query_length": self.original_query_length,
            "context_expansion_ratio": (
                self.enriched_query_length / self.original_query_length
                if self.original_query_length > 0 else 0
            )
        }


@dataclass
class GenerationContext:
    """Context about facts provided to generation."""
    facts_count: int
    facts_text_length: int
    generation_type: Literal["routine", "advice"]
    target_type: Optional[str] = None
    target_value: Optional[str] = None

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "facts_count": self.facts_count,
            "facts_text_length": self.facts_text_length,
            "generation_type": self.generation_type,
            "target_type": self.target_type,
            "target_value": self.target_value
        }
