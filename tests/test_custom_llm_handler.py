from src.custom_llm_handler import route_model


def test_claude_passthrough():
    model, params = route_model("claude-3-haiku-20240307")
    assert model == "anthropic/claude-3-haiku-20240307"
    assert params == {}


def test_gpt5_reason_low():
    model, params = route_model("gpt-5-reason-low")
    assert model == "openai/gpt-5"
    assert params == {"reasoning_effort": "low"}


def test_gpt5_mini_reason_high():
    model, params = route_model("gpt-5-mini-reason-high")
    assert model == "openai/gpt-5-mini"
    assert params == {"reasoning_effort": "high"}


def test_gpt5_nano_reason_minimal():
    model, params = route_model("gpt-5-nano-reason-minimal")
    assert model == "openai/gpt-5-nano"
    assert params == {"reasoning_effort": "minimal"}


def test_default_passthrough():
    model, params = route_model("openai/gpt-4o")
    assert model == "openai/gpt-4o"
    assert params == {}

