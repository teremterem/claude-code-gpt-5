import os

from common import config as common_config  # Makes sure .env is loaded  # pylint: disable=unused-import
from common.utils import env_var_to_bool


# NOTE: If any of the three env vars below are set to an empty string, the
# defaults will NOT be used. The defaults are used only when these env vars are
# not set at all. This is intentional - setting them to empty strings should
# result in no remapping.
REMAP_CLAUDE_HAIKU_TO = os.getenv("REMAP_CLAUDE_HAIKU_TO", "gpt-5-mini-reason-minimal")
REMAP_CLAUDE_SONNET_TO = os.getenv("REMAP_CLAUDE_SONNET_TO", "gpt-5-reason-medium")
REMAP_CLAUDE_OPUS_TO = os.getenv("REMAP_CLAUDE_OPUS_TO", "gpt-5-reason-high")

ENFORCE_ONE_TOOL_CALL_PER_RESPONSE = env_var_to_bool(os.getenv("ENFORCE_ONE_TOOL_CALL_PER_RESPONSE"), "true")

ALWAYS_USE_RESPONSES_API = env_var_to_bool(os.getenv("ALWAYS_USE_RESPONSES_API"), "false")

ANTHROPIC = "anthropic"
OPENAI = "openai"
