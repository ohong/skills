---
name: save2md
description: Save articles, X posts or threads, and YouTube transcripts as local Markdown with bundled tools. Use when the user asks to save or archive a URL as Markdown, including paywalled articles.
---

# Save to Markdown

Save the requested content as one Markdown file with its title and source link. Inspect it and return the absolute path.

## Route by URL

1. Normalize the URL and identify its host.
2. Read the relevant source guidance:
   - `youtube.com` or `youtu.be`: read [references/youtube.md](references/youtube.md).
   - `x.com` or `twitter.com`: read [references/x.md](references/x.md).
   - Any other web or archive URL: read [references/web-articles.md](references/web-articles.md).
3. Use the user's requested destination. Otherwise use `~/Documents/Saved Articles/` with the source subfolder `Web`, `X`, or `YouTube`. Name the final Markdown file from the extracted title, using a filesystem-safe version of the title, never a generic name such as `article.md`.
4. Open or inspect the generated Markdown before responding. Reject CAPTCHA pages, paywall prompts without article text, navigation chrome, empty transcripts, broken media, and suspiciously short output.
5. Keep the final response short and link the absolute Markdown path. Mention any fallback, incomplete extraction, or podcast-to-YouTube substitution.

## Shared rules

- Do not invent text, metadata, authors, dates, media, or archive URLs.
- Prefer structured text or rendered DOM extraction over OCR.
- Keep the output lean: title, source link, requested content, and useful author/date information when available. Do not include extraction logs or technical metadata.
- Keep intermediate HTML, reader responses, manifests, and screenshots in temporary storage. Retain diagnostics only when requested; helpers support `--debug`.
- Save local media only when it is part of the requested content. Do not create empty media folders.
- When the user requests a section, extract only that section and remove repeated responsive-layout text.
- Use the extracted title for the final Markdown filename. Preserve readable capitalization and punctuation where the filesystem permits; replace only unsafe filename characters. If no title can be extracted, use the URL-derived title.
- For public pages, use the original page first. For paywalled articles, try archive.today/archive.ph, then a readable-text fallback or browser-saved HTML. Mention material fallbacks briefly in the reply.
- Do not ask the user to choose an extraction method. Try the safe routes in order and report a blocker only after they fail.
