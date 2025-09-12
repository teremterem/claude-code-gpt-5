import os

import litellm


# We don't need to do `dotenv.load_dotenv()` - litellm does this for us upon import


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

REMAP_CLAUDE_HAIKU_TO = os.getenv("REMAP_CLAUDE_HAIKU_TO")
REMAP_CLAUDE_SONNET_TO = os.getenv("REMAP_CLAUDE_SONNET_TO")
REMAP_CLAUDE_OPUS_TO = os.getenv("REMAP_CLAUDE_OPUS_TO")

OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE = os.getenv("OPENAI_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE", "true").lower() in (
    "true",
    "1",
    "on",
    "yes",
    "y",
)
