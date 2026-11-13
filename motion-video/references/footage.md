# Real footage

Read when a beat is marked `source: clip`. Real footage grounds an explainer in the world (the actual bridge, the actual launch, the actual lab) in a way generated video can't, so prefer it whenever the beat is about something that happened or exists.

## Rights come first

Use only clips whose uploader marked them Creative Commons (on YouTube that means CC BY), public-domain archives, or material the user has cleared. The license on the page is the uploader's claim, so skip anything that is obviously a re-upload of broadcast, film, or music-video content even if it says CC. CC BY requires attribution, so every clip gets a line in `assets.md` and a credit in the end card or description.

## Search and download

`scripts/find_clips.py` wraps yt-dlp. It searches, keeps only results whose `license` field says Creative Commons, and writes a candidate list with title, channel, URL, duration, and license:

```sh
uv run scripts/find_clips.py search "Tacoma Narrows bridge collapse 1940" --n 20 --out footage/candidates.json
```

Expect low yields: most YouTube uploads carry no license metadata, so a specific historical query often returns nothing. When that happens, search broader terms, try public-domain archives (the Internet Archive's Prelinger collection, NASA, Wikimedia Commons), or use `--license-override "reason"` for material the user has cleared, which records the reason in the ledger.

Review the candidates (thumbnails and descriptions, then watch the promising ones), pick the exact in and out points, and download only that section:

```sh
uv run scripts/find_clips.py get "https://www.youtube.com/watch?v=..." --section 12.5-18.0 --out footage/tacoma-1940.mp4 --ledger assets.md
```

Under the hood that is `yt-dlp --download-sections "*12.5-18.0" --force-keyframes-at-cuts`, with the format capped at the project's output height. The `--ledger` flag appends the source URL, channel, license, section, and retrieval date to `assets.md`.

The same approach works for Wikimedia Commons, the Internet Archive, and NASA, which yt-dlp also supports; their license terms are on each item's page, so record them by hand.

## Fitting clips into the film

Archival and phone footage rarely matches the project's aspect ratio, frame rate, or color. Reframe with a deliberate crop (or a blurred-fill background for vertical source in a horizontal film) rather than stretching, conform to the project frame rate in assembly, and apply a light shared grade so clips sit next to generated shots. Strip the clip's own audio unless the beat needs its natural sound, and never keep its music.
