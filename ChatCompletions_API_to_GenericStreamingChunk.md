## ChatCompletions API → GenericStreamingChunk Mapping Guide

### How to use this guide
- Review the field-by-field mapping rules below when converting `litellm.ModelResponseStream` payloads into `litellm.GenericStreamingChunk`.
- Each rule cites at least one concrete example chunk from the attached traces so you can quickly reopen the original stream capture if you need to double-check the raw data.
- Preserve nulls/omitted keys as-is unless a rule explicitly calls for a default.

### Top-level chunk fields
- `id` → copy verbatim to `GenericStreamingChunk.id`. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `created` → copy to `GenericStreamingChunk.created` without transformation. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `model` → populate `GenericStreamingChunk.model` with the same string. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `object` → pass through to `GenericStreamingChunk.object`. (The examples use `"chat.completion.chunk"`; keep whatever value arrives.) Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `system_fingerprint` → copy directly to `GenericStreamingChunk.system_fingerprint`, preserving `null`. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `provider_specific_fields` (top-level) → forward untouched into the corresponding `GenericStreamingChunk` field. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `citations` → expose on `GenericStreamingChunk.citations`; keep nulls if present. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `usage` → when the `ModelResponseStream` chunk includes a `usage` block, attach it to `GenericStreamingChunk.usage` without altering the numeric counters or nested detail dictionaries. Reference: `Response Chunk #106` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.

### Choices array
- Always emit a `GenericStreamingChunk.choices` list whose length matches the incoming `choices` array. Preserve the order so indexes remain aligned with the upstream stream. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- For each element, set `GenericStreamingChoice.index` equal to the incoming `index`. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- Forward the `finish_reason` (including `null`) to `GenericStreamingChoice.finish_reason`. Reference: `Response Chunk #105` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- Accept non-`stop` finish signals (e.g., `"tool_calls"`) and propagate them unchanged so downstream logic can detect tool switchovers. Reference: `Response Chunk #63` in `ChatCompletions_API_streaming_examples/20251108_222758_22270_RESPONSE_STREAM.md`.
- Map any `logprobs` field—currently `null` in the traces—to `GenericStreamingChoice.logprobs` verbatim. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.

### Delta payload
- Copy the entire `delta` object into a fresh `GenericStreamingDelta` structure, mirroring the keys present in the stream.
- `delta.content` → assign to `GenericStreamingDelta.content`, concatenating downstream as needed. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `delta.role` → populate `GenericStreamingDelta.role`, noting that later chunks often send `null`. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- Subsequent deltas regularly omit the role (`null`); mirror the streamed value inside each chunk instead of injecting the previously observed role. Reference: `Response Chunk #0` vs `Response Chunk #1` in `ChatCompletions_API_streaming_examples/20251109_125816_01437_RESPONSE_STREAM.md`.
- `delta.provider_specific_fields` → carry forward unchanged onto the delta. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `delta.function_call` → forward as-is (the current capture shows `null`, but preserve the object structure if present). Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `delta.tool_calls` → preserve the list (even when `null`) for later combination with tool streaming logic. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- `delta.audio` → forward the value (currently `null`) to the delta’s audio slot so audio-capable providers remain compatible. Reference: `Response Chunk #0` in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.

#### Tool-call specific handling
- When `delta.tool_calls` is a list of call deltas, map each entry to a `GenericStreamingToolCallDelta` while keeping the existing ordering so partially streamed arguments can be concatenated later.
- `tool_call.id` → copy the identifier (may be `null` in subsequent fragments). Reference: `Response Chunk #8` in `ChatCompletions_API_streaming_examples/20251108_222824_10592_RESPONSE_STREAM.md`.
- `tool_call.type` → transfer directly (the capture shows `"function"`; preserve any other provider values). Reference: `Response Chunk #8` in `ChatCompletions_API_streaming_examples/20251108_222824_10592_RESPONSE_STREAM.md`.
- `tool_call.index` → mirror the numeric slot so batched tool deltas stay aligned. Reference: `Response Chunk #8` in `ChatCompletions_API_streaming_examples/20251108_222824_10592_RESPONSE_STREAM.md`.
- `tool_call.function.name` → set on the target tool-call structure; allow `null` for intermediate frames. Reference: `Response Chunk #8` in `ChatCompletions_API_streaming_examples/20251108_222824_10592_RESPONSE_STREAM.md`.
- `tool_call.function.arguments` → append the streamed arguments string exactly as received (they often arrive piecemeal across chunks). Reference: `Response Chunk #9` in `ChatCompletions_API_streaming_examples/20251108_222824_10592_RESPONSE_STREAM.md`.
- When multiple tool calls are active simultaneously, use each entry’s `index` to merge follow-up fragments into the correct call record; maintain per-index buffers in your eventual implementation. Reference: `Response Chunk #16` in `ChatCompletions_API_streaming_examples/20251108_222816_94922_RESPONSE_STREAM.md`.

### Usage payload details
- `usage` only appears on the closing chunks; keep `GenericStreamingChunk.usage` unset for intermediate emissions and populate it once the payload arrives. Reference: `Response Chunk #28` in `ChatCompletions_API_streaming_examples/20251109_125816_01437_RESPONSE_STREAM.md`.
- Copy the numeric counters (`prompt_tokens`, `completion_tokens`, `total_tokens`) directly; they already reflect request-level totals. Reference: `Response Chunk #35` in `ChatCompletions_API_streaming_examples/20251109_125816_01973_RESPONSE_STREAM.md`.
- Preserve every nested `*_tokens_details` block and cache counter exactly as provided (including zeros and `null` values) so downstream consumers retain provider-specific accounting. Reference: the `usage` block in `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md`.
- Cached-token metrics can shift between the `cache_creation_*` and `cache_read_*` counters across calls; never normalize these values. Reference: `Response Chunk #41` in `ChatCompletions_API_streaming_examples/20251109_131644_45210_RESPONSE_STREAM.md` (`cache_creation_tokens` populated) versus `Response Chunk #19` in `ChatCompletions_API_streaming_examples/20251109_131704_44443_RESPONSE_STREAM.md` (`cache_read_input_tokens` populated).
