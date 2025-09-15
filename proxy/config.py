import os

import litellm


# We don't need to do `dotenv.load_dotenv()` - litellm does this for us upon import


REMAP_CLAUDE_HAIKU_TO = os.getenv("REMAP_CLAUDE_HAIKU_TO")
REMAP_CLAUDE_SONNET_TO = os.getenv("REMAP_CLAUDE_SONNET_TO")
REMAP_CLAUDE_OPUS_TO = os.getenv("REMAP_CLAUDE_OPUS_TO")

RECOMMEND_SETTING_REMAPS = (
    "REMAP_CLAUDE_HAIKU_TO" not in os.environ
    or "REMAP_CLAUDE_SONNET_TO" not in os.environ
    or "REMAP_CLAUDE_OPUS_TO" not in os.environ
)


class ProxyError(RuntimeError):
    def __init__(self, error: BaseException | str):
        # Highlight error messages in red, so the actual problems are easier to spot in long tracebacks
        super().__init__(f"\033[1;31m{error}\033[0m")


if "OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE" in os.environ:
    raise ProxyError(
        "The OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE environment variable is no longer supported. "
        "Please use the ENFORCE_ONE_TOOL_CALL_PER_RESPONSE environment variable instead."
    )

ENFORCE_ONE_TOOL_CALL_PER_RESPONSE = (os.getenv("ENFORCE_ONE_TOOL_CALL_PER_RESPONSE") or "true").lower() in (
    "true",
    "1",
    "on",
    "yes",
    "y",
)

ANTHROPIC = "anthropic"
OPENAI = "openai"

if os.getenv("LANGFUSE_SECRET_KEY") or os.getenv("LANGFUSE_PUBLIC_KEY"):
    try:
        import langfuse  # pylint: disable=unused-import
    except ImportError:
        print(
            "\033[1;31mLangfuse is not installed. Please install it with either `uv sync --extra langfuse` or "
            "`uv sync --all-extras`.\033[0m"
        )
    else:
        print("\033[1;34mEnabling Langfuse logging...\033[0m")
        litellm.success_callback = ["langfuse"]
        litellm.failure_callback = ["langfuse"]


def recommend_setting_remaps():
    # TODO Turn this print into a log record ? Or, maybe, into a Python warning ?
    print(
        "\033[1;31mWARNING: It is recommended to set the REMAP_CLAUDE_HAIKU_TO, REMAP_CLAUDE_SONNET_TO, and "
        "REMAP_CLAUDE_OPUS_TO environment variables.\n"
        "Please refer to .env.template for recommended values (and an explanation).\033[0m"
    )


if RECOMMEND_SETTING_REMAPS:
    recommend_setting_remaps()
