---
name: video-transcript
description: Extract the actual spoken text from a supplied video source, correct context-supported recognition errors and typos, and return the complete manuscript in natural paragraphs. Do not summarize, rewrite, or invent content.
metadata:
  short-description: Extract and review a complete video manuscript
---

# Video Transcript

## Purpose

Do one job: obtain the actual spoken manuscript from the source, check it in context, fix supported semantic or spelling errors, and return the complete text in natural paragraphs.

## Workflow

1. Accept a user-provided video URL, local video/audio file, subtitle file, or transcript. Processing the supplied source is authorized for this extraction attempt only; do not publish or redistribute it.
2. Obtain actual speech text with whatever media, subtitle, or transcription capability is already available in the current Codex session. Prefer a user-supplied transcript or source-tied subtitle, then readable media. Do not install software, download model weights, require local models, or require vendor-specific tools.
3. Treat the title, description, hashtags, thumbnail, share text, search results, and OCR-only text as metadata, never as the transcript. Do not bypass login, anti-bot controls, paywalls, regional restrictions, or copyright controls.
4. Keep the untouched source transcript as `raw` internally. Read it completely before editing.
5. Compare `raw` with the strongest available evidence: audio/video, source-tied subtitles, visible captions, timestamps, and user corrections. Fix only evidence-supported homophones, names, numbers, negations, semantic substitutions, duplicated or omitted fragments, and typos. Context may choose between clearly plausible words, but may not invent missing speech.
6. Produce `reviewed`: the complete transcript in original speaking order. Keep all meaning-bearing content and repetition. Normalize punctuation and split natural paragraphs by topic, story beat, or speaker turn. Do not summarize, polish the style, add ideas, or silently omit uncertain words.
7. Return the reviewed manuscript first. Add a short note only when useful: what evidence was checked, substantive corrections, and any unresolved wording. Keep `raw` separate and include it only when the user asks for audit detail.

## When Speech Cannot Be Obtained

If the current session cannot access actual speech text, say so briefly and do not fabricate a transcript from metadata. Ask for one of: source-tied subtitles (`.srt`/`.vtt`), a text transcript, or a video/audio file that the current session can read. Do not ask the user to repeat a URL already provided.

Read [references/transcript-verification.md](references/transcript-verification.md) for the correction and uncertainty rules.
