#!/usr/bin/env python3
"""Read-only audit of the research-location record contract. No network or writes."""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit

DEFAULTS = dict(min_sources=51, min_visual=24, min_local=22,
                min_primary_share=0.60, min_publishers=10, opening_visuals=8)
GROUPS = {'landscape', 'architecture-history', 'materials-detail', 'infrastructure-precedents'}
LOCALITIES = {'local', 'adjacent', 'nearby', 'external'}
RIGHTS = {'approved', 'unknown', 'not_permitted'}


def audit(root, published):
    errors = []
    counts = {}

    def check(condition, message):
        if not condition:
            errors.append(message)
        return bool(condition)

    def read(relative):
        path = root / relative
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError) as exc:
            errors.append(f'{relative}: {exc}')
            return {}

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def required(obj, fields, label):
        for field in fields:
            check(text(obj.get(field)), f'{label}: missing/nontext {field}')

    def url(value, label, canonical=False):
        try:
            parts = urlsplit(value if isinstance(value, str) else '')
            # Query-bearing canonical pages are allowed; embedded credentials are not.
            sensitive = re.compile(r'(^|[_-])(token|key|secret|password|signature|credential|auth)([_-]|$)', re.I)
            valid = (parts.scheme in {'http', 'https'} and parts.hostname and
                     not parts.username and not parts.password and
                     not any(c.isspace() for c in value) and
                     not any(sensitive.search(k) for k, _ in parse_qsl(parts.query)))
            check(valid, f'{label}: invalid or credential-bearing HTTP URL')
            if canonical:
                query = [(k, v) for k, v in parse_qsl(parts.query)
                         if not k.lower().startswith('utm_') and k.lower() not in {'fbclid', 'gclid'}]
                parts = parts._replace(fragment='', query=urlencode(sorted(query)), path=parts.path.rstrip('/'))
            return parts._replace(scheme=parts.scheme.lower(), netloc=parts.netloc.lower()).geturl()
        except (ValueError, TypeError):
            check(False, f'{label}: invalid HTTP URL')
            return ''

    def rights(obj, label):
        if not check(isinstance(obj, dict), f'{label}: rights object required'):
            return {}
        required(obj, ['board', 'model_input'], label)
        check(obj.get('local_redistribution') in RIGHTS, f'{label}: invalid local_redistribution')
        check('evidence' in obj and isinstance(obj['evidence'], str), f'{label}: rights evidence field required')
        if obj.get('local_redistribution') == 'approved':
            check(text(obj.get('evidence')), f'{label}: approved rights require evidence')
        return obj

    source_doc = read('sources/sources.json')
    board = read('boards/research-board.json')
    if not isinstance(source_doc, dict) or not isinstance(board, dict):
        return {'ok': False, 'counts': counts, 'errors': ['Manifest roots must be objects']}
    site = source_doc.get('site_id', '')
    check(text(site) and bool(re.fullmatch(r'[a-z0-9][a-z0-9-]*', site)), 'Invalid site_id')
    check(board.get('site_id') == site, 'Board site_id differs')
    thresholds = DEFAULTS.copy()
    overrides = source_doc.get('thresholds', {})
    if check(isinstance(overrides, dict), 'thresholds must be an object'):
        if overrides:
            check(text(source_doc.get('override_reason')), 'Threshold overrides require override_reason')
        for name, value in overrides.items():
            valid = name in DEFAULTS and type(value) in {int, float} and value > 0
            valid = valid and (value <= 1 if name == 'min_primary_share' else type(value) is int)
            if check(valid, f'Invalid threshold: {name}'):
                thresholds[name] = value
    sources = source_doc.get('sources', [])
    blocks = board.get('blocks', [])
    if not check(isinstance(sources, list) and isinstance(blocks, list), 'sources and blocks must be arrays'):
        return {'ok': False, 'counts': counts, 'errors': errors}
    by_id, works, canonical, visual, assets = {}, [], [], set(), set()
    for index, source in enumerate(sources):
        label = f'source[{index}]'
        if not check(isinstance(source, dict), f'{label}: object required'):
            continue
        sid = source.get('id')
        required(source, ['id', 'work_id', 'canonical_url', 'title', 'publisher_id', 'publisher',
                          'source_type', 'observation', 'interpretation', 'limit', 'creator',
                          'accessed_at', 'media_credit'], label)
        if not isinstance(sid, str):
            continue
        check(sid.startswith(site + ':'), f'{sid}: ID must be site-namespaced')
        check(sid not in by_id, f'Duplicate source ID: {sid}')
        by_id[sid] = source
        works.append(str(source.get('work_id', '')))
        canonical.append(url(source.get('canonical_url'), sid, canonical=True))
        check(source.get('locality') in LOCALITIES, f'{sid}: invalid locality')
        check(type(source.get('primary')) is bool, f'{sid}: primary must be boolean')
        check(source.get('chapter') in {'01', '02', '03', '04', '05', '06'}, f'{sid}: invalid chapter')
        check(source.get('group') in GROUPS, f'{sid}: invalid group')
        check('date' in source and (source['date'] is None or text(source['date'])), f'{sid}: date required (null allowed)')
        check(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(source.get('accessed_at', '')))), f'{sid}: accessed_at must be YYYY-MM-DD')
        words = sum(len(str(source.get(k, '')).split()) for k in ['observation', 'interpretation', 'limit'])
        check(70 <= words <= 120, f'{sid}: annotation is {words} words, expected 70–120')
        rights(source.get('rights'), sid)
        inspection = source.get('inspection', {})
        if not isinstance(inspection, dict):
            inspection = {}
        required(inspection, ['method', 'evidence'], f'{sid} inspection')
        check(type(inspection.get('visual')) is bool, f'{sid}: inspection.visual must be boolean')
        if inspection.get('visual') is True:
            required(inspection, ['visual_evidence'], f'{sid} inspection')
        media = source.get('media')
        inspected_media = False
        if check(isinstance(media, list), f'{sid}: media array required'):
            for item in media:
                if not check(isinstance(item, dict), f'{sid}: media item must be object'):
                    continue
                required(item, ['url', 'caption', 'alt', 'credit'], f'{sid} media')
                url(item.get('url'), f'{sid} media')
                item_rights = rights(item.get('rights'), f'{sid} media')
                seen = item.get('inspection', {})
                if isinstance(seen, dict) and text(seen.get('method')) and text(seen.get('evidence')):
                    inspected_media = True
                else:
                    check(False, f'{sid}: media inspection method/evidence required')
                if 'local_path' in item:
                    raw = item['local_path']
                    if check(text(raw), f'{sid}: local_path must be nonempty text'):
                        path = Path(raw)
                        resolved = (root / path).resolve()
                        check(not path.is_absolute() and resolved.is_relative_to(root) and resolved.is_relative_to((root / 'sources/assets').resolve()),
                              f'{sid}: asset escapes sources/assets')
                        check(resolved.is_file(), f'{sid}: asset missing: {raw}')
                        check(item_rights.get('local_redistribution') == 'approved' and text(item_rights.get('evidence')),
                              f'{sid}: copied media lacks explicit redistribution evidence')
                        assets.add(resolved)
        if inspection.get('visual') is True:
            check(inspected_media, f'{sid}: visual claim needs inspected media URL and evidence')
            if inspected_media:
                visual.add(sid)
        if 'same_project' in source:
            relation = source['same_project']
            check(isinstance(relation, dict) and text(relation.get('id')) and text(relation.get('reason')),
                  f'{sid}: same_project requires id and reason for separate authorship/evidence')
    for label, values in [('canonical URL', canonical), ('work_id', works)]:
        for value, number in Counter(values).items():
            check(number == 1, f'Duplicate {label} ({number}): {value}')
    for path in (root / 'sources/assets').rglob('*'):
        if path.is_file():
            check(path.resolve() in assets, f'Unreferenced local asset: {path.relative_to(root)}')
    check({s.get('chapter') for s in by_id.values()} == {'01', '02', '03', '04', '05', '06'}, 'All six chapters required')
    check({s.get('group') for s in by_id.values()} == GROUPS, 'All four groups required')
    distinct = {s.get('work_id'): s for s in by_id.values()}
    counts.update(sources=len(sources), distinct_works=len(distinct), visual=len({by_id[s]['work_id'] for s in visual}),
                  local=sum(s.get('locality') in {'local', 'adjacent'} for s in distinct.values()),
                  primary_share=sum(s.get('primary') is True for s in distinct.values()) / max(1, len(distinct)),
                  publishers=len({str(s.get('publisher_id', '')).strip().casefold() for s in distinct.values()}))
    for metric, key in [('distinct_works', 'min_sources'), ('visual', 'min_visual'), ('local', 'min_local'),
                        ('primary_share', 'min_primary_share'), ('publishers', 'min_publishers')]:
        check(counts[metric] >= thresholds[key], f'{metric}: {counts[metric]} below {thresholds[key]}')

    def refs(record, label):
        values = record.get('source_ids')
        if not check(isinstance(values, list) and all(isinstance(s, str) for s in values), f'{label}: source_ids array required'):
            return set()
        check(len(set(values)) == len(values), f'{label}: duplicate source refs')
        check(all(s in by_id for s in values), f'{label}: unknown source ref')
        return set(values) & set(by_id)

    block_map, synthesis, referenced = {}, [], set()
    for block in blocks:
        if not check(isinstance(block, dict), 'Block must be object'):
            continue
        bid = block.get('id')
        required(block, ['id', 'title'], 'block')
        if not isinstance(bid, str):
            continue
        check(bid.startswith(site + ':'), f'{bid}: ID must be site-namespaced')
        check(bid not in block_map and bid not in by_id, f'Duplicate/conflicting block ID: {bid}')
        block_map[bid] = block
        referenced_here = refs(block, bid)
        check(block.get('kind') in {'source', 'synthesis'}, f'{bid}: invalid kind')
        if block.get('kind') == 'source':
            check(bool(referenced_here), f'{bid}: source block needs source refs')
            referenced |= referenced_here
        if block.get('kind') == 'synthesis':
            synthesis.append(block)
            required(block, ['content', 'card_type'], bid)
            check(block.get('authored') is True, f'{bid}: synthesis must be explicitly authored')
            if block.get('card_type') == 'direction':
                check(len({by_id[s]['work_id'] for s in referenced_here}) >= 5, f'{bid}: direction needs five works')
                check(sum(by_id[s].get('locality') in {'local', 'adjacent'} for s in referenced_here) >= 3,
                      f'{bid}: direction needs three local/adjacent sources')
                moves = block.get('moves', [])
                check(isinstance(moves, list) and len(moves) >= 3 and all(text(m) for m in moves), f'{bid}: three moves required')
                required(block, ['tradeoff'], bid)
    check(referenced == set(by_id), 'Every source must have a source display block')
    check(Counter(s.get('card_type') for s in synthesis) == Counter(orientation=1, dna=1, palette=1, direction=4, avoidances=1),
          'Exactly eight synthesis cards required: orientation, dna, palette, four directions, avoidances')
    order = board.get('display_order', [])
    order_valid = isinstance(order, list) and all(isinstance(i, str) for i in order)
    check(order_valid and len(order) == len(block_map) and len(set(order)) == len(order) and set(order) == set(block_map),
          'display_order must contain every block exactly once')
    if order_valid and order:
        check(block_map.get(order[0], {}).get('card_type') == 'orientation', 'Orientation must open the board')
        opening = order[1:1 + thresholds['opening_visuals']]
        opening_refs = set()
        for bid in opening:
            block = block_map.get(bid, {})
            ids = refs(block, bid)
            check(block.get('kind') == 'source' and bool(ids & visual), f'{bid}: opening block needs inspected visual source')
            opening_refs |= ids & visual
        check(len(opening) == thresholds['opening_visuals'] and len(opening_refs) >= thresholds['opening_visuals'],
              'Opening needs distinct inspected visuals')
    connections = board.get('connections', [])
    if check(isinstance(connections, list) and len(connections) >= 5, 'Five connections required'):
        for connection in connections:
            if check(isinstance(connection, dict), 'Connection must be object'):
                check(len(refs(connection, 'connection')) >= 2, 'Connection needs at least two source refs')
                required(connection, ['claim'], 'connection')
    counts.update(blocks=len(blocks), synthesis=len(synthesis))
    for relative in ['sources/credits.md', 'boards/curator-brief.md', 'boards/direction-opportunities.md',
                     'boards/qa-report.md', 'provenance/research-log.md', 'provenance/arena-publication.json']:
        check((root / relative).is_file(), f'Missing package file: {relative}')
    brief = root / 'boards/curator-brief.md'
    if brief.is_file():
        check(500 <= len(brief.read_text().split()) <= 800, 'Curator brief must contain 500–800 words')
    if published:
        publication(root, read, check, url, block_map, order if order_valid else [])
    return {'ok': not errors, 'counts': counts, 'thresholds': thresholds, 'errors': errors,
            'limits': 'Counts and inspection/rights fields are declarations, not proof of evidence, visual, or rights quality. No live network or browser verification.'}


