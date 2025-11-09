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

### File coverage log
- Processed `ChatCompletions_API_streaming_examples/20251108_222915_51732_RESPONSE_STREAM.md` – introduced the baseline field set (top-level metadata, single `choices` array, simple `delta`, and optional `usage` in the final chunk).
- Processed `ChatCompletions_API_streaming_examples/20251108_222824_10592_RESPONSE_STREAM.md` – confirmed streaming tool-call payloads with evolving `id`, `function`, and `arguments` fragments; no new top-level keys.
- Processed `ChatCompletions_API_streaming_examples/20251108_222824_11383_RESPONSE_STREAM.md` – no additional fields beyond the baseline; reinforced `usage` block handling for short completions.
- Processed `ChatCompletions_API_streaming_examples/20251108_222824_05136_RESPONSE_STREAM.md` – reaffirmed markdown-to-JSON content streaming; all fields already covered.
- Processed `ChatCompletions_API_streaming_examples/20251108_222816_94773_RESPONSE_STREAM.md` – same `<is_displaying_contents>` pattern as other haiku runs; no new schema elements.
- Processed `ChatCompletions_API_streaming_examples/20251108_222816_94922_RESPONSE_STREAM.md` – highlighted multi-tool-call streaming where argument strings are interleaved per `index`.
- Processed `ChatCompletions_API_streaming_examples/20251108_222824_05035_RESPONSE_STREAM.md` – another minimal JSON snippet stream; schema unchanged.
- Processed `ChatCompletions_API_streaming_examples/20251108_222816_51724_RESPONSE_STREAM.md` – short plaintext metadata response, reusing the baseline keys.
- Processed `ChatCompletions_API_streaming_examples/20251108_222816_51834_RESPONSE_STREAM.md` – Dockerfile-oriented metadata stream; fields already accounted for.
- Processed `ChatCompletions_API_streaming_examples/20251108_222808_69776_RESPONSE_STREAM.md` – another JSON metadata emission with identical structure.
- Processed `ChatCompletions_API_streaming_examples/20251108_222808_70283_RESPONSE_STREAM.md` – long tool-planning trace with sustained tool-call deltas; schema matches earlier sonnet traces.
- Processed `ChatCompletions_API_streaming_examples/20251108_222808_69727_RESPONSE_STREAM.md` – same JSON metadata pattern, no new keys.
- Processed `ChatCompletions_API_streaming_examples/20251108_222808_62579_RESPONSE_STREAM.md` – mirrored the short JSON listing format; no schema change.
- Processed `ChatCompletions_API_streaming_examples/20251108_222808_65199_RESPONSE_STREAM.md` – equivalent JSON metadata streaming; nothing new schema-wise.
- Processed `ChatCompletions_API_streaming_examples/20251108_222803_66636_RESPONSE_STREAM.md` – extensive tool-planning conversation; tool-call schema matches prior sonnet traces.
- Processed `ChatCompletions_API_streaming_examples/20251108_222808_62419_RESPONSE_STREAM.md` – JSON metadata again with identical structure; no new mapping rules.
- Processed `ChatCompletions_API_streaming_examples/20251108_222803_57337_RESPONSE_STREAM.md` – YAML-focused metadata stream; same field usage as earlier haiku traces.
- Processed `ChatCompletions_API_streaming_examples/20251108_222803_62089_RESPONSE_STREAM.md` – `<is_displaying_contents>` guard responses; field layout unchanged.
- Processed `ChatCompletions_API_streaming_examples/20251108_222758_22270_RESPONSE_STREAM.md` – multi-tool run with `finish_reason: \"tool_calls\"`; confirms that non-`stop` finish reasons need to passthrough.
- Processed `ChatCompletions_API_streaming_examples/20251108_222803_57224_RESPONSE_STREAM.md` – short JSON metadata stream; schema remains consistent.
- Processed `ChatCompletions_API_streaming_examples/20251108_222758_08613_RESPONSE_STREAM.md` – markdown metadata emission; all fields already covered.
- Processed `ChatCompletions_API_streaming_examples/20251108_222758_12392_RESPONSE_STREAM.md` – another `<is_displaying_contents>` guard flow; schema unchanged.
- Processed `ChatCompletions_API_streaming_examples/20251108_222751_77786_RESPONSE_STREAM.md` – long multi-tool playout with argument streaming; confirmed tool-call structure remains consistent even with dozens of fragments.
- Processed `ChatCompletions_API_streaming_examples/20251108_222659_09073_RESPONSE_STREAM.md` – conversational opening stream without tool calls; no new fields introduced.
- Processed `ChatCompletions_API_streaming_examples/20251108_222751_77605_RESPONSE_STREAM.md` – short JSON metadata stream at smaller token counts; no schema updates.
- Processed `ChatCompletions_API_streaming_examples/20251108_222659_08898_RESPONSE_STREAM.md` – short completion culminating in a `usage` block; fields already covered by earlier entries.
- Processed `ChatCompletions_API_streaming_examples/20251108_222659_09025_RESPONSE_STREAM.md` – friendly introductory stream with no additional schema elements.
- Processed `ChatCompletions_API_streaming_examples/20251109_125816_01437_RESPONSE_STREAM.md` – long-form conversational stream with no tool calls; reaffirmed role-null deltas and end-of-stream `usage`.
- Processed `ChatCompletions_API_streaming_examples/20251109_125816_01973_RESPONSE_STREAM.md` – extended sonnet narration; confirmed `usage` payloads land only with the terminal chunk.
- Processed `ChatCompletions_API_streaming_examples/20251109_130011_19426_RESPONSE_STREAM.md` – concise JSON metadata emission; schema unchanged.
- Processed `ChatCompletions_API_streaming_examples/20251109_130011_19523_RESPONSE_STREAM.md` – short JSON snippet beginning mid-object; highlights that deltas can start with leading newlines.
- Processed `ChatCompletions_API_streaming_examples/20251109_130011_19635_RESPONSE_STREAM.md` – brief greeting without tool calls; no additional fields observed.
- Processed `ChatCompletions_API_streaming_examples/20251109_131623_12733_RESPONSE_STREAM.md` – long conversational run; reaffirmed plain-text streaming with terminal `usage`.
- Processed `ChatCompletions_API_streaming_examples/20251109_131644_45210_RESPONSE_STREAM.md` – extensive tool-call sequence with `cache_creation_tokens` populated.
- Processed `ChatCompletions_API_streaming_examples/20251109_131704_44443_RESPONSE_STREAM.md` – follow-up tool-call run with `cache_read_input_tokens` populated.
- Processed `ChatCompletions_API_streaming_examples/20251109_131623_12694_RESPONSE_STREAM.md`, `20251109_131623_12025_RESPONSE_STREAM.md`, `20251109_131658_64510_RESPONSE_STREAM.md`, `20251109_131704_44354_RESPONSE_STREAM.md`, `20251109_131644_44925_RESPONSE_STREAM.md`, `20251109_131644_45119_RESPONSE_STREAM.md`, `20251109_131653_76018_RESPONSE_STREAM.md`, and `20251109_131704_44443_RESPONSE_STREAM.md` – additional short responses and tool-call traces; no new schema fields beyond the cache metric variations already documented.
