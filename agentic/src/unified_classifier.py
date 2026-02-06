"""Unified intent classification and feedback detection in a single LLM call."""
import json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from .config import Intent
from .tracing import maybe_track, update_current_span


UNIFIED_PROMPT = """You are a fitness AI assistant analyzing a user's message in context.

Determine:
1. What the user INTENDS (what they want done)
2. Whether the message contains FEEDBACK about a previous workout routine
3. If feedback is present, extract structured details

=== INPUT STRUCTURE ===

The input you receive has THREE sections:
1. Chat History - previous conversation turns (CONTEXT ONLY)
2. Previous Routines - past routines and outcomes (CONTEXT ONLY)
3. Current Query - the user's ACTUAL current message (PRIMARY)

=== INTENT TYPES ===

ROUTINE_GENERATION
- User wants a new workout, training plan, split, or program
- Examples: "give me a push workout", "make a 4 day split", "what should I train today"

REASONING
- User wants advice, analysis, explanation, or coaching insight
- Examples: "how can I improve my squat", "am I overtraining", "what muscles am I neglecting"

FEEDBACK
- User is giving feedback about a PREVIOUS routine IN THEIR CURRENT MESSAGE
- Positive: "worked well", "loved it", "saw progress", "completed it"
- Negative: "too hard", "didn't like", "wasn't effective", "couldn't finish"
- Injury/pain: "hurt my shoulder", "caused knee pain", "got injured"
- Abandonment: "stopped doing it", "gave up", "abandoned after day 2"

=== DETECTION RULES ===

**CRITICAL: Where to detect intents from:**

1. **Normal Case (default):**
   - Detect intents ONLY from the "=== Current Query ===" section
   - IGNORE feedback keywords in "Chat History" and "Previous Routines" sections
   - Those sections are context/background, NOT current user feedback

2. **Clarification Response Case (exception):**
   - IF the last Assistant message in Chat History asks "Which routine are you referring to?"
   - AND Current Query is very short/ambiguous (e.g., "1", "2", "the push one")
   - THEN use Chat History context to understand which routine the user means
   - This is ONLY for resolving clarification responses, not for intent detection

**Examples:**
- Current Query: "Give me a back routine" (Previous Routines mentions "too hard") → ROUTINE_GENERATION only (ignore context)
- Current Query: "That push routine was too hard" → FEEDBACK detected (from Current Query)
- After "Which routine?" clarification, Current Query: "1" → Use Chat History to understand "1" refers to

=== RULES ===

- A message can have MULTIPLE intents. Examples:
  "that was too hard, give me an easier one" -> FEEDBACK + ROUTINE_GENERATION
  "that routine felt easy, what should I do?" -> FEEDBACK + REASONING
- FEEDBACK can only be present if the user is commenting on a PREVIOUS routine/workout IN CURRENT QUERY
- If FEEDBACK is detected, you MUST also extract outcome and target signals
- If user wants BOTH analysis AND a routine, choose ONLY ROUTINE_GENERATION (not both)
- Valid intent combinations:
  * Single: ROUTINE_GENERATION, REASONING, or FEEDBACK
  * Double: FEEDBACK + ROUTINE_GENERATION, or FEEDBACK + REASONING
  * NEVER return both ROUTINE_GENERATION and REASONING without FEEDBACK

=== RESPONSE FORMAT ===

Respond with ONLY valid JSON:

{
  "intents": ["FEEDBACK", "ROUTINE_GENERATION"],
  "is_feedback": true,
  "feedback": {
    "outcome_type": "negative",
    "outcome_text": "too hard, couldn't complete",
    "mentioned_muscles": ["chest", "shoulder"],
    "mentioned_exercises": ["bench press"],
    "explicit_routine_refs": ["chest routine"],
    "negations": []
  }
}

If is_feedback is false, omit the "feedback" key:
{
  "intents": ["ROUTINE_GENERATION"],
  "is_feedback": false
}
"""


@dataclass
class UnifiedClassification:
    """Result of unified intent + feedback classification."""
    intents: List[str]
    classification_method: str
    is_feedback: bool
    outcome_type: Optional[str] = None
    outcome_text: Optional[str] = None
    target_signals: Optional[Dict[str, Any]] = None

    @property
    def primary_intent(self) -> str:
        """First non-FEEDBACK intent, or FEEDBACK if that's the only one."""
        for intent in self.intents:
            if intent != Intent.FEEDBACK:
                return intent
        return Intent.FEEDBACK

    @property
    def has_feedback(self) -> bool:
        return Intent.FEEDBACK in self.intents

    @property
    def has_routine_generation(self) -> bool:
        return Intent.ROUTINE_GENERATION in self.intents

    @property
    def has_reasoning(self) -> bool:
        return Intent.REASONING in self.intents

    def to_metadata(self) -> Dict[str, Any]:
        """Serialize for Opik tracing."""
        meta = {
            "intents": self.intents,
            "classification_method": self.classification_method,
            "is_feedback": self.is_feedback,
            "primary_intent": self.primary_intent,
        }
        if self.is_feedback:
            meta["outcome_type"] = self.outcome_type
            meta["outcome_text"] = self.outcome_text
            meta["target_signals"] = self.target_signals
        return meta


