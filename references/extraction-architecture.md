# Optional Extraction Adapters

This is an adapter guide, not a requirement that Codex reproduce the original platform. Select one adapter based on tools actually available in the current session.

## Adapter Order

1. **Supplied transcript/subtitles**: highest reliability and lowest permission cost. Preserve the supplied text and filename/source label.
2. **Codex-native media understanding**: use the audio/video understanding capability already exposed by the current Codex session for an attached file, supported workspace media, or authorized connector. No user installation is required.
3. **Configured transcript tool**: use an available `transcribe_media`/equivalent tool only after source-specific consent. It should accept a temporary media reference or file, return structured transcript evidence, and delete the media according to `transcript-tool-contract.md`.
4. **Authorized browser/session**: use only when the user has access to the source. Capture visible captions or an authorized media reference; do not bypass access controls. A browser is an acquisition surface, not an ASR engine.
5. **No local fallback by default**: do not install or invoke a local ASR runtime, media-processing stack, Python ASR package, or downloaded model weights merely to satisfy this skill. A user-configured local engine may be used only when the user explicitly requests that mode.

If the adapter cannot yield actual speech/text, status is `blocked`. A URL, title, description, thumbnail, or platform metadata is not sufficient evidence.

## Common Contract

Every adapter should return:

```json
{
  "source_url": "optional canonical URL",
  "source_label": "human-readable label",
  "text": "actual supplied or transcribed text",
  "timestamps": [],
  "provider": "codex_native | supplied | subtitle | remote_transcript | ASR | OCR+ASR | other",
  "confidence": "high | medium | low",
  "media_retention": "not_received | temporary_deleted | user_retained",
  "status": "ready | needs_review | blocked",
  "error_code": "AUTHORIZATION_UNCLEAR | NO_ADAPTER | NO_TRANSCRIPT_EVIDENCE | null"
}
```

For `blocked`, set `text` to `unavailable`; never insert title, hashtags, metadata, a placeholder sentence, or a guessed reconstruction just to fill the contract.

## Resource Limits and Cleanup

When implementing an adapter, bound request size, media/audio size, processing time, and concurrent work. Validate content type and redirects when retrieving media. Put cleanup in a `finally`/defer path and verify that the temporary media is gone before reporting success.

## Transcript Quality

Keep raw ASR/subtitle/OCR signals separate. Derive a reviewed transcript with explicit confidence and correction records. A minimum character count can reject empty responses, but length alone does not prove fidelity; inspect coherence, language, speaker boundaries, and ASR/OCR disagreement.
