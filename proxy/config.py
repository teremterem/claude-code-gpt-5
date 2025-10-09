import os
from pathlib import Path

import litellm

from proxy.utils import env_var_to_bool


# We don't need to do `dotenv.load_dotenv()` - litellm does this for us upon
# import.
# TODO This would break if LITELLM_MODE env var is set to a value other than
#  DEV (although, when it is not set, it is DEV by default). What would be the
#  best way to adapt to the approach taken by litellm ?

# NOTE: If any of the three env vars below are set to an empty string, the
# defaults will NOT be used. The defaults are used only when these env vars are
# not set at all. This is intentional - setting them to empty strings should
# result in no remapping.
REMAP_CLAUDE_HAIKU_TO = os.getenv("REMAP_CLAUDE_HAIKU_TO", "gpt-5-mini-reason-minimal")
REMAP_CLAUDE_SONNET_TO = os.getenv("REMAP_CLAUDE_SONNET_TO", "gpt-5-reason-medium")
REMAP_CLAUDE_OPUS_TO = os.getenv("REMAP_CLAUDE_OPUS_TO", "gpt-5-reason-high")

ENFORCE_ONE_TOOL_CALL_PER_RESPONSE = env_var_to_bool(os.getenv("ENFORCE_ONE_TOOL_CALL_PER_RESPONSE"), "true")

ALWAYS_USE_RESPONSES_API = env_var_to_bool(os.getenv("ALWAYS_USE_RESPONSES_API"), "false")

WRITE_TRACES_TO_FILES = env_var_to_bool(os.getenv("WRITE_TRACES_TO_FILES"), "false")
TRACES_DIR = Path(__file__).parent.parent / ".traces"

ANTHROPIC = "anthropic"
OPENAI = "openai"

if os.getenv("LANGFUSE_SECRET_KEY") or os.getenv("LANGFUSE_PUBLIC_KEY") or os.getenv("LANGFUSE_HOST"):
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