@maybe_track(name="unified_classify")
def unified_classify(enriched_query: str, client=None) -> UnifiedClassification:
    """
    Single LLM call that determines intents AND extracts feedback signals.

    Args:
        enriched_query: Full enriched query (chat history + episodes + current message)
        client: OpenAI client (None = keyword fallback mode)

    Returns:
        UnifiedClassification with intents and optional feedback extraction
    """
    if client is None:
        return _classify_keyword_fallback(enriched_query)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": UNIFIED_PROMPT},
                {"role": "user", "content": enriched_query}
            ],
            max_tokens=300,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content.strip())

        intents = result.get("intents", [])
        is_feedback = result.get("is_feedback", False)
        feedback_data = result.get("feedback", {})

        classification = UnifiedClassification(
            intents=intents,
            classification_method="llm",
            is_feedback=is_feedback,
            outcome_type=feedback_data.get("outcome_type") if is_feedback else None,
            outcome_text=feedback_data.get("outcome_text") if is_feedback else None,
            target_signals={
                "mentioned_muscles": feedback_data.get("mentioned_muscles", []),
                "mentioned_exercises": feedback_data.get("mentioned_exercises", []),
                "explicit_routine_refs": feedback_data.get("explicit_routine_refs", []),
                "negations": feedback_data.get("negations", [])
            } if is_feedback else None
        )

        update_current_span(metadata={
            **classification.to_metadata(),
            "raw_llm_response": result,
            "enriched_query_length": len(enriched_query),
            "llm_calls_saved": 3
        })

        return classification

    except Exception as e:
        update_current_span(metadata={
            "classification_method": "llm_error",
            "error": str(e)
        })
        return _classify_keyword_fallback(enriched_query)


def _classify_keyword_fallback(enriched_query: str) -> UnifiedClassification:
    """Deterministic keyword-based classification when no LLM client is available."""
    query_lower = enriched_query.lower()

    # Feedback detection
    feedback_keywords = [
        "too hard", "worked well", "didn't like", "completed", "stopped",
        "hurt", "injury", "pain", "abandoned", "finished", "loved", "hated",
        "too easy", "felt great", "couldn't finish", "gave up"
    ]
    is_feedback = any(kw in query_lower for kw in feedback_keywords)

    outcome_type = None
    outcome_text = None
    target_signals = None

    if is_feedback:
        # Outcome extraction
        if any(w in query_lower for w in ["hurt", "injury", "pain", "injured"]):
            outcome_type = "injury"
        elif any(w in query_lower for w in ["stopped", "abandoned", "gave up"]):
            outcome_type = "abandoned"
        elif any(w in query_lower for w in ["worked", "loved", "great", "good", "completed"]):
            outcome_type = "positive"
        else:
            outcome_type = "negative"

        outcome_text = enriched_query[:200]

        # Target signal extraction
        muscles = ["chest", "shoulder", "bicep", "tricep", "back", "leg", "quad",
                   "hamstring", "glute", "lat", "trap", "core", "calf"]
        mentioned_muscles = [m for m in muscles if m in query_lower]

        target_signals = {
            "mentioned_muscles": mentioned_muscles,
            "mentioned_exercises": [],
            "explicit_routine_refs": [],
            "negations": []
        }

    # Intent classification
    intents = []

    if is_feedback:
        intents.append(Intent.FEEDBACK)

    routine_keywords = ["give me", "make me", "create", "design", "generate",
                        "workout", "routine", "plan", "split", "program",
                        "what should I train", "easier one", "harder one", "new one"]
    if any(kw in query_lower for kw in routine_keywords):
        intents.append(Intent.ROUTINE_GENERATION)

    reasoning_keywords = ["why", "how", "should I", "am I", "is it", "what about",
                          "explain", "analyze", "advice"]
    if any(kw in query_lower for kw in reasoning_keywords):
        if Intent.ROUTINE_GENERATION not in intents:
            intents.append(Intent.REASONING)

    # Default to REASONING if no intents detected
    if not intents:
        intents = [Intent.REASONING]

    return UnifiedClassification(
        intents=intents,
        classification_method="keyword",
        is_feedback=is_feedback,
        outcome_type=outcome_type,
        outcome_text=outcome_text,
        target_signals=target_signals,
    )
