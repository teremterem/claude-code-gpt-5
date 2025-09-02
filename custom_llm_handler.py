"""
Custom LLM handler for routing requests to appropriate models.
"""

import re
from typing import Any, Dict, Optional
from litellm import completion


class CustomLLMHandler:
    """
    Custom handler that routes model requests to appropriate providers.
    """

    def completion(self, model: str, messages: list, **kwargs) -> Any:
        """
        Route completion requests based on model name patterns.
        
        Args:
            model: The requested model name
            messages: The chat messages
            **kwargs: Additional parameters
            
        Returns:
            Completion response from the appropriate provider
        """
        # Handle GPT-5 variants with reasoning effort
        if model.startswith("gpt-5"):
            return self._handle_gpt5_model(model, messages, **kwargs)
        
        # Handle Claude models (wildcard matching)
        elif model.startswith("claude-"):
            return self._handle_claude_model(model, messages, **kwargs)
        
        # Fallback for unknown models
        else:
            raise ValueError(f"Unknown model: {model}")

    def _handle_gpt5_model(self, model: str, messages: list, **kwargs) -> Any:
        """
        Handle GPT-5 model variants with reasoning effort levels.
        """
        # Parse model name to extract base model and reasoning effort
        base_model, reasoning_effort = self._parse_gpt5_model(model)
        
        # Map to OpenAI model
        openai_model = f"openai/{base_model}"
        
        # Add reasoning_effort to kwargs if specified
        if reasoning_effort:
            kwargs["reasoning_effort"] = reasoning_effort
        
        return completion(model=openai_model, messages=messages, **kwargs)

    def _handle_claude_model(self, model: str, messages: list, **kwargs) -> Any:
        """
        Handle Claude model requests by routing to Anthropic.
        """
        # Map to Anthropic model
        anthropic_model = f"anthropic/{model}"
        
        return completion(model=anthropic_model, messages=messages, **kwargs)

    def _parse_gpt5_model(self, model: str) -> tuple[str, Optional[str]]:
        """
        Parse GPT-5 model name to extract base model and reasoning effort.
        
        Returns:
            Tuple of (base_model, reasoning_effort)
        """
        # Pattern to match gpt-5 variants with reasoning effort
        pattern = r"(gpt-5(?:-mini|-nano)?)-reason-(\w+)"
        match = re.match(pattern, model)
        
        if match:
            base_model = match.group(1)
            reasoning_effort = match.group(2)
            return base_model, reasoning_effort
        
        # Handle base models without reasoning effort
        if model in ["gpt-5", "gpt-5-mini", "gpt-5-nano"]:
            return model, None
        
        raise ValueError(f"Invalid GPT-5 model format: {model}")


# Create global instance
custom_llm_handler = CustomLLMHandler()