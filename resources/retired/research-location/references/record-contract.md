# Portable research records

Use this small contract for the skill's local audit. Additional evidence and project-compatible fields are welcome.
If the active project has a source or board schema, preserve its interfaces and adapt this portable export alongside it.
Do not overwrite incompatible existing records. IDs stay stable across reruns; source IDs and block IDs are different.
All relative paths below resolve from the case directory supplied through `--root`.

```text
sources/sources.json
sources/credits.md
sources/assets/                    # Only explicitly permitted copied media
boards/research-board.json
boards/arena-snapshot.json          # Actual complete readback after publication
boards/curator-brief.md             # 500–800 words
boards/direction-opportunities.md
boards/qa-report.md
provenance/research-log.md
provenance/arena-publication.json
```

The research log also preserves candidates, exclusions, explicit user target overrides, material access failures, and concise curation decisions. Keep research actions and rationale, not private reasoning transcripts.
Credits list every source and copied asset, original creator, media credit, canonical URL, date/access, and the three separate rights statuses.

## Sources

`sources.json` is `{ "site_id": "<location-slug>", "sources": [...] }`.
Optional `thresholds` overrides any of `min_sources:51`, `min_visual:24`, `min_local:22`, `min_primary_share:0.60`, `min_publishers:10`, and `opening_visuals:8`.
Any override requires a nonempty `override_reason` describing the user's explicit request. Never reduce a requirement just to pass.
Count thresholds are positive integers; primary share is greater than zero and at most one.

Each selected underlying work has exactly one source record. Multiple views become `media` entries or display blocks.
`work_id` identifies the underlying work independently of URL. Duplicate work IDs fail audit while the report still counts distinct works.
Duplicate canonical URLs also fail. Normalize aliases, mirrors, fragments, and tracking links before selection; the helper cannot discover undisclosed duplicate works.
`publisher_id` is a normalized originating publisher/creator identity, not a host domain. Record same-project independent works with a shared `same_project.id` and a source-specific reason for distinct evidence/authorship.

The following abbreviated example shows shape, not a verified source or a passing collection. It intentionally lacks a complete annotation and inspected image:

```json
{
  "id": "river-district:source-001",
  "work_id": "municipal-archive-quay-survey-1924",
  "canonical_url": "https://archive.example.org/catalog/quay-survey-1924",
  "title": "Quay survey drawing, 1924",
  "publisher_id": "municipal-archive",
  "publisher": "Municipal Archive",
  "source_type": "map",
  "locality": "local",
  "primary": true,
  "chapter": "01",
  "group": "landscape",
  "observation": "Record the inspected drawing's actual levels, boundaries, labels, and catalog scope here.",
  "interpretation": "Label a possible change in pedestrian approach or building section as our interpretation.",
  "limit": "Explain changes since the survey and why it cannot establish current boundaries or development rights.",
  "creator": "Municipal survey office",
  "date": "1924",
  "accessed_at": "2026-09-08",
  "media_credit": "Unknown; catalog does not identify the draughtsperson",
  "rights": {
    "board": "Canonical link only; reproduction permission unknown",
    "local_redistribution": "unknown",
    "model_input": "unknown",
    "evidence": "Catalog does not state a reproduction license"
  },
  "inspection": {
    "method": "Catalog page read",
    "evidence": "Identify the reviewed catalog fields and access limit",
    "visual": false,
    "visual_evidence": ""
  },
  "media": []
}
```

Required source fields are those above. `date` may be `null`, `unknown`, or a known date/year string. Never invent missing dates or credits.
`locality` is `local`, `adjacent`, `nearby`, or `external`; only the first two count toward the local minimum.
Use `adjacent` for immediately neighboring context, not a broad metropolitan area. Define these boundaries in orientation.
`primary` is boolean. Chapters are strings `01` through `06`.
Groups are `landscape`, `architecture-history`, `materials-detail`, and `infrastructure-precedents`.
The three annotation fields together contain 70–120 words; attribution is excluded.

`inspection.method` and `inspection.evidence` are required even for text-only sources.
To count as visually inspected, set `inspection.visual:true`, supply `visual_evidence`, and include at least one inspected `media` item with the following shape:

```json
{
  "url": "https://archive.example.org/media/quay-survey-detail.jpg",
  "caption": "Specific observed subject and view, after inspection",
  "alt": "Concrete description of the inspected image",
  "credit": "Image-specific creator or explicit unknown",
  "rights": {
    "board": "State permitted link/preview use and limit",
    "local_redistribution": "unknown",
    "model_input": "unknown",
    "evidence": "Image-specific rights statement or explicit absence"
  },
  "inspection": {
    "method": "Opened original image",
    "evidence": "Describe the actual detail inspected, with page or timestamp if applicable"
  }
}
```

