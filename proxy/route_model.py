import re
from typing import Any

from proxy.config import (
    RECOMMEND_SETTING_REMAPS,
    REMAP_CLAUDE_HAIKU_TO,
    REMAP_CLAUDE_OPUS_TO,
    REMAP_CLAUDE_SONNET_TO,
    recommend_setting_remaps,
)


def route_model(requested_model: str) -> tuple[str, dict[str, Any]]:
    final_model = requested_model.strip()

    if final_model.startswith("claude-"):
        # If the model name contains "haiku", "opus", or "sonnet", remap it to the appropriate model (provided the
        # remap is configured)
        if "haiku" in final_model:
            if REMAP_CLAUDE_HAIKU_TO:
                final_model = REMAP_CLAUDE_HAIKU_TO
        elif "opus" in final_model:
            if REMAP_CLAUDE_OPUS_TO:
                final_model = REMAP_CLAUDE_OPUS_TO
        elif REMAP_CLAUDE_SONNET_TO:
            # Here we assume the requested model is a Sonnet model (but also fallback to this remap in case it is some
            # new, unknown model by Anthropic)
            final_model = REMAP_CLAUDE_SONNET_TO

    # Prepend the provider name (and resolve to a real GPT-5 model name and configuration if it is one of our GPT-5
    # aliases with a reasoning effort specified in the alias)
    final_model, extra_params = resolve_model_for_provider(final_model)

    log_message = f"\033[1m\033[32m{requested_model}\033[0m -> \033[1m\033[36m{final_model}\033[0m"
    if extra_params:
        log_message += f" [\033[1m\033[33m{repr_extra_params(extra_params)}\033[0m]"
    # TODO Make it possible to disable this print ? (Turn it into a log record ?)
    print(log_message)

    if RECOMMEND_SETTING_REMAPS:
        recommend_setting_remaps()

    return final_model, extra_params


def resolve_model_for_provider(requested_model: str) -> tuple[str, dict[str, Any]]:
    final_model = requested_model.strip()

    extra_params = {}
    # Check if it is one of our GPT-5 model aliases with a reasoning effort specified in the model name
    reasoning_effort_alias_match = re.fullmatch(r"(?P<name>.+)-reason(ing)?(-effort)?-(?P<effort>\w+)", final_model)
    if reasoning_effort_alias_match:
        final_model = reasoning_effort_alias_match.group("name")
        extra_params = {"reasoning_effort": reasoning_effort_alias_match.group("effort")}

    # TODO If the model already contains a provider name, don't change it (make sure that the GPT-5 aliases are still
    #  resolved properly, though; also, invert the request correction logic from `_adapt_for_openai_in_place` to
    #  `_adapt_for_non_anthropic`)
    # TODO Autocorrect `gpt5` to `gpt-5` for convience
    if final_model.startswith("claude-"):
        final_model = f"anthropic/{final_model}"
    else:
        # Default to OpenAI if it is not a Claude model
        final_model = f"openai/{final_model}"

    return final_model, extra_params


def repr_extra_params(extra_params: dict[str, Any]) -> str:
    return ", ".join([f"{k}: {v}" for k, v in extra_params.items()])
