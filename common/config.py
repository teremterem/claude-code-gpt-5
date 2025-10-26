import os
from pathlib import Path

import litellm

# We don't need to do `dotenv.load_dotenv()` - litellm does this for us upon
# import.
# TODO This would break if LITELLM_MODE env var is set to a value other than
#  DEV (although, when it is not set, it is DEV by default). What would be the
#  best way to adapt to the approach taken by litellm ?

from common.utils import env_var_to_bool


WRITE_TRACES_TO_FILES = env_var_to_bool(os.getenv("WRITE_TRACES_TO_FILES"), "false")
TRACES_DIR = Path(__file__).parent.parent / ".traces"

if os.getenv("LANGFUSE_SECRET_KEY") or os.getenv("LANGFUSE_PUBLIC_KEY") or os.getenv("LANGFUSE_HOST"):
    try:
        import langfuse  # pylint: disable=unused-import
    except ImportError:
        print(
            "\033[1;31mLangfuse is not installed. Please install it with either `uv sync --extra langfuse` or "
            "`uv sync --all-extras`.\033[0m"
        )
    else:
        # TODO Replace with a logger ?
        print("\033[1;34mEnabling Langfuse logging...\033[0m")
        litellm.success_callback = ["langfuse"]
        litellm.failure_callback = ["langfuse"]
