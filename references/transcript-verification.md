# Transcript Verification

## Verification Checklist

Check each segment against the strongest available evidence, in this order:

1. Audio/video speech and visible captions.
2. User-supplied subtitles or transcript tied to the same source.
3. ASR timestamps and confidence.
4. OCR text from frames, used as supporting evidence rather than assumed speech.
5. Context or general knowledge, used only to flag an ambiguity, never to invent a replacement.

Review these error classes explicitly:

- omitted or duplicated phrases;
- homophones and dialect pronunciation;
- names, products, places, dates, numbers, and units;
- negation, modality, and other meaning-changing words;
- speaker changes and quoted speech;
- subtitle line joins and punctuation;
- OCR character substitutions;
- ASR/OCR/subtitle disagreement.

## Second-Pass Semantic Review

After the raw transcript is complete, read it as a whole before editing. Use the immediate sentence, established terminology, parallel lists, and the speaker's argument to detect ASR substitutions that are semantically impossible or clearly inconsistent. Accept a correction only when the audio, source-tied subtitle/OCR, or strong local context supports it. Context can select between plausible words (for example, a system's "input" versus "income"), but it cannot add a new fact, infer an unstated number, or rewrite the speaker's position.

Produce a separate `manuscript.reviewed` text. Keep the original sequence and all meaning-bearing repetition, fix supported typos and recognition errors, normalize harmless punctuation, and split the text into natural paragraphs by topic, story beat, or speaker turn. Do not polish wording for style, summarize, or silently delete uncertain content. Every lexical or semantic change belongs in `corrections.json`; paragraph breaks and harmless punctuation may be recorded as a grouped formatting change.

## Correction Record

Keep corrections separate from the raw manuscript:

```json
{
  "segment": "00:12.4-00:15.8",
  "original": "raw recognized text",
  "corrected": "evidence-supported text",
  "reason": "audio clearly contains ...",
  "evidence": "audio | subtitle | visible_caption | user_confirmation",
  "confidence": "high | medium | low",
  "decision": "proposed | accepted | rejected | unresolved"
}
```

Only `accepted` corrections become part of `manuscript.reviewed`. Keep `proposed` and `unresolved` items visible.

## Status Criteria

### `verified`

- The actual source media or a source-tied transcript/subtitle was obtained.
- The transcript is complete enough for the requested scope.
- Material names, numbers, negations, omissions, and disagreements were checked.
- No unresolved high-impact ambiguity remains.

### `needs_review`

- The source was obtained, but one or more material spans are uncertain.
- ASR/OCR/subtitles disagree and the available evidence cannot decide.
- The transcript is readable but requires user confirmation for fidelity.

### `blocked`

- Authorization is missing or unclear.
- The actual media/text could not be obtained.
- The result is empty, truncated, or too low quality to compare.
- Required local tools or an authorized browser/session are unavailable.

## Minimal Case Files

When the user asks for files, use a small case directory:

```text
<case>/
  source.json
  manuscript.raw.txt
  manuscript.reviewed.txt
  corrections.json
  verification.json
```

`verification.json` should contain `status`, `provider`, `checked_evidence`, `unresolved_segments`, `cleanup_status`, and `updated_at`. Do not store raw video, audio, cookies, API keys, or browser profiles in this directory.
