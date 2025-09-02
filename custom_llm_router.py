from __future__ import annotations

from typing import Any, Dict, List, Optional

import litellm


class CustomLLMRouter:
    """
    Routes model requests to the correct provider and parameters.
    """

    def _map_model(self, model: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if model.startswith("claude-"):
            params["model"] = f"anthropic/{model}"
            return params
        if model.startswith("gpt-5"):
            base: str
            if model.startswith("gpt-5-mini"):
                base = "openai/gpt-5-mini"
            elif model.startswith("gpt-5-nano"):
                base = "openai/gpt-5-nano"
            else:
                base = "openai/gpt-5"
            params["model"] = base
            if "reason-minimal" in model:
                params["reasoning_effort"] = "minimal"
            elif "reason-low" in model:
                params["reasoning_effort"] = "low"
            elif "reason-medium" in model:
                params["reasoning_effort"] = "medium"
            elif "reason-high" in model:
                params["reasoning_effort"] = "high"
            params.update({k: v for k, v in kwargs.items() if k != "model"})
            return params
        params["model"] = model
        params.update({k: v for k, v in kwargs.items() if k != "model"})
        return params

    def completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        mapped = self._map_model(model, kwargs)
        if api_key is not None:
            mapped["api_key"] = api_key
        return litellm.completion(messages=messages, **mapped)

    async def acompletion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        mapped = self._map_model(model, kwargs)
        if api_key is not None:
            mapped["api_key"] = api_key
        return await litellm.acompletion(messages=messages, **mapped)

    def streaming(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        mapped = self._map_model(model, kwargs)
        if api_key is not None:
            mapped["api_key"] = api_key
        mapped["stream"] = True
        return litellm.completion(messages=messages, **mapped)

    async def astreaming(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        mapped = self._map_model(model, kwargs)
        if api_key is not None:
            mapped["api_key"] = api_key
        mapped["stream"] = True
        return await litellm.acompletion(messages=messages, **mapped)


custom_llm_router = CustomLLMRouter()
