# Transcript Tool Contract

This skill can call a transcript MCP/plugin tool only when one is already available in the current Codex session and the user has approved sending the source to it. The skill must not install a server, download a model, or invent a provider.

## Logical Operation

The tool may be named `transcribe_media` or expose an equivalent operation. Its logical input is:

```json
{
  "source": "temporary local media reference or authorized media URL",
  "language_hint": "optional BCP-47 language",
  "include_segments": true,
  "retention": "delete_after_request"
}
```

It must return, at minimum:

```json
{
  "status": "ready | needs_review | blocked",
  "provider": "remote_transcript",
  "text": "untouched transcript",
  "segments": [{"start": 0.0, "end": 1.2, "text": "...", "confidence": 0.0}],
  "language": "zh-CN",
  "confidence": "high | medium | low",
  "source_url": "optional canonical source",
  "media_retention": "temporary_deleted | user_retained | not_received",
  "error_code": null
}
```

## Required Service Behavior

- Accept only a user-authorized source and enforce platform/domain and size/duration limits.
- Make outbound transfer explicit. A Codex login or subscription is not permission to use an unrelated ASR provider.
- Keep raw media and extracted audio request-scoped; delete them on both success and failure when `delete_after_request` is selected.
- Do not place media, raw transcript, credentials, cookies, or authorization headers in logs, caches, backups, or repository files.
- Return timestamps and confidence when the provider supports them. A prose-only response is lower-confidence and must not be reported as fully verified solely because it is long.
- Return `blocked` or `needs_review` when media is inaccessible, speech is missing, or retention/authorization requirements cannot be met.

The skill may continue to semantic review only after receiving actual speech text. It must never treat a title, description, hashtags, thumbnail, OCR-only text, or a failed tool message as the transcript.
