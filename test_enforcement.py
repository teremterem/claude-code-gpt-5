#!/usr/bin/env python3
"""
Test script to verify GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE functionality.
"""
import os
from proxy.custom_llm_router import _should_enforce_single_tool_call, _modify_messages_for_gpt


def test_enforcement_enabled():
    """Test that enforcement is enabled by default."""
    # Test default (should be True)
    assert _should_enforce_single_tool_call() is True

    # Test explicit true values
    test_values = ["true", "True", "1", "yes", "YES", "on"]
    for value in test_values:
        os.environ["GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE"] = value
        assert _should_enforce_single_tool_call() is True, f"Failed for value: {value}"

    # Test false values
    false_values = ["false", "False", "0", "no", "off", ""]
    for value in false_values:
        os.environ["GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE"] = value
        assert _should_enforce_single_tool_call() is False, f"Failed for value: {value}"

    # Clean up
    if "GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE" in os.environ:
        del os.environ["GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE"]


def test_message_modification():
    """Test message modification for different models."""
    original_messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]

    # Test GPT model - should add instruction
    os.environ["GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE"] = "true"
    gpt_messages = _modify_messages_for_gpt(original_messages, "openai/gpt-5")
    assert len(gpt_messages) == 3
    assert gpt_messages[-1]["role"] == "system"
    assert "ONE tool at a time" in gpt_messages[-1]["content"]
    assert gpt_messages[0:2] == original_messages  # Original messages unchanged

    # Test Claude model - should not modify
    claude_messages = _modify_messages_for_gpt(original_messages, "anthropic/claude-3-5-sonnet")
    assert claude_messages == original_messages

    # Test with enforcement disabled - should not modify
    os.environ["GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE"] = "false"
    disabled_messages = _modify_messages_for_gpt(original_messages, "openai/gpt-5")
    assert disabled_messages == original_messages

    # Clean up
    if "GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE" in os.environ:
        del os.environ["GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE"]


def test_message_immutability():
    """Test that original messages are not modified."""
    original_messages = [{"role": "user", "content": "Test"}]
    original_copy = original_messages.copy()

    os.environ["GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE"] = "true"
    _modify_messages_for_gpt(original_messages, "openai/gpt-5")

    # Original should be unchanged
    assert original_messages == original_copy

    # Clean up
    if "GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE" in os.environ:
        del os.environ["GPT_ENFORCE_ONE_TOOL_CALL_PER_RESPONSE"]


if __name__ == "__main__":
    test_enforcement_enabled()
    test_message_modification()
    test_message_immutability()
    print("✅ All tests passed!")
