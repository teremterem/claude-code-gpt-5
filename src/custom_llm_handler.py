from __future__ import annotations

from typing import Any, Dict, Tuple
import re

import litellm


def route_model(requested_model: str) -> Tuple[str, Dict[str, Any]]:
    """
    Map a friendly model alias to a provider model and extra params.

    Supported patterns:
    - gpt-5(-mini|-nano)?-reason-(minimal|low|medium|high)
      -> maps to openai/gpt-5[(-mini|-nano)] with reasoning_effort
    - claude-* -> maps directly to anthropic/claude-*

    Returns a tuple of (provider_model, extra_params)
    """
    model = requested_model.strip()

    # Claude passthrough (kept for Claude Code fast model usage)
    if model.startswith("claude-"):
        return f"anthropic/{model}", {}

    # GPT-5 family with reasoning effort
    m = re.fullmatch(
        r"gpt-5(?P<variant>-(mini|nano))?-reason-(?P<effort>minimal|low|medium|high)",
        model,
    )
    if m:
        variant = m.group("variant") or ""
        effort = m.group("effort")
        provider_model = f"openai/gpt-5{variant or ''}"
        return provider_model, {"reasoning_effort": effort}

    # Default passthrough – use as-is
    return model, {}


class CustomLLMHandler:
    """LiteLLM custom handler that routes model aliases.

    The proxy is configured with a single wildcard mapping to this handler.
    This handler inspects the requested `model` string and forwards the
    call to the appropriate provider + parameters via litellm.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - lifecycle hook
        pass

    # Synchronous completion
    def completion(self, model: str, *args: Any, **kwargs: Any):  # pragma: no cover - runtime path
        target_model, extra = route_model(model)
        merged = {**kwargs, **extra}
        return litellm.completion(model=target_model, *args, **merged)

    # Async completion
    async def acompletion(self, model: str, *args: Any, **kwargs: Any):  # pragma: no cover
        target_model, extra = route_model(model)
        merged = {**kwargs, **extra}
        return await litellm.acompletion(model=target_model, *args, **merged)

    # Embeddings passthrough (if ever invoked)
    def embeddings(self, model: str, *args: Any, **kwargs: Any):  # pragma: no cover
        target_model, extra = route_model(model)
        merged = {**kwargs, **extra}
        return litellm.embeddings(model=target_model, *args, **merged)

