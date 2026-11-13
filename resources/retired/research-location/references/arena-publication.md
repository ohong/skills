# Are.na publication mechanics

## Discover current commands and access

Consult the official [CLI resource](https://www.are.na/developers/resources/cli), [CLI repository](https://github.com/aredotna/cli), [channel visibility](https://help.are.na/docs/getting-started/channels), and [handling blocks with care](https://help.are.na/docs/guides/handling-blocks-with-care) during execution.
Use the official `@aredotna/cli` package and `arena` executable, requiring Node.js 20 or later; verify current requirements and actual versions.
Prefer an existing permitted installation. If absent, install the official package in the task's permitted environment.

```sh
node --version
arena --help
arena --json whoami
arena help channel
arena help add
arena help upload
```

Read command-specific help for channel creation, insertion, uploads, connections, positions, and paginated readback before issuing those commands. Do not copy stale flags from past projects.
Authentication uses `arena login`; the human completes OAuth. Never request or expose credentials. If access is missing, continue local work and report the precise access step needed.

Read the destination and all existing content before writes. Confirm channel identity, visibility, and permission to add. A supplied URL must be resolved to the actual channel identifier; a title is not an identifier.
Reuse an authorized channel. Otherwise create private. Only change visibility when authorized for this destination; closed permits public reading and restricted editing, while public permits open contribution.
Save the returned canonical URL because renaming can change the slug.

## One writer, recoverable writes

Only the lead curator publishes. Prefer paced sequential writes over a bulk submission because each returned identifier can be saved and reconciled.
Use structured CLI arguments or subprocess argument arrays; never interpolate research text into shell command strings.
Read JSON output. Journal the channel ID, local block ID, returned block ID, connection ID when returned, operation, timestamp, and result immediately after each write.
Use stable site-namespaced local IDs in owned metadata when supported. Keep source and display-block identities separate.

Before each creation, look for a saved ID, then stable local metadata, then the canonical source URL and intended annotation.
Do not treat a URL match alone as permission to edit shared content. An unmanaged existing source may be connected or reused and accompanied by a new authored interpretation.
Never change the title, description, attribution, source, or other shared metadata of a reused block. Limit edits to your own cards and authorized channel connections.

After a timeout or connection loss, read the channel and reconcile the intended operation before retrying. A timeout is an uncertain result, not proof of failure.
Retry only appropriate transient errors, such as rate limits or temporary service failures. Honor Retry-After where supplied; otherwise use bounded backoff, for example 2, 5, and 10 seconds with pacing.
Stop after three unsuccessful reconciled attempts for an item. Persist its failed or uncertain state, continue safe independent work, and report publication incomplete.
Do not retry authentication, permission, validation, or rights failures as transient errors. Never create duplicates to force progress.

Prefer canonical source links and credited platform previews. An inspected media URL may be the display input while the canonical work URL remains in attribution.
Publish full annotations, creator and media credit, source URL, dates, locality, interpretation label, and rights limits.
Upload only explicitly permitted assets. Use an annotated source-link card for a PDF if ingestion would copy an unapproved report.

## Ordering and readback

Do not assume insertion order equals presentation order. Inspect current connection positions and browser behavior.
Reverse insertion may suit a newest-first channel; confirm this before depending on it. Preserve unrelated existing content and positions.
Use supported connection-position operations for authorized curated content when necessary, then read back the result.
For reused nonempty channels, compare the curated subsequence with intended order. Historical unrelated blocks are permitted and must remain represented in the full snapshot.

Fetch every page until the API/CLI reports no continuation. Save a sanitized actual snapshot and page provenance, not a reconstruction from the local manifest.
The contract's normalized snapshot retains IDs, state, native order, page membership, actual channel visibility, reported total, and read timestamp. Additional useful source and preview fields may remain; remove secrets and irrelevant account metadata.
Match each intended local block to its returned ID and available state. Distinguish a complete readback from a complete publication.

Inspect the actual Are.na UI when browser access is available. Check opening sequence, important images, source links, annotation placement, and audiovisual usability.
For public-link delivery, test signed-out browser access. Anonymous API access can return 403 even when the signed-out browser can read a closed channel; API 403 alone is inconclusive.
For private channels without an authenticated browser, report UI inspection unavailable without exposing the board.
You may inspect returned thumbnails to test previews, but label that evidence separately. It cannot establish full-page rendering, source-image review, or video playback.
Record these distinctions and unresolved gaps in `boards/qa-report.md`.
