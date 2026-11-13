/** All timeline values are seconds. Frame conversion happens only at the scene boundary. */
export type Ease = (progress: number) => number;
export type Interval = Readonly<{start: number; end: number}>;
export type Keyframe = Readonly<{time: number; value: number; ease?: Ease}>;

export const finite = (value: number, name: string): number => {
  if (!Number.isFinite(value)) throw new RangeError(`${name} must be finite`);
  return value;
};
export const clamp01 = (value: number): number => Math.max(0, Math.min(1, finite(value, 'progress')));
export const seconds = (frame: number, fps: number): number => {
  finite(frame, 'frame');
  if (finite(fps, 'fps') <= 0) throw new RangeError('fps must be positive');
  return frame / fps;
};
export const validateInterval = ({start, end}: Interval): void => {
  if (finite(end, 'end') <= finite(start, 'start')) throw new RangeError('end must be after start');
};
export const linear: Ease = (p) => p;

/** CSS cubic-bezier timing: solve x first, then evaluate y. No sampled lookup table. */
export const bezier = (x1: number, y1: number, x2: number, y2: number): Ease => {
  [x1, y1, x2, y2].forEach((v) => finite(v, 'bezier control'));
  if (x1 < 0 || x1 > 1 || x2 < 0 || x2 > 1) throw new RangeError('bezier x controls must be in [0, 1]');
  const curve = (t: number, a: number, b: number) => 3 * (1 - t) ** 2 * t * a + 3 * (1 - t) * t * t * b + t ** 3;
  return (value) => {
    const p = clamp01(value);
    if (p === 0 || p === 1) return p;
    let lo = 0; let hi = 1;
    for (let i = 0; i < 40; i++) {
      const mid = (lo + hi) / 2;
      if (curve(mid, x1, x2) < p) lo = mid; else hi = mid;
    }
    return curve((lo + hi) / 2, y1, y2);
  };
};

/** Exact endpoint holds, including the first frame at end. */
export const progress = (time: number, interval: Interval, ease: Ease = linear): number => {
  validateInterval(interval); finite(time, 'time');
  if (time <= interval.start) return 0;
  if (time >= interval.end) return 1;
  return clamp01(ease((time - interval.start) / (interval.end - interval.start)));
};
export const mix = (from: number, to: number, p: number): number => {
  finite(from, 'from'); finite(to, 'to');
  return from + (to - from) * clamp01(p);
};

/** Each key's ease controls its outgoing segment. Repeat values to author a hold. */
export const keyframes = (time: number, keys: readonly Keyframe[]): number => {
  finite(time, 'time');
  if (!keys.length) throw new RangeError('keyframes must not be empty');
  keys.forEach((key, i) => {
    finite(key.time, 'key time'); finite(key.value, 'key value');
    if (i && key.time <= keys[i - 1].time) throw new RangeError('key times must strictly increase');
  });
  if (time <= keys[0].time) return keys[0].value;
  for (let i = 1; i < keys.length; i++) {
    if (time <= keys[i].time) {
      const a = keys[i - 1]; const b = keys[i];
      return mix(a.value, b.value, progress(time, {start: a.time, end: b.time}, a.ease));
    }
  }
  return keys[keys.length - 1].value;
};
