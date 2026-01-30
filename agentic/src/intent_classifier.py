"""Intent classification using LLM."""
import json
from .config import Intent


INTENT_PROMPT = """Classify the user's fitness query into one of two intents:

DATA_ACCESS - User wants to see/view/list their workout data
Examples: "show my bench press history", "what did I do last week", "list chest exercises"

REASONING - User wants advice, analysis, or coaching
Examples: "how can I improve my squat", "am I overtraining", "why am I stuck"

Respond with ONLY the intent label: DATA_ACCESS or REASONING"""


def classify_intent(query: str, client=None) -> str:
    """Classify query as DATA_ACCESS or REASONING."""
    if client is None:
        return _classify_mock(query)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": INTENT_PROMPT},
            {"role": "user", "content": query}
        ],
        max_tokens=20
    )
    
    result = response.choices[0].message.content.strip().upper()
    return Intent.DATA_ACCESS if "DATA" in result else Intent.REASONING


def _classify_mock(query: str) -> str:
    """Fallback keyword-based classification."""
    data_keywords = ["show", "list", "see", "display", "what did", "history"]
    if any(kw in query.lower() for kw in data_keywords):
        return Intent.DATA_ACCESS
    return Intent.REASONING
