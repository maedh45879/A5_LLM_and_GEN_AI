from app.orchestration.router import IntentRouter


def test_intent_router_heuristics():
    router = IntentRouter()
    assert router.route("I want to reserve a table").intent == "reservation"
    assert router.route("Can I order two pizzas?").intent == "order"
    assert router.route("What allergens are in the risotto?").intent == "menu"
    assert router.route("Where is your location?").intent == "general"


def test_intent_router_fallback():
    router = IntentRouter()
    result = router.route("Hello there")
    assert result.intent in {"general", "fallback"}