def publication(root, read, check, url, block_map, order):
    journal = read('provenance/arena-publication.json')
    snapshot = read('boards/arena-snapshot.json')
    if not check(isinstance(journal, dict) and isinstance(snapshot, dict), 'Publication files must be objects'):
        return
    check(bool(journal.get('channel_id')) and str(journal.get('channel_id')) == str(snapshot.get('channel_id')), 'Channel IDs must match')
    url(journal.get('url'), 'Channel URL')
    check(journal.get('visibility') in {'private', 'closed', 'public'} and journal.get('visibility') == snapshot.get('visibility'), 'Visibility must match')
    check(journal.get('status') == 'complete' and journal.get('failures') == [], 'Publication incomplete or failures unresolved')
    check(snapshot.get('complete') is True, 'Snapshot incomplete')
    entries, native, pages = snapshot.get('blocks', []), snapshot.get('native_order', []), snapshot.get('pages', [])
    if not check(all(isinstance(v, list) for v in [entries, native, pages]), 'Snapshot arrays required'):
        return
    actual = {str(e.get('id')): e.get('state') for e in entries if isinstance(e, dict)}
    native = [str(i) for i in native]
    check(len(actual) == len(entries) == len(native) == len(set(native)) and set(actual) == set(native), 'Snapshot ID membership/order mismatch')
    check(type(snapshot.get('total')) is int and snapshot['total'] == len(entries), 'Snapshot reported total mismatch')
    check(bool(pages), 'Snapshot pages must not be empty')
    page_ids = []
    for index, page in enumerate(pages):
        if not check(isinstance(page, dict), 'Snapshot page must be object'):
            continue
        check(page.get('page') == index + 1, 'Missing or unordered snapshot page')
        expected = index + 2 if index + 1 < len(pages) else None
        check('next_page' in page and page['next_page'] == expected, 'Snapshot continuation mismatch')
        ids = page.get('block_ids', [])
        if check(isinstance(ids, list), 'Page block_ids array required'):
            page_ids.extend(str(i) for i in ids)
    check(page_ids == native, 'Pages do not establish complete native order')
    mappings = journal.get('blocks', [])
    if not check(isinstance(mappings, list), 'Journal blocks must be array'):
        return
    managed = {}
    for entry in mappings:
        if not check(isinstance(entry, dict), 'Journal mapping must be object'):
            continue
        local, remote = entry.get('local_block_id'), entry.get('arena_block_id')
        if not check(isinstance(local, str) and remote is not None, 'Journal mapping lacks IDs'):
            continue
        check(local not in managed, f'Duplicate journal local ID: {local}')
        managed[local] = str(remote)
    check(set(block_map) <= set(managed), 'Journal missing managed block')
    selected = [managed[i] for i in order if i in managed]
    check(len(set(selected)) == len(selected), 'Different managed blocks share one Are.na ID')
    check(all(actual.get(i) == 'available' for i in selected), 'Managed block missing or unavailable in snapshot')
    check([i for i in native if i in set(selected)] == selected, 'Published curated order differs from display_order')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='Explicit casework directory')
    parser.add_argument('--published', action='store_true', help='Also check saved journal and complete snapshot')
    args = parser.parse_args()
    try:
        result = audit(args.root.resolve(), args.published)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {'ok': False, 'errors': [f'Malformed package: {exc}']}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
