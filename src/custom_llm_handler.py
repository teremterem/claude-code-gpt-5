
"""
Custom LiteLLM handler that routes model names to providers.
"""

import re
from typing import Any, Dict, List, Tuple

from litellm import CustomLLM, completion as litellm_completion


class CustomLLMHandler(CustomLLM):
    """
    Routes incoming model names like "gpt-5-..." or "claude-*" to the correct provider/model with optional reasoning_effort.
    """

    def _parse(self, model: str) -> Tuple[str, Dict[str, Any]]:
        m = re.search(r"reason-(minimal|low|medium|high)", model)
        level = m.group(1) if m else None
        extra: Dict[str, Any] = {}
        if model.startswith("gpt-5-nano"):
            target = "openai/gpt-5-nano"
            if level is not None:
                extra["reasoning_effort"] = level
            return target, extra
        if model.startswith("gpt-5-mini"):
            target = "openai/gpt-5-mini"
            if level is not None:
                extra["reasoning_effort"] = level
            return target, extra
        if model.startswith("gpt-5"):
            target = "openai/gpt-5"
            if level is not None:
                extra["reasoning_effort"] = level
            return target, extra
        if model.startswith("claude-"):
            return f"anthropic/{model}", extra
        if "/" in model:
            return model, extra
        return model, extra

    def completion(self, messages: List[Dict[str, Any]], model: str, stream: bool = False, **kwargs: Any):
        try:
            target_model, extra = self._parse(model)
            merged = {**kwargs, **extra}
            return litellm_completion(model=target_model, messages=messages, stream=stream, **merged)
        except Exception as e:  # pylint: disable=broad-except
            raise RuntimeError("CustomLLMHandler completion failed") from e

    async def acompletion(self, messages: List[Dict[str, Any]], model: str, stream: bool = False, **kwargs: Any):
        try:
            target_model, extra = self._parse(model)
            merged = {**kwargs, **extra}
            from litellm import acompletion as litellm_acompletion

            return await litellm_acompletion(model=target_model, messages=messages, stream=stream, **merged)
        except Exception as e:  # pylint: disable=broad-except
            raise RuntimeError("CustomLLMHandler acompletion failed") from e
