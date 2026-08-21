---
name: video-transcript
description: Extract a real video manuscript with Codex-native media understanding when available, context-correct it, and return a naturally paragraphed reviewed version with evidence-bounded corrections. Do not require vendor-specific software, local models, or other user-installed ASR dependencies; do not use for creative rewriting, publishing, or platform-access bypass.
metadata:
  short-description: Extract and verify authorized video manuscripts
---

# Video Manuscript Extraction and Verification

This skill has one narrow job: obtain the actual spoken/visible manuscript from an authorized video source using capabilities already available in the Codex session, then verify and correct the transcript without inventing missing content. It is an orchestration and review instruction, not a bundled transcription engine.

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

1. **Confirm source and authorization.** Accept a user-provided URL, local video/audio, subtitle file, or transcript. Do not bypass login, anti-bot controls, paywalls, regional restrictions, or copyright controls. A title, description, thumbnail, search result, or share text without accessible video/text is not a manuscript.
2. **Choose the available adapter.** Prefer user-supplied subtitles/transcript. Next use Codex-native audio/video understanding on media the session can actually inspect (an attached file, supported workspace media, or an authorized media connector). For a public Douyin URL, the bundled anonymous Chromium adapter (`scripts/download_public_douyin.py`) may obtain a temporary media file, but downloading alone is not transcription: pass it to a Codex-native media capability only when the current session supports that handoff. An external ASR service is an optional, explicitly user-approved fallback; it must already be configured and must not trigger installation instructions or model downloads. If no native capability, supplied text, or approved fallback is available, report `blocked` and state exactly what evidence is missing.
3. **Create a temporary acquisition workspace.** Keep downloaded video, extracted audio, OCR frames, cookies, and intermediate files outside the final output. Use bounded file sizes/timeouts and clean temporary files on both success and failure. Never put API keys, cookies, browser profiles, or raw media in a repository or skill artifact.
4. **Extract the raw manuscript.** Preserve the provider and method (`codex_native`, `supplied`, `subtitle`, `ASR`, `OCR+ASR`, or other), timestamps when available, language, and confidence. Never overwrite the raw transcript with an AI rewrite.
5. **Run a second-pass review.** Read the full raw transcript in context, then compare suspicious spans with the strongest available evidence. Fix clear ASR semantic errors, homophones, names, numbers, negations, and typos when the audio/subtitle/OCR or immediate sentence context supports the correction. Context may disambiguate a recognition error, but it may not supply a new fact or reconstruct missing speech.
6. **Create the reviewed manuscript.** Keep every supported spoken idea and the original sequence. Normalize obvious punctuation, remove ASR-only clutter, and split into natural paragraphs by topic, story beat, or speaker turn. Do not polish the author's style, change word choice merely for elegance, merge distinct claims, or silently omit repetition that carries meaning.
7. **Record corrections and uncertainty.** Log every non-trivial lexical or semantic change with its evidence and confidence. Leave unresolved spans unchanged (or mark them inline) and list them for the user; never present guessed text as verified.
8. **Finish at the evidence boundary.** `verified` means the reviewed transcript is sufficiently supported by the available source evidence. `needs_review` means a human must resolve listed uncertainties. `blocked` means the actual media/text could not be obtained or the source is not authorized.

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

Read [references/transcript-verification.md](references/transcript-verification.md) for the verification checklist, correction schema, and status criteria.
