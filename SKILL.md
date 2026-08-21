---
name: video-transcript
description: Extract and verify a real video manuscript using supplied text, subtitles, Codex media understanding, or an approved OpenAI transcription bridge, then return a complete naturally paragraphed manuscript. Do not require local models, vendor software, or platform-access bypass.
metadata:
  short-description: Extract and verify authorized video manuscripts
---

# Video Manuscript Extraction and Verification

This skill has one narrow job: obtain the actual spoken/visible manuscript from a source the user asked Codex to process, then verify and correct it without inventing missing content. It orchestrates available subtitle/media/transcript capabilities; it is not an ASR engine and never installs one.

## Required Output

Return a concise report with:

1. **Source**: the user-provided source, authorization basis, and acquisition method.
2. **Raw manuscript**: the untouched ASR/subtitle text, kept separate from all edits.
3. **Reviewed manuscript**: the complete transcript after evidence-bounded semantic/typo correction and natural paragraphing. Preserve the original speaking order; do not summarize, shorten, add ideas, or turn it into a new article.
4. **Verification**: what was checked against audio, subtitles, visible captions/OCR, timestamps, or user corrections.
5. **Corrections**: each substantive change as `original`, `corrected`, `reason`, `evidence`, `confidence`, and `decision`; formatting-only paragraph and punctuation changes may be grouped separately.
6. **Status**: `verified`, `needs_review`, or `blocked`, with the next safe action.

Do not add structure analysis, hook extraction, writing templates, Skill generation, model scoring, repository changes, or publishing unless the user starts a separate request.

## Workflow

1. **Confirm source and processing authorization.** Accept a user-provided URL, local video/audio, subtitle file, or transcript. The user's explicit request to process a supplied source is sufficient authorization for this extraction attempt; do not claim that it grants publishing or redistribution rights. Record the source and that basis. Do not bypass login, anti-bot controls, paywalls, regional restrictions, or copyright controls. A title, description, thumbnail, search result, or share text without accessible video/text is not a manuscript.
2. **Run capability preflight before retrieval.** Identify which of these are actually callable in the current session: source-tied subtitles, Codex-native media understanding, or an already configured `transcribe_media`/equivalent tool backed by an approved provider. Do not download a video until a downstream consumer is available. If none is callable, return a resumable `blocked` result with `NO_TRANSCRIPT_TOOL` and the `next_action` contract below. When a provider is being configured, use the official OpenAI bridge design in [references/openai-transcription-bridge.md](references/openai-transcription-bridge.md); do not invent a direct Codex audio endpoint.
3. **Choose the adapter in this order.** Use user-supplied transcript or source-tied subtitles first. Next use a Codex-native audio/video capability for an attached file, supported workspace media, or authorized connector. Then use an available transcript tool only when it is configured and the user has approved sending this source to it; read [references/transcript-tool-contract.md](references/transcript-tool-contract.md) before calling one. The recommended remote implementation is an MCP bridge that fetches/normalizes authorized media and calls the official OpenAI file transcription API; the API key stays server-side. For a public platform URL, use an authorized connector or browser capability only to obtain source-tied subtitles or a temporary media reference. A downloader bundled with this skill is intentionally not provided: it would impose runtime dependencies and cannot guarantee platform access. Downloading media alone is never transcription. If no adapter yields actual speech/text, report `blocked`; do not reconstruct from title, description, hashtags, OCR alone, or share text.
4. **Handle temporary media only inside the selected adapter.** Keep downloaded video, extracted audio, OCR frames, cookies, and intermediate files outside final output. Require bounded size/time and cleanup on success and failure. Never put API keys, cookies, browser profiles, or raw media in a repository or skill artifact.
5. **Extract the raw manuscript.** Preserve the provider and method (`codex_native`, `supplied`, `subtitle`, `remote_transcript`, `ASR`, `OCR+ASR`, or other), timestamps when available, language, confidence, and media retention. Never overwrite the raw transcript with an AI rewrite.
6. **Run a second-pass review.** Read the full raw transcript in context, then compare suspicious spans with the strongest available evidence. Fix clear ASR semantic errors, homophones, names, numbers, negations, and typos when the audio/subtitle/OCR or immediate sentence context supports the correction. Context may disambiguate a recognition error, but it may not supply a new fact or reconstruct missing speech.
7. **Create the reviewed manuscript.** Keep every supported spoken idea and the original sequence. Normalize obvious punctuation, remove ASR-only clutter, and split into natural paragraphs by topic, story beat, or speaker turn. Do not polish the author's style, change word choice merely for elegance, merge distinct claims, or silently omit repetition that carries meaning.
8. **Record corrections and uncertainty.** Log every non-trivial lexical or semantic change with its evidence and confidence. Leave unresolved spans unchanged (or mark them inline) and list them for the user; never present guessed text as verified.
9. **Finish at the evidence boundary.** `verified` means the reviewed transcript is sufficiently supported by the available source evidence. `needs_review` means a human must resolve listed uncertainties. `blocked` means the actual media/text could not be obtained or no usable adapter is available. In a blocked result, label both manuscript fields `unavailable`, provide one of `NO_TRANSCRIPT_TOOL`, `NO_ADAPTER`, `NO_TRANSCRIPT_EVIDENCE`, or `MEDIA_UNREADABLE`, preserve the canonical source, and return a concrete `next_action`:

   ```json
   {
     "type": "provide_evidence | approve_configured_tool | retry_source",
     "prompt": "one sentence the user can act on",
     "accepted_inputs": [".srt", ".vtt", ".txt", "local audio/video", "configured transcript tool"]
   }
   ```

   A blocked result is resumable: when the user supplies the requested evidence or approves the configured tool, continue from the last completed stage instead of restarting source discovery.

## Quality Rules

- A minimum length check rejects empty/truncated results but does not prove accuracy; assess coherence and evidence coverage.
- Keep raw ASR, subtitles, OCR, normalized display text, and proposed corrections as separate layers.
- Always return both raw and reviewed text when a second-pass review is requested; the reviewed file must be complete and naturally paragraphed, not an excerpt or summary.
- Treat paragraphing and harmless punctuation normalization as presentation changes, but keep lexical/semantic corrections auditable.
- If multiple signals disagree, report the disagreement instead of silently selecting one.
- If media is unavailable after a reasonable authorized attempt, ask for a local file, subtitle file, or transcript. Do not fall back to title/description reconstruction.
- Redact credentials, cookies, authorization headers, proxy credentials, URLs in logs where unnecessary, and absolute sensitive paths from diagnostics.

## Reference

Read [references/extraction-architecture.md](references/extraction-architecture.md) for adapter selection, temporary media handling, and the common extraction result contract.

Read [references/execution-state-machine.md](references/execution-state-machine.md) when routing a URL or media source through more than one adapter, or when a prior attempt returned `blocked`.

Read [references/transcript-verification.md](references/transcript-verification.md) for the verification checklist, correction schema, and status criteria.

Read [references/transcript-tool-contract.md](references/transcript-tool-contract.md) only when a transcript MCP/plugin tool is available for the current request.

Read [references/openai-transcription-bridge.md](references/openai-transcription-bridge.md) when configuring or diagnosing the recommended official remote provider.
