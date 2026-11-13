import React, {type ReactNode} from 'react';
import {finite, seconds, validateInterval, type Interval} from './timing';

export type ShutterOptions = Readonly<{
  time: number;
  fps: number;
  /** Union of intervals in which any sampled child moves. Sorted, without overlap. */
  moving: readonly Interval[];
  samples?: number;
  shutterAngle?: number;
}>;

/** Midpoint integration of a centered exposure; never samples across a declared hold. */
export const shutterTimes = ({time, fps, moving, samples = 8, shutterAngle = 180}: ShutterOptions): readonly number[] => {
  finite(time, 'time'); seconds(0, fps);
  if (!Number.isInteger(samples) || samples < 1 || samples > 64) throw new RangeError('samples must be an integer in [1, 64]');
  if (finite(shutterAngle, 'shutterAngle') < 0 || shutterAngle > 360) throw new RangeError('shutterAngle must be in [0, 360]');
  moving.forEach((interval, i) => {
    validateInterval(interval);
    if (i && interval.start < moving[i - 1].end) throw new RangeError('moving intervals must be sorted and not overlap');
  });
  const active = moving.find(({start, end}) => time > start && time < end);
  if (!active || samples === 1 || shutterAngle === 0) return [time];
  const half = shutterAngle / 360 / fps / 2;
  const start = Math.max(active.start, time - half);
  const end = Math.min(active.end, time + half);
  return Array.from({length: samples}, (_, i) => start + (end - start) * (i + 0.5) / samples);
};

export type ShutterProps = ShutterOptions & Readonly<{children: (sampleTime: number) => ReactNode}>;
/** Add premultiplied samples in an isolated group, then composite the group once. */
export const Shutter = ({children, ...options}: ShutterProps) => {
  const times = shutterTimes(options);
  const fill = {position: 'absolute', inset: 0} as const;
  return <div style={{...fill, isolation: 'isolate'}}>
    {times.map((time, i) => <div key={i} style={{...fill,
      ...(times.length > 1 ? {mixBlendMode: 'plus-lighter' as const, opacity: 1 / times.length} : {})}}>
      {children(time)}
    </div>)}
  </div>;
};
