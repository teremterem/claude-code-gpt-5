"""
Custom LLM handler for routing requests to appropriate models.
"""

from typing import Any, Dict, Optional
import litellm


class CustomLLMHandler:
    """
    Routes requests to the appropriate model based on the model name.
    """

    def __init__(self):
        # Model mappings
        self.model_mappings = {
            # GPT-5 variants
            "gpt-5-reason-minimal": {
                "model": "openai/gpt-5",
                "reasoning_effort": "minimal",
            },
            "gpt-5-reason-low": {"model": "openai/gpt-5", "reasoning_effort": "low"},
            "gpt-5-reason-medium": {
                "model": "openai/gpt-5",
                "reasoning_effort": "medium",
            },
            "gpt-5-reason-high": {
                "model": "openai/gpt-5",
                "reasoning_effort": "high",
            },
            # GPT-5-mini variants
            "gpt-5-mini-reason-minimal": {
                "model": "openai/gpt-5-mini",
                "reasoning_effort": "minimal",
            },
            "gpt-5-mini-reason-low": {
                "model": "openai/gpt-5-mini",
                "reasoning_effort": "low",
            },
            "gpt-5-mini-reason-medium": {
                "model": "openai/gpt-5-mini",
                "reasoning_effort": "medium",
            },
            "gpt-5-mini-reason-high": {
                "model": "openai/gpt-5-mini",
                "reasoning_effort": "high",
            },
            # GPT-5-nano variants
            "gpt-5-nano-reason-minimal": {
                "model": "openai/gpt-5-nano",
                "reasoning_effort": "minimal",
            },
            "gpt-5-nano-reason-low": {
                "model": "openai/gpt-5-nano",
                "reasoning_effort": "low",
            },
            "gpt-5-nano-reason-medium": {
                "model": "openai/gpt-5-nano",
                "reasoning_effort": "medium",
            },
            "gpt-5-nano-reason-high": {
                "model": "openai/gpt-5-nano",
                "reasoning_effort": "high",
            },
        }

    def completion(self, model: str, messages: list, **kwargs) -> Any:
        """
        Handle completion requests.
        """
        # Check if model is in our mappings
        if model in self.model_mappings:
            params = self.model_mappings[model].copy()
            actual_model = params.pop("model")
            # Merge additional params with kwargs
            kwargs.update(params)
            return litellm.completion(model=actual_model, messages=messages, **kwargs)

        # Handle Claude models with wildcard
        if model.startswith("claude-"):
            return litellm.completion(
                model=f"anthropic/{model}", messages=messages, **kwargs
            )

        # Default fallback - pass through as-is
        return litellm.completion(model=model, messages=messages, **kwargs)

    async def acompletion(self, model: str, messages: list, **kwargs) -> Any:
        """
        Handle async completion requests.
        """
        # Check if model is in our mappings
        if model in self.model_mappings:
            params = self.model_mappings[model].copy()
            actual_model = params.pop("model")
            # Merge additional params with kwargs
            kwargs.update(params)
            return await litellm.acompletion(
                model=actual_model, messages=messages, **kwargs
            )

        # Handle Claude models with wildcard
        if model.startswith("claude-"):
            return await litellm.acompletion(
                model=f"anthropic/{model}", messages=messages, **kwargs
            )

        # Default fallback - pass through as-is
        return await litellm.acompletion(model=model, messages=messages, **kwargs)


# Create singleton instance
handler = CustomLLMHandler()