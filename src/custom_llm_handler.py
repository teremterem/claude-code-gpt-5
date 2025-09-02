"""
CustomLLMHandler for LiteLLM proxy.

This handler maps friendly model names used by Claude Code to the
corresponding provider models and parameters, so we don't need an
explicit mapping for each variant in config.yaml.

Supported patterns:
- gpt-5[-mini|-nano]-reason-(minimal|low|medium|high)
  -> model: openai/gpt-5[-mini|-nano], reasoning_effort accordingly
- claude-* -> model: anthropic/claude-*

Any other model name that already includes a provider prefix (e.g.,
"openai/gpt-5") is passed through unchanged.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Tuple


class CustomLLMHandler:
    """LiteLLM custom handler that rewrites model names and forwards calls.

    This class provides both sync and async completion methods to match how
    LiteLLM might invoke providers. It uses litellm's built-in providers to
    make the final API call after rewriting the model and params.
    """

    GPT5_PATTERN = re.compile(
        r"^(?P<base>gpt-5)(?P<size>-mini|-nano)?-reason-(?P<effort>minimal|low|medium|high)$"
    )

    def __init__(self, *_: Any, **__: Any) -> None:
        pass

    @classmethod
    def _map_model(cls, model: str) -> Tuple[str, Dict[str, Any]]:
        """Return (provider_model, extra_params) for a given input model.

        - For GPT‑5 variants, sets the appropriate OpenAI model and
          `reasoning_effort`.
        - For Claude models, prefixes with `anthropic/`.
        - For already-qualified models (contain "/"), pass through.
        """
        # Already-qualified provider/model
        if "/" in model:
            return model, {}

        # Claude fast models
        if model.startswith("claude-"):
            return f"anthropic/{model}", {}

        # GPT‑5 variants with reasoning effort
        m = cls.GPT5_PATTERN.match(model)
        if m is not None:
            base = m.group("base")  # gpt-5
            size = m.group("size") or ""  # "", "-mini", or "-nano"
            effort = m.group("effort")
            provider_model = f"openai/{base}{size}"
            return provider_model, {"reasoning_effort": effort}

        raise ValueError(
            f"Unsupported model alias '{model}'. Expected 'gpt-5[-mini|-nano]-reason-<level>' "
            "or 'claude-*', or a fully-qualified 'provider/model'."
        )

    # Async API
    async def acompletion(self, *, model: str, messages: Any, **kwargs: Any) -> Any:
        """Async chat.completions entrypoint used by LiteLLM.

        We rewrite the model and forward to litellm.acompletion.
        """
        from litellm import acompletion  # lazy import to keep startup light

        provider_model, extra = self._map_model(model)
        merged_kwargs = {**kwargs, **extra}
        # Avoid infinite recursion by ensuring we call a provider model
        # (we only ever return provider-qualified models from _map_model).
        return await acompletion(model=provider_model, messages=messages, **merged_kwargs)

    # Sync API
    def completion(self, *, model: str, messages: Any, **kwargs: Any) -> Any:
        """Sync chat.completions entrypoint used by LiteLLM.

        We rewrite the model and forward to litellm.completion.
        """
        from litellm import completion  # lazy import to keep startup light

        provider_model, extra = self._map_model(model)
        merged_kwargs = {**kwargs, **extra}
        return completion(model=provider_model, messages=messages, **merged_kwargs)

    # Embeddings passthrough if needed in future
    async def aembedding(self, *, model: str, input: Any, **kwargs: Any) -> Any:  # noqa: A003
        from litellm import aembedding  # type: ignore[attr-defined]

        provider_model, extra = self._map_model(model)
        merged_kwargs = {**kwargs, **extra}
        return await aembedding(model=provider_model, input=input, **merged_kwargs)

    def embedding(self, *, model: str, input: Any, **kwargs: Any) -> Any:  # noqa: A003
        from litellm import embedding  # type: ignore[attr-defined]

        provider_model, extra = self._map_model(model)
        merged_kwargs = {**kwargs, **extra}
        return embedding(model=provider_model, input=input, **merged_kwargs)

