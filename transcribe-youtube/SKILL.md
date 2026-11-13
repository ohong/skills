---
name: transcribe-youtube
description: Transcribe a YouTube video through usetranscribe.io and save timestamped Markdown. Use for YouTube transcription or transcript-based summaries and follow-up questions.
---

# Transcribe YouTube

Use [save2md's YouTube guide](../save2md/skills/save2md/references/youtube.md)
and its bundled `transcribe_yt.py` helper. This is an explicit adapter to that
workflow; do not maintain a second service procedure or substitute providers.

Read the current [service guide](https://www.usetranscribe.io/AGENTS.md) before
calling the service. Use the user's destination, inspect the saved transcript,
and return its absolute path and hosted permalink. Link the service guide.
For follow-up answers, use the saved transcript and cite timestamps. Do not
invent missing segments or replace the requested transcript with only a summary.
