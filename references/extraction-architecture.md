# Optional Extraction Adapters

This is an adapter guide, not a requirement that Codex reproduce the original platform. Select one adapter based on tools actually available in the current session.

## Adapter Order

1. **Supplied transcript/subtitles**: highest reliability and lowest permission cost. Preserve the supplied text and filename/source label.
2. **Codex-native media understanding**: use the audio/video understanding capability already exposed by the current Codex session for an attached file, supported workspace media, or authorized connector. No user installation is required.
3. **Public Douyin URL**: run `scripts/download_public_douyin.py <url> --output <temporary>.mp4` only to acquire authorized temporary media. It uses a fresh anonymous Chromium profile, loads the public page, requests the matching `aweme_detail` response inside that page, extracts HTTPS `play_addr`/`download_addr`/bit-rate URLs, validates the video ID and byte ranges, and downloads with the page URL as `Referer`. It does not read the user's browser profile or require a login Cookie. A downloaded file must still be handed to a Codex-native media capability; if that handoff is unavailable, stop as `blocked` rather than requiring BaoCut or a local model.
4. **Authorized browser/session**: use only when the user has access and the native capability or bundled public adapter is unavailable. Capture visible captions or an authorized media reference; do not bypass access controls.
5. **External ASR**: use only when the user explicitly supplies or approves an already configured service. Do not install packages, download model weights, or silently send media to a third party.

If the adapter cannot yield actual speech/text, status is `blocked`. A URL, title, description, thumbnail, or platform metadata is not sufficient evidence.

## Common Contract

Every adapter should return:

```json
{
  "source_url": "optional canonical URL",
  "source_label": "human-readable label",
  "text": "actual supplied or transcribed text",
  "timestamps": [],
  "provider": "codex_native | supplied | subtitle | ASR | OCR+ASR | other",
  "confidence": "high | medium | low",
  "media_retention": "not_received | temporary_deleted | user_retained",
  "status": "ready | needs_review | blocked",
  "error_code": null
}
```

The original Still Settling implementation provides three optional examples:

- A loopback connector that validates Origin/host, tries anonymous `yt-dlp` before local browser profiles, runs FFmpeg and an isolated ASR worker, and cleans a `TemporaryDirectory`.
- A Tauri path that resolves authorized browser media, validates HTTPS/range responses and size, then falls back to `yt-dlp`.
- A server task path with a single worker, persisted progress, external `audio/transcriptions`, and cleanup. This path is deliberately not assumed by Codex and may be disabled in production.

## Resource Limits and Cleanup

When implementing an adapter, bound request size, media/audio size, download/FFmpeg/transcription time, and concurrent work. Validate content type and ranged responses when downloading. Use private permissions for temporary cookie jars. Put cleanup in a `finally`/defer path and verify that the directory is gone before reporting success.

## Transcript Quality

Keep raw ASR/subtitle/OCR signals separate. Derive a reviewed transcript with explicit confidence and correction records. A minimum character count can reject empty responses, but length alone does not prove fidelity; inspect coherence, language, speaker boundaries, and ASR/OCR disagreement.
