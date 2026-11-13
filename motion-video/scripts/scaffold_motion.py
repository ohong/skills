#!/usr/bin/env python3
"""Create an isolated, pinned Remotion mechanics project. Never installs dependencies."""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys


ROOT = '''import React from 'react';
import {AbsoluteFill, Composition, useCurrentFrame, useVideoConfig} from 'remotion';
import {CameraLayer, DrawPath, MaskedText, MorphFrame, Shutter, bezier,
  cameraForRect, mixCamera, mixRect, progress, seconds, worldToScreen} from './motion-kit';

const move = {start: 1, end: 1.6};
const ease = bezier(0.65, 0, 0.25, 1);
const source = {x: 0, y: 0, width: 1000, height: 380};
const viewport = {x: 80, y: 200, width: 1760, height: 480};
const wide = cameraForRect(source, viewport);
const close = cameraForRect({x: 700, y: 120, width: 280, height: 160}, viewport);
const target = {x: 820, y: 200};

export const MechanicsDiagnostic = () => {
  const {fps} = useVideoConfig();
  const time = seconds(useCurrentFrame(), fps);
  return <AbsoluteFill style={{background: '#e8e8e8', fontFamily: 'sans-serif', color: '#181818'}}>
    <div style={{position: 'absolute', left: 80, top: 55, fontSize: 42}}>MOTION KIT / MECHANICS DIAGNOSTIC</div>
    <div style={{position: 'absolute', left: 80, top: 115, fontSize: 26}}>Synthetic geometry. Camera: hold 0–1s · move 1–1.6s · hold 1.6–3s</div>
    <div style={{position: 'absolute', inset: 0, clipPath: 'inset(200px 80px 400px 80px)'}}>
      <Shutter time={time} fps={fps} moving={[move]}>
        {(sampleTime) => {
          // Every descendant motion derives from sampleTime, never the outer time.
          const p = progress(sampleTime, move, ease);
          const camera = mixCamera(wide, close, p);
          const cursor = worldToScreen(target, camera);
          return <>
            <CameraLayer camera={camera}>
              <div style={{position: 'absolute', width: 1000, height: 380, background: '#fff', border: '2px solid #181818', boxSizing: 'border-box'}}>
                <div style={{position: 'absolute', left: 40, top: 35, fontSize: 30}}>WORLD: 1000 × 380</div>
                <div style={{position: 'absolute', left: 700, top: 140, width: 240, height: 120, borderRadius: 16, background: '#333'}} />
                <div style={{position: 'absolute', left: 735, top: 180, color: '#fff', fontSize: 24}}>TARGET 820,200</div>
              </div>
            </CameraLayer>
            <div style={{position: 'absolute', left: cursor.x - 15, top: cursor.y - 15, width: 30, height: 30, border: '3px solid #e05522', borderRadius: '50%', boxSizing: 'border-box'}} />
          </>;
        }}
      </Shutter>
    </div>
    <div style={{position: 'absolute', left: 80, top: 720, fontSize: 26}}>Persistent container</div>
    <MorphFrame rect={mixRect({x: 80, y: 780, width: 80, height: 80, radius: 40},
      {x: 80, y: 780, width: 440, height: 210, radius: 20}, progress(time, move, ease))}
      style={{background: '#444'}} />
    <MaskedText progress={progress(time, move, ease)} style={{position: 'absolute', left: 620, top: 790, fontSize: 40, lineHeight: 1.3}}>Masked line reveal</MaskedText>
    <svg width={600} height={170} style={{position: 'absolute', left: 1210, top: 780}}>
      <DrawPath d="M 20 100 C 150 100 150 30 290 30 S 450 130 570 100" progress={progress(time, move)} stroke="#aaa"
        pulse={progress(time, {start: 1.6, end: 2.6})} pulseColor="#222" strokeWidth={7} />
    </svg>
  </AbsoluteFill>;
};

export const Root = () => <Composition id="MechanicsDiagnostic" component={MechanicsDiagnostic}
  durationInFrames={90} fps={30} width={1920} height={1080} />;
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path, help='New output directory; must not exist')
    parser.add_argument('--remotion-version', required=True, help='Exact 4.x release, for example 4.0.520')
    args = parser.parse_args()
    if not re.fullmatch(r'4\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', args.remotion_version):
        parser.error('--remotion-version must be an exact 4.x version, without a range')
    destination = args.destination.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        parser.error(f'destination already exists: {destination}')
    kit = Path(__file__).resolve().parents[1] / 'assets' / 'motion-kit'
    if not (kit / 'index.ts').is_file():
        parser.error(f'motion kit is missing: {kit}')
    try:
        destination.mkdir(parents=True, exist_ok=False)
        (destination / 'src').mkdir()
        (destination / 'public').mkdir()
        shutil.copytree(kit, destination / 'src' / 'motion-kit')
        package = {
            'name': 'motion-mechanics-project', 'version': '0.0.0', 'private': True, 'type': 'module',
            'scripts': {'studio': 'remotion studio src/index.ts --no-open',
                        'typecheck': 'tsc --noEmit',
                        'still': 'remotion still src/index.ts MechanicsDiagnostic',
                        'render:diagnostic': 'remotion render src/index.ts MechanicsDiagnostic renders/mechanics.mp4 --muted'},
            'dependencies': {'@remotion/cli': args.remotion_version, 'remotion': args.remotion_version,
                             'react': '19.2.0', 'react-dom': '19.2.0'},
            'devDependencies': {'typescript': '5.9.3', '@types/react': '19.2.14', '@types/react-dom': '19.2.3'},
        }
        (destination / 'package.json').write_text(json.dumps(package, indent=2) + '\n')
        (destination / 'tsconfig.json').write_text(json.dumps({'compilerOptions': {
            'target': 'ES2020', 'module': 'ESNext', 'jsx': 'react-jsx', 'moduleResolution': 'Bundler',
            'strict': True, 'esModuleInterop': True, 'skipLibCheck': True, 'noEmit': True,
            'lib': ['ES2020', 'DOM']}, 'include': ['src']}, indent=2) + '\n')
        (destination / 'src' / 'index.ts').write_text("import {registerRoot} from 'remotion';\nimport {Root} from './Root';\nregisterRoot(Root);\n")
        (destination / 'src' / 'Root.tsx').write_text(ROOT)
        (destination / '.gitignore').write_text('node_modules/\nrenders/\n.remotion/\n')
    except OSError as error:
        print(f'Could not complete scaffold: {error}. Inspect partial output at {destination}.', file=sys.stderr)
        return 1
    print(f'Created {destination}\nNo packages installed. Run npm install in that directory, then npm run typecheck.\nKeep the generated lockfile. Replace the diagnostic with your directed film.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
