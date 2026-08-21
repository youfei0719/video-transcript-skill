# Optional Extraction Adapters

This is an adapter guide, not a requirement that Codex reproduce the original platform. Select one adapter based on tools actually available in the current session.

## Adapter Order

1. **Supplied transcript/subtitles**: highest reliability and lowest permission cost. Preserve the supplied text and filename/source label.
2. **Local media**: use `ffmpeg` or an available transcription skill/tool. Process in a temporary directory and record the ASR provider, language, and confidence.
3. **Public Douyin URL**: run `scripts/download_public_douyin.py <url> --output <temporary>.mp4`. It uses a fresh anonymous Chromium profile, loads the public page, requests the matching `aweme_detail` response inside that page, extracts HTTPS `play_addr`/`download_addr`/bit-rate URLs, validates the video ID and byte ranges, and downloads with the page URL as `Referer`. It does not read the user's browser profile or require a login Cookie. It retries direct networking and system-proxy networking.
4. **Authorized browser/session**: use only when the user has access and the bundled public adapter is unavailable. Capture visible captions or an authorized media reference; do not bypass access controls.
5. **Configured downloader/connector**: use only when already installed/configured and explicitly in scope. Keep cookies and raw media local; return only the manuscript and provenance.

If the adapter cannot yield actual speech/text, status is `blocked`. A URL, title, description, thumbnail, or platform metadata is not sufficient evidence.

## Common Contract

Every adapter should return:

```json
{
  "source_url": "optional canonical URL",
  "source_label": "human-readable label",
  "text": "actual supplied or transcribed text",
  "timestamps": [],
  "provider": "supplied | subtitle | ASR | OCR+ASR | other",
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
