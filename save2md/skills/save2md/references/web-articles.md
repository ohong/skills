# Web Articles

Save the requested article or section as `<extracted-title>.md` in `~/Documents/Saved Articles/Web/`, unless the user specifies a destination. Include the source link and content; remove navigation, forms, repeated headings, and unrelated sections.

Use the original page first for public content. Extract structured text or rendered DOM directly when available. Store any working HTML in temporary storage.

For paywalled or inaccessible articles, use the bundled archive helper:

```bash
python3 scripts/archive_article.py "https://example.com/article"
```

The helper tries archive.ph/archive.today, then a text reader. It writes only the Markdown by default. Warnings go to stderr. Inspect the result and retry with accessible browser HTML when extraction fails or includes a challenge, paywall, or page chrome.

Options:

- `--out-dir /path/to/folder`: requested output directory.
- `--archive-url URL`: known snapshot while preserving the original source link.
- `--html-file /path/to/page.html`: extract from saved HTML.
- `--no-reader-fallback`: disable the text reader.
- `--debug`: retain `source.json`, fetched HTML, and reader output for troubleshooting. Use only when requested.

Do not copy intermediate files into the final library. Mention incomplete extraction or material fallback briefly in the reply.
