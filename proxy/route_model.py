import re
from typing import Any

from proxy.config import REMAP_CLAUDE_HAIKU_TO, REMAP_CLAUDE_OPUS_TO, REMAP_CLAUDE_SONNET_TO


def route_model(requested_model: str) -> tuple[str, dict[str, Any]]:
    requested_model = requested_model.strip()

    if requested_model.startswith("claude-"):
        if REMAP_CLAUDE_HAIKU_TO and "haiku" in requested_model:
            requested_model = REMAP_CLAUDE_HAIKU_TO
        elif REMAP_CLAUDE_OPUS_TO and "opus" in requested_model:
            requested_model = REMAP_CLAUDE_OPUS_TO
        elif REMAP_CLAUDE_SONNET_TO:
            requested_model = REMAP_CLAUDE_SONNET_TO

    # Prepend the provider name and resolve to a concrete GPT-5 model configuration if it is one of our GPT-5 aliases
    final_model, extra_params = resolve_model_for_provider(requested_model)

    log_message = f"\033[1m\033[32m{requested_model}\033[0m -> \033[1m\033[36m{final_model}\033[0m"
    if extra_params:
        log_message += f" [\033[1m\033[33m{repr_extra_params(extra_params)}\033[0m]"
    # TODO Make it possible to disable this print ? (Turn it into a log record ?)
    print(log_message)

    return final_model, extra_params


def resolve_model_for_provider(requested_model: str) -> tuple[str, dict[str, Any]]:
    requested_model = requested_model.strip()

    extra_params = {}
    # Check if it is one of our GPT-5 model aliases with a reasoning effort specified in the model name
    reasoning_effort_alias_match = re.fullmatch(
        r"(?P<name>.+)-reason(ing)?(-effort)?-(?P<effort>\w+)",
        requested_model,
    )
    if reasoning_effort_alias_match:
        requested_model = reasoning_effort_alias_match.group("name")
        extra_params = {"reasoning_effort": reasoning_effort_alias_match.group("effort")}

    if requested_model.startswith("claude-"):
        final_model = f"anthropic/{requested_model}"
    else:
        # Default to OpenAI if it is not a Claude model
        final_model = f"openai/{requested_model}"

    return final_model, extra_params


def repr_extra_params(extra_params: dict[str, Any]) -> str:
    return ", ".join([f"{k}: {v}" for k, v in extra_params.items()])
