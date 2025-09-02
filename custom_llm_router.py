from typing import Any, Generator, AsyncGenerator, Optional

import litellm


class CustomLLMRouter(litellm.CustomLLM):
    def _to_generic_streaming_chunk(
        self, chunk: "litellm.ModelResponseStream"
    ) -> "litellm.GenericStreamingChunk":
        """Convert a ModelResponseStream to a GenericStreamingChunk.

        This normalizes streamed chunks for LiteLLM's CustomStreamWrapper, which expects
        an OpenAI-like generic chunk dict.
        """
        # Extract text
        try:
            text: str = litellm.utils.get_response_string(chunk) or ""
        except Exception:
            text = ""

        # Extract index and finish reason from the first choice
        index: int = 0
        finish_reason: Optional[str] = None
        try:
            if getattr(chunk, "choices", None) and len(chunk.choices) > 0:
                first_choice = chunk.choices[0]
                index = getattr(first_choice, "index", 0) or 0
                finish_reason = getattr(first_choice, "finish_reason", None)
        except Exception:
            pass

        # Extract tool call info if present in delta
        tool_use: Optional[dict[str, Any]] = None
        try:
            if getattr(chunk, "choices", None) and len(chunk.choices) > 0:
                delta = getattr(chunk.choices[0], "delta", None)
                tool_calls = getattr(delta, "tool_calls", None)
                if tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0:
                    first = tool_calls[0]
                    if hasattr(first, "model_dump"):
                        tool_use = first.model_dump()
                    elif isinstance(first, dict):
                        tool_use = first
        except Exception:
            # Best-effort; tool calls are optional in generic chunk
            tool_use = None

        # Extract usage if present
        usage: Optional[dict[str, Any]] = None
        try:
            if getattr(chunk, "usage", None) is not None:
                usage_obj = chunk.usage
                if hasattr(usage_obj, "model_dump"):
                    usage = usage_obj.model_dump()
                elif isinstance(usage_obj, dict):
                    usage = usage_obj
        except Exception:
            usage = None

        provider_specific_fields: Optional[dict[str, Any]] = None
        try:
            model_name = getattr(chunk, "model", None)
            if model_name:
                provider_specific_fields = {"model": model_name}
        except Exception:
            provider_specific_fields = None

        return {
            "text": text,
            "tool_use": tool_use,
            "is_finished": bool(finish_reason),
            "finish_reason": finish_reason or "",
            "usage": usage,
            "index": index,
            "provider_specific_fields": provider_specific_fields,
        }
    def _map_model(self, model: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        # TODO "Unconvolute" this function - it should be straightforward
        params: dict[str, Any] = {}
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
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> Any:
        mapped = self._map_model(model, kwargs)
        return litellm.completion(messages=messages, **mapped)

    async def acompletion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> Any:
        mapped = self._map_model(model, kwargs)
        return await litellm.acompletion(messages=messages, **mapped)

    def streaming(
        self,
        model: str,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> Generator[litellm.GenericStreamingChunk, None, None]:
        mapped = self._map_model(model, kwargs)
        mapped["stream"] = True
        response = litellm.completion(messages=messages, **mapped)
        for chunk in response:
            # Convert ModelResponseStream -> GenericStreamingChunk
            yield self._to_generic_streaming_chunk(chunk)

    async def astreaming(
        self,
        model: str,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> AsyncGenerator[litellm.GenericStreamingChunk, None]:
        print("WHATAAAAAP")
        print("WHATAAAAAP")
        print("WHATAAAAAP")
        print("WHATAAAAAP")
        print("WHATAAAAAP")
        print("WHATAAAAAP")
        mapped = self._map_model(model, kwargs)
        from pprint import pprint, pformat
        # pprint(mapped, width=160)
        print("WHATAAAAAP", mapped["model"])
        mapped.pop("acompletion", None)
        mapped.pop("model_response", None)
        mapped["stream"] = True
        try:
            response = await litellm.acompletion(messages=messages, **mapped)
        except Exception as e:
            with open("mapped.pformat", "w") as f:
                f.write(pformat(mapped, width=180))
            raise ValueError() from e
            raise e
        print("WHATAAAAAP2")
        for _ in ():
            yield {}
        # async for chunk in response:
        #     # Convert ModelResponseStream -> GenericStreamingChunk
        #     yield self._to_generic_streaming_chunk(chunk)
        print("WHATAAAAAP3")


custom_llm_router = CustomLLMRouter()
