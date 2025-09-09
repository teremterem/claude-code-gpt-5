import re
from typing import Any


def route_model(requested_model: str) -> tuple[str, dict[str, Any]]:
    # TODO TODO TODO
    return resolve_gpt_5_alias(requested_model)


def resolve_gpt_5_alias(requested_model: str) -> tuple[str, dict[str, Any]]:
    # TODO TODO TODO
    """
    Map a friendly model alias to a provider model and extra params.

    Supported patterns:
    - gpt-5(-mini|-nano)?-reason-(minimal|low|medium|high)
      -> maps to openai/gpt-5[(-mini|-nano)] with reasoning_effort
    - claude-* -> maps directly to anthropic/claude-*

    Returns a tuple of (provider_model, extra_params)
    """
    requested_model = requested_model.strip()

    # Claude passthrough (kept for Claude Code fast model usage)
    if requested_model.startswith("claude-"):
        final_model = f"anthropic/{requested_model}"
        # TODO Make it possible to disable this print ? (turn it into a log record ?)
        print(f"\033[1m\033[32m{requested_model}\033[0m -> \033[1m\033[36m{final_model}\033[0m")
        return final_model, {}

    # GPT-5 family with reasoning effort
    m = re.fullmatch(
        r"gpt-5(?P<variant>-(mini|nano))?-reason-(?P<effort>minimal|low|medium|high)",
        requested_model,
    )
    if m:
        variant = m.group("variant") or ""
        effort = m.group("effort")
        final_model = f"openai/gpt-5{variant or ''}"
        # TODO Make it possible to disable this print ? (turn it into a log record ?)
        print(
            f"\033[1m\033[32m{requested_model}\033[0m -> \033[1m\033[36m{final_model}\033[0m "
            f"[\033[1m\033[33mreasoning_effort: {effort}\033[0m]"
        )
        return final_model, {"reasoning_effort": effort}

    raise ValueError(
        f"Unknown model alias '{requested_model}'. Supported patterns: "
        "'gpt-5(-mini|-nano)?-reason-(minimal|low|medium|high)' or 'claude-*'."
    )
