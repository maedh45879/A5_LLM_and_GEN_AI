from dataclasses import dataclass
from typing import Dict, Optional

from langchain.schema.language_model import BaseLanguageModel


INTENTS = ("reservation", "order", "menu", "general", "fallback")


@dataclass
class IntentResult:
    intent: str
    score: float
    reason: str = ""


class IntentRouter:
    """
    Lightweight intent classifier using heuristics with optional LLM fallback.
    """

    def __init__(self, model: Optional[BaseLanguageModel] = None):
        self.model = model
        self.keyword_map: Dict[str, set[str]] = {
            "reservation": {"reserve", "book", "table", "reservation", "booking"},
            "order": {"order", "takeaway", "delivery", "pickup", "dish"},
            "menu": {"menu", "ingredient", "allergen", "special", "promo"},
            "general": {"hours", "opening", "location", "address", "parking"},
        }

    def heuristic_route(self, text: str) -> IntentResult:
        lower = text.lower()
        scores = {intent: 0 for intent in INTENTS}
        for intent, keywords in self.keyword_map.items():
            for kw in keywords:
                if kw in lower:
                    scores[intent] += 1
        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]
        if max_score == 0:
            return IntentResult(intent="fallback", score=0, reason="no keyword hit")
        return IntentResult(intent=best_intent, score=max_score, reason="keyword match")

    def llm_route(self, text: str) -> Optional[IntentResult]:
        if not self.model:
            return None
        prompt = (
            "Classify the user request into one of: reservation, order, menu, general.\n"
            f"User: {text}\nReturn the intent only."
        )
        try:
            response = self.model.invoke(prompt)
            label = response.content.strip().lower()
            if label not in INTENTS:
                label = "fallback"
            return IntentResult(intent=label, score=0.5, reason="llm classification")
        except Exception:
            return None

    def route(self, text: str) -> IntentResult:
        heuristic = self.heuristic_route(text)
        if heuristic.intent != "fallback":
            return heuristic
        llm_guess = self.llm_route(text)
        return llm_guess or heuristic
