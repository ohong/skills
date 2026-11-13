#!/usr/bin/env python3
"""Link canonical skills globally or into a project. Inspect with --dry-run first."""
import argparse
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--include-local', action='store_true', help='Also install ignored catalog.local.json entries')
    parser.add_argument('--target', type=Path, help='Project root; omit for global installation')
    parser.add_argument('--only', help='Comma-separated skill names; omit to install all standalone skills')
    parser.add_argument('--agents', default='agents,claude', help='Comma-separated agents, claude, codex')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    root = args.repo.expanduser().resolve()
    catalog = json.loads((root / 'catalog.json').read_text())['skills']
    if args.include_local:
        local = root / 'catalog.local.json'
        if local.is_file():
            catalog += json.loads(local.read_text())['skills']
    names = [item['name'] for item in catalog]
    if len(names) != len(set(names)):
        parser.error('Duplicate skill names in catalogs')
    selected = set(args.only.split(',')) if args.only else None
    unknown = selected - {item['name'] for item in catalog} if selected else set()
    if unknown:
        parser.error('Unknown skills: ' + ', '.join(sorted(unknown)))
    agents = args.agents.split(',')
    if any(agent not in ('agents', 'claude', 'codex') for agent in agents):
        parser.error('--agents accepts agents,claude,codex')
    target = args.target.expanduser().resolve() if args.target else Path.home()
    plan, conflicts = [], []
    for item in catalog:
        if selected is not None and item['name'] not in selected:
            continue
        if item['installation'] == 'plugin':
            print(f"PLUGIN {item['name']}: use its marketplace plugin")
            continue
        source = root / item['path']
        if not (source / 'SKILL.md').is_file():
            parser.error(f'Missing canonical skill: {source}')
        for agent in agents:
            destination = target / f'.{agent}' / 'skills' / item['name']
            if destination.is_symlink() and destination.resolve() == source.resolve():
                continue
            if destination.exists() or destination.is_symlink():
                conflicts.append(str(destination))
            else:
                plan.append((source, destination))
    # Validate every destination before changing any consumer.
    if conflicts:
        parser.error('Existing installations need explicit reconciliation:\n' + '\n'.join(conflicts))
    for source, destination in plan:
        print(f'LINK {destination} -> {source}')
        if not args.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(os.path.relpath(source, destination.parent), target_is_directory=True)
    print(f'{len(plan)} links ' + ('planned' if args.dry_run else 'created'))


if __name__ == '__main__':
    main()
