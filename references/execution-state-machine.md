# Execution State Machine

The workflow is deliberately staged so acquisition cannot be mistaken for transcription.

```text
SOURCE_RECEIVED
  -> PREFLIGHT
  -> TEXT_READY       (user text or source-tied subtitles)
  -> MEDIA_CAPABLE    (native media capability or configured transcript tool)
  -> MEDIA_ACQUIRED   (only after a consumer is known)
  -> RAW_READY
  -> REVIEWED
  -> VERIFIED | NEEDS_REVIEW
```

Failure transitions are resumable:

```text
PREFLIGHT      -> BLOCKED / NO_TRANSCRIPT_TOOL
SOURCE_ACCESS  -> BLOCKED / NO_ADAPTER
MEDIA_ACQUIRED -> BLOCKED / MEDIA_UNREADABLE
TRANSCRIPTION  -> BLOCKED / NO_TRANSCRIPT_EVIDENCE
```

## Stage Rules

- `SOURCE_RECEIVED`: normalize the user URL or file reference. Keep the user-provided share text as metadata only.
- `PREFLIGHT`: inspect callable capabilities in the current session. A browser or downloader is not a transcript consumer. If no consumer exists, stop before media retrieval.
- `TEXT_READY`: accept only text tied to the source. Treat platform title, description, hashtags, and OCR-only text as supporting metadata, never as speech.
- `MEDIA_CAPABLE`: select either Codex-native media understanding or an already configured transcript tool. For a remote tool, obtain source-specific consent immediately before transfer.
- `MEDIA_ACQUIRED`: keep media request-scoped and bounded. The selected consumer must own cleanup; the skill must not leave media in output directories.
- `RAW_READY`: preserve untouched provider text, timestamps, language, confidence, and retention state.
- `REVIEWED`: correct only evidence-supported recognition/semantic errors and paragraph the complete text.
- `VERIFIED` or `NEEDS_REVIEW`: return the manuscript and an auditable correction list.

## Resume Rules

When returning `blocked`, keep the canonical source and completed stage in `verification`. Return one concrete `next_action` and accepted inputs. On the next user turn, reuse the source and continue from that stage; do not ask for the same URL again or repeat already completed acquisition.