Do not copy these placeholder claims into a collection. Each inspection needs actual observed evidence.
Preserve canonical work URL separately from media URLs. All URLs must be credential-free HTTP(S); canonical URLs should omit fragments and tracking parameters.
The helper ignores common tracking keys, fragments, and trailing slashes when checking canonical duplicates. Media URLs may retain useful page/timestamp fragments.
Each media item carries its own rights and review record. A page's general license cannot silently authorize an image.
`local_redistribution` is `approved`, `unknown`, or `not_permitted`; approval requires nonempty evidence.
Only copied media add `local_path`, for example `sources/assets/quay-detail.jpg`.
That exact item's redistribution must be `approved`, backed by specific license/permission evidence. Paths must resolve inside the case's `sources/assets/`, exist, and be referenced. Unknown or denied copied assets fail.
Keep temporary review images outside the package. Model-input permission is independent of local redistribution.

## Board and synthesis

`research-board.json` contains `site_id`, `blocks`, `display_order`, and `connections`.
Every block has a site-namespaced `id`, nonempty `title`, `kind` (`source` or `synthesis`), and `source_ids` array.
A source block references at least one selected source; each selected source has a source display block.
Source annotations are resolved from those source records, retaining visible observation/interpretation/limit labels.
A work may have multiple display blocks without changing its count.

A synthesis block also requires `authored:true`, nonempty `content`, and `card_type`: `orientation`, `dna`, `palette`, `direction`, or `avoidances`.
Publish the visible label **“Authored synthesis — not an external source”**, optionally prefixed by the inferred studio name.
There are exactly eight synthesis blocks: one orientation, one DNA, one palette, four directions, and one avoidances card.
Each direction has at least five distinct source refs, including at least three local/adjacent sources; `moves` is an array of at least three substantive strings and `tradeoff` is nonempty text.
Avoidances describes five specific, source-backed mistakes. Orientation may have an empty source array when it only describes the brief.

```json
{
  "id": "river-district:direction-01",
  "title": "A stepped public edge",
  "kind": "synthesis",
  "authored": true,
  "card_type": "direction",
  "content": "Authored synthesis — not an external source. Develop the source-linked proposition here.",
  "source_ids": ["river-district:source-001"],
  "moves": ["Describe move one", "Describe move two", "Describe move three"],
  "tradeoff": "State the actual cost, tension, or limitation"
}
```

This abbreviated direction is not passing: it needs four additional distinct references and sufficient local evidence.
`display_order` lists every block ID exactly once. It starts with orientation followed by the configured number of distinct inspected source visuals.
Keep six-chapter rhythm and annotation adjacency clear in actual publication; the helper checks opening and membership, not editorial quality.
`connections` contains at least five `{ "source_ids": ["id1", "id2"], "claim": "Source-specific defensible relationship" }` objects.
Each references at least two selected works. Manual review must establish distinct, meaningful connections and directions.

## Journal and actual snapshot

Before publication, the journal can record `status:"pending"`, missing channel access, and unresolved items.
After publication, normalize these fields from actual CLI responses:

```json
{
  "channel_id": 123,
  "url": "https://www.are.na/account/actual-returned-slug",
  "visibility": "private",
  "status": "complete",
  "failures": [],
  "blocks": [
    {"local_block_id": "river-district:orientation", "arena_block_id": 456}
  ]
}
```

Example IDs above are illustrative, never a default destination. Retain timestamps, attempts, connection IDs, and uncertain writes in additional fields. Persist failed items instead of dropping them.

The actual `arena-snapshot.json` retains normalized audit fields below alongside useful returned titles, descriptions, source URLs, media/preview metadata, connection IDs, and read timestamps. Do not fabricate snapshot rows from the planned manifest.

```json
{
  "channel_id": 123,
  "visibility": "private",
  "complete": true,
  "total": 1,
  "blocks": [{"id": 456, "state": "available"}],
  "native_order": [456],
  "pages": [{"page": 1, "next_page": null, "block_ids": [456]}]
}
```

Normalize paginated/cursor responses into consecutive page numbers, preserving actual response provenance separately where useful. `next_page` points to the next normalized number or is `null` on the terminal page.
Pages are nonempty as a list even for an empty channel. All page IDs flatten to native order, and the reported total matches complete snapshot membership.
For an existing channel, retain unrelated historical blocks in snapshot and page totals. Only the managed curated subsequence must match `display_order`; the entire channel need not equal the new collection's size.
`--published` requires every managed block in the journal and snapshot, available state, consistent visibility/channel, complete pagination, and no unresolved failures.
This verifies saved records, not live access. Actual readback and browser inspection remain separate QA evidence.
