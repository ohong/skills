# Motion mechanics

Copy this directory into an existing Remotion project's `src/`, or run the skill's `scripts/scaffold_motion.py` with `--destination` and `--remotion-version`. The scaffold creates a **mechanics diagnostic**, not a finished film. It never installs packages. Install in the new project, keep its lockfile, and replace the diagnostic with your shot design. All Remotion packages must use the same exact version. This kit uses only React and Remotion at runtime.

## One coordinate system

Use source screenshot pixels as world coordinates. Keep the screenshot, button geometry, and cursor target in that space. `cameraForRect(sourceRect, viewport = HD, fit = 'contain')` finds a uniform scale and translation. `HD` is `{x:0,y:0,width:1920,height:1080}`. Supply a different viewport for other formats. Contain preserves the entire source rectangle and may leave space; cover fills the viewport and may crop. Neither stretches the UI. The camera does not clip: put it inside a viewport mask when needed.

`CameraLayer` transforms everything inside it. A cursor placed inside scales with the UI. For a constant screen-size cursor outside the layer, map its world point using `worldToScreen(point, camera)`. Never apply both mappings.

```tsx
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {CameraLayer, Shutter, bezier, cameraForRect, mixCamera,
  progress, seconds, worldToScreen} from './motion-kit';

const move = {start: 1.2, end: 1.65};
const ease = bezier(0.7, 0, 0.2, 1);
const wide = cameraForRect({x: 0, y: 0, width: 1440, height: 900});
const detail = cameraForRect({x: 900, y: 500, width: 480, height: 270});
const buttonCenter = {x: 1170, y: 660}; // Measure from the actual capture.

export const ProofShot = () => {
  const {fps} = useVideoConfig();
  const time = seconds(useCurrentFrame(), fps);
  return <AbsoluteFill style={{background: '#fff', overflow: 'hidden'}}>
    <Shutter time={time} fps={fps} moving={[move]} samples={8}>
      {(t) => {
        const camera = mixCamera(wide, detail, progress(t, move, ease));
        const cursor = worldToScreen(buttonCenter, camera);
        return <>
          <CameraLayer camera={camera}>
            <Img src={staticFile('actual-capture.png')}
              style={{position:'absolute', width:1440, height:900}} />
          </CameraLayer>
          <div style={{position:'absolute', left:cursor.x-8, top:cursor.y-8,
            width:16, height:16, borderRadius:8, background:'#111'}} />
        </>;
      }}
    </Shutter>
  </AbsoluteFill>;
};
```

**Every animated child must compute its state from `t`, including text, cursor motion, masks, and camera movement.** A value computed from the outer `time` stays frozen across exposure samples. This render callback does not alter Remotion's frame context. Child components must accept sampled seconds as a prop; their own `useCurrentFrame()` calls will still see the composition frame. Do not place audio or frame-decoded video inside the sampler. Place audio once outside; use this sampler for deterministic graphics and still captures.

## Timing and holds

`seconds(frame, fps)` accepts fractional frames. `progress(t, {start,end}, ease?)` clamps before and after the interval, with exact endpoint holds. `bezier(x1,y1,x2,y2)` solves cubic timing, not a cubic value curve. `mix(a,b,p)` and `mixCamera(a,b,p)` clamp progress. These helpers deliberately clamp overshooting easing results; use a separate spring for a physical overshoot.

`keyframes(t, [{time,value,ease?}, ...])` uses seconds; each key controls the easing into the next key. Repeat equal values at distinct times to author a hold. Times must strictly increase. Invalid durations, coordinates, and nonpositive camera scales throw clear errors.

## Exposure sampling

`Shutter` averages complete fractional-time renders in an isolated additive group, using equal weights. This approximates temporal exposure along the actual motion path, including rotation and camera scale. A velocity-driven Gaussian filter only smears the current image; it cannot recover occluded positions or changing geometry. This kit does not use that approximation.

`moving` is a sorted list of non-overlapping `{start,end}` intervals, covering motion from every sampled child. Merge overlaps. Outside those intervals, and exactly at each boundary, the scene renders once with no averaging. Inside an interval, the exposure is centered on time and clipped to that interval. This deliberately trades a physical exposure tail for immediately crisp authored holds. `shutterAngle` defaults to 180 degrees; its exposure is `shutterAngle / 360 / fps` seconds. `samples` defaults to 8 and permits 1–64. Set the angle to 0 or samples to 1 for a crisp comparison.

This is browser sample averaging, not a linear-light film simulation. Browser precision can shift colors, especially with many low-opacity samples. Inspect opaque colors, transparent edges, and fine text in exported frames. Increase sample count only when visible gaps require it. Do not substitute ordinary stacked `opacity: 1/N` layers: alpha-over blending produces ghosted, darkened results instead of an average. Keep `isolation: isolate` and `mixBlendMode: plus-lighter` together. Each exposure multiplies rendering cost; use it during motivated movement.

Related primary documentation: [Remotion's exposure effect and color limitation](https://www.remotion.dev/docs/motion-blur/camera-motion-blur), [the child-time mistake](https://www.remotion.dev/docs/motion-blur/common-mistake).

## Carry objects, reveal type, draw connections

`mixRect(from, to, p)` interpolates `{x,y,width,height,radius}`. Feed it into one continuously mounted `MorphFrame`. That shared container can grow from a rounded object into a UI panel without changing identity. Optional `src` uses Remotion's image loader; `imageFit` is `cover`, `contain`, or `fill`. Preserve source aspect ratio unless distortion is deliberate. When child layout must remain fixed, give it explicit dimensions instead of letting it reflow during the morph.

`MaskedText` takes `progress`, `children`, optional `style`, and `distance` (percent, default 110). Give each text line a separate mask and explicit line height. It rises through a clipping boundary; it does not fade.

Place `DrawPath` inside your own SVG with a suitable viewBox. Pass `d`, `progress`, `stroke`, and optional `strokeWidth`. SVG `pathLength=1` makes draw timing independent of the path's length. Optional `pulse` (0–1), `pulseColor`, and `pulseLength` (fraction, default 0.08) send a short dash along the path. Draw the connection first, then pulse it. The same component traces an outline or a connection; the consumer owns the geometry.

These are operations, not a visual theme: fonts, palette, assets, captions, scene order, durations, and product claims remain the film's choices.
