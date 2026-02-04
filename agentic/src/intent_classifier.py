"""Intent classification using LLM."""
import json
from .config import Intent


# INTENT_PROMPT = """Classify the user's fitness query into one of two intents:

# DATA_ACCESS - User wants to see/view/list their workout data
# Examples: "show my bench press history", "what did I do last week", "list chest exercises"

# REASONING - User wants advice, analysis, or coaching
# Examples: "how can I improve my squat", "am I overtraining", "why am I stuck"

# Respond with ONLY the intent label: DATA_ACCESS or REASONING"""

INTENT_PROMPT = """Classify the user's fitness query into one of the following intents:

ROUTINE_GENERATION
- User asks for a workout, training plan, split, or program
- User implies wanting a routine or plan to follow
Examples:
"give me a push workout"
"make a 4 day gym split"
"I want a leg day routine"
"design a plan to build muscle"
"what should I train today"

REASONING
- User asks for advice, analysis, explanation, or coaching
- User wants insight, feedback, or understanding
Examples:
"how can I improve my squat"
"am I overtraining"
"why am I stuck at the same weight"
"what muscles am I neglecting"

Respond with ONLY one label:
ROUTINE_GENERATION or REASONING
"""

def classify_intent(query: str, client=None) -> str:
    """Classify query as REASONING or ROUTINE_GENERATION."""
    if client is None:
        return _classify_mock(query)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": INTENT_PROMPT},
            {"role": "user", "content": query}
        ],
        max_tokens=25
    )
    
    result = response.choices[0].message.content.strip().upper()
    return Intent.ROUTINE_GENERATION if "ROUTINE_GENERATION" in result else Intent.REASONING


# def classify_intent(query: str, client=None) -> str:
#     """Classify query as DATA_ACCESS or REASONING."""
#     if client is None:
#         return _classify_mock(query)
    
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": INTENT_PROMPT},
#             {"role": "user", "content": query}
#         ],
#         max_tokens=20
#     )
    
#     result = response.choices[0].message.content.strip().upper()
#     return Intent.DATA_ACCESS if "DATA" in result else Intent.REASONING


def _classify_mock(query: str) -> str:
    """Fallback keyword-based classification."""
    data_keywords = ["show", "list", "see", "display", "what did", "history"]
    if any(kw in query.lower() for kw in data_keywords):
        return Intent.ROUTINE_GENERATION
    return Intent.REASONING
