# pylint: disable=too-many-branches,too-many-locals,too-many-statements,too-many-return-statements
# pylint: disable=too-many-nested-blocks
"""
NOTE: The utilities in this module were mostly vibe-coded without review.
"""
import os
from datetime import UTC, datetime
from typing import Optional, Union

from litellm import GenericStreamingChunk, ModelResponseStream


class ProxyError(RuntimeError):
    def __init__(self, error: Union[BaseException, str], highlight: Optional[bool] = None):

        final_highlight: bool
        if highlight is None:
            # No value provided, read from env var (default 'True')
            env_val = os.environ.get("PROXY_ERROR_HIGHLIGHT", "True")
            final_highlight = env_val.lower() not in ("false", "0", "no")
        else:
            # Value was provided, use it
            final_highlight = highlight

        if final_highlight:
            # Highlight error messages in red, so the actual problems are
            # easier to spot in long tracebacks
            super().__init__(f"\033[1;31m{error}\033[0m")
        else:
            super().__init__(error)


def env_var_to_bool(value: Optional[str], default: str = "false") -> bool:
    """
    Convert environment variable string to boolean.

    Args:
        value: The environment variable value (or None if not set)
        default: Default value to use if value is None

    Returns:
        True if the value (or default) is a truthy string, False otherwise
    """
    return (value or default).lower() in ("true", "1", "on", "yes", "y")


def generate_timestamp_utc() -> str:
    """
    Generate timestamp in format YYYYmmdd_HHMMSS_fff_fff in UTC.

    An example of how these timestamps are used later:

    `.traces/20251005_140642_180_342_RESPONSE_STREAM.md`
    """
    now = datetime.now(UTC)

    str_repr = now.strftime("%Y%m%d_%H%M%S_%f")
    # Let's separate the milliseconds from the microseconds with an underscore
    # to make it more readable
    return f"{str_repr[:-3]}_{str_repr[-3:]}"


def model_response_stream_to_generic_streaming_chunk(chunk: ModelResponseStream) -> GenericStreamingChunk:
    """
    Convert a LiteLLM ModelResponseStream chunk into a GenericStreamingChunk.

    Args:
        chunk: The LiteLLM ModelResponseStream chunk to convert.

    Returns:
        The converted GenericStreamingChunk.
    """
    return GenericStreamingChunk(
        text="",
        tool_use=None,
        is_finished=False,
        finish_reason="",
        usage=None,
        index=0,
        provider_specific_fields=None,
    )
