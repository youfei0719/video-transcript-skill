# Transcript Verification

Compare the complete raw transcript with the strongest available evidence, in this order:

1. Audio/video speech and visible captions.
2. Source-tied subtitles or a user-provided transcript.
3. Timestamps and transcription confidence.
4. OCR, only as supporting evidence.
5. Context, only to flag ambiguity or choose between clearly plausible words.

Check especially names, products, places, dates, numbers, units, negations, omitted or duplicated phrases, homophones, speaker changes, quoted speech, subtitle joins, punctuation, and OCR substitutions.

Read the raw text completely before editing. Accept a correction only when the source evidence supports it. Context may disambiguate a recognition error, but it cannot add a new fact, infer an unstated number, or rewrite the speaker's position.

The reviewed manuscript must be complete, preserve speaking order, retain meaning-bearing repetition, and use natural paragraphs. Punctuation and paragraph breaks are formatting changes. Do not summarize, polish, or silently delete uncertain speech.

For each substantive correction, record internally:

```json
{
  "original": "raw text",
  "corrected": "evidence-supported text",
  "reason": "why the source supports the change",
  "evidence": "audio | subtitle | visible_caption | timestamp | user_confirmation",
  "confidence": "high | medium | low",
  "decision": "accepted | unresolved"
}
```

Leave unresolved wording unchanged and tell the user briefly. Use `needs_review` when the source is available but a material ambiguity remains. Use `blocked` when actual speech text was not obtained.
