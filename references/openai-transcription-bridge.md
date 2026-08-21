# Official OpenAI Transcription Bridge

## Why a bridge is required

The skill is an orchestration layer. A Codex skill cannot create a speech recognizer, and the current Codex CLI input surface does not expose a general audio/video attachment or transcription operation. Use an MCP tool as the capability boundary:

```text
video-transcript skill -> transcribe_media MCP tool -> OpenAI file transcription API -> raw transcript -> semantic review
```

Do not put an OpenAI API key in the skill, repository, prompt, logs, or local case files. The bridge owns the key and provider request.

## Provider request

The bridge should call the official endpoint:

```text
POST https://api.openai.com/v1/audio/transcriptions
model=gpt-transcribe
```

OpenAI's official speech-to-text guide documents `gpt-transcribe` for completed recordings, a 25 MB file limit, and these input formats: `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, and `webm`. The bridge should request structured output/segments when supported, preserve the provider response as raw text, and pass language hints only when known.

## MCP boundary

Expose a tool named `transcribe_media` (or an equivalent declared in the contract) with these responsibilities:

1. Accept a user-authorized URL or request-scoped media reference.
2. Allow only approved source domains and enforce duration/size limits before provider upload.
3. Fetch/normalize media inside the bridge; do not require the Codex user to install a model, ffmpeg, or a platform downloader.
4. Upload the bounded media to the official OpenAI endpoint using a server-side key.
5. Return untouched text, segments/timestamps when available, language, confidence, provider, and cleanup status.
6. Delete downloaded media and extracted audio in both success and failure paths.

Codex can register a remote streamable HTTP MCP server with `codex mcp add <name> --url <server-url>`. Do not put a placeholder URL into this skill or claim the bridge is configured until `transcribe_media` is actually visible in the session.

## Failure mapping

- `PROVIDER_NOT_CONFIGURED`: no MCP bridge is registered or the tool is not visible.
- `PROVIDER_AUTH_REQUIRED`: the bridge exists but its provider credential is absent/expired.
- `MEDIA_UNREADABLE`: the source was fetched but cannot be decoded or exceeds provider limits.
- `NO_TRANSCRIPT_EVIDENCE`: the provider returned no usable speech text.

For the first two cases, keep the source URL and return a resumable `next_action` asking the user to configure or authenticate the bridge. Never ask for an API key in chat and never retry with a local model by default.

## Privacy and cost

Sending media to OpenAI is an external transfer and requires source-specific user approval. The bridge must disclose provider use, enforce quotas/rate limits, avoid raw-media logs/backups, and delete request-scoped media after transcription. A Codex subscription is not itself an OpenAI API billing credential; the bridge operator must provide an approved API project or an equivalent authorized provider.
