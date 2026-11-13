import React, {type CSSProperties, type ReactNode} from 'react';
import {Img} from 'remotion';
import {validateRect, type Rect} from './camera';
import {clamp01, finite, mix} from './timing';

export type RoundedRect = Rect & Readonly<{radius: number}>;
const validateRoundedRect = (rect: RoundedRect): void => {
  validateRect(rect);
  if (finite(rect.radius, 'radius') < 0) throw new RangeError('radius must not be negative');
};
export const mixRect = (from: RoundedRect, to: RoundedRect, p: number): RoundedRect => {
  validateRoundedRect(from); validateRoundedRect(to);
  return {x: mix(from.x, to.x, p), y: mix(from.y, to.y, p), width: mix(from.width, to.width, p),
    height: mix(from.height, to.height, p), radius: mix(from.radius, to.radius, p)};
};
export type MorphFrameProps = Readonly<{
  rect: RoundedRect;
  children?: ReactNode;
  src?: string;
  imageFit?: 'cover' | 'contain' | 'fill';
  style?: CSSProperties;
}>;
/** Keep this component mounted across the match cut; change rect and content within it. */
export const MorphFrame = ({rect, children, src, imageFit = 'cover', style}: MorphFrameProps) => {
  validateRoundedRect(rect);
  return <div style={{...style, boxSizing: 'border-box', position: 'absolute', left: rect.x, top: rect.y, width: rect.width,
    height: rect.height, borderRadius: rect.radius, overflow: 'hidden'}}>
    {src && <Img src={src} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: imageFit}} />}
    {children}
  </div>;
};

export type MaskedTextProps = Readonly<{progress: number; children: ReactNode; style?: CSSProperties; distance?: number}>;
/** A line mask, not an opacity fade. Give separate lines separate masks. */
export const MaskedText = ({progress, children, style, distance = 110}: MaskedTextProps) => {
  const p = clamp01(progress); finite(distance, 'distance');
  return <div style={{...style, overflow: 'hidden'}}>
    <div style={{transform: `translateY(${(1 - p) * distance}%)`, visibility: p === 0 ? 'hidden' : 'visible'}}>{children}</div>
  </div>;
};

export type DrawPathProps = Readonly<{
  d: string;
  progress: number;
  stroke: string;
  strokeWidth?: number;
  pulse?: number;
  pulseColor?: string;
  pulseLength?: number;
}>;
/** Place inside your SVG. Works with open connection paths and closed shape outlines. */
export const DrawPath = ({d, progress, stroke, strokeWidth = 3, pulse, pulseColor = stroke, pulseLength = 0.08}: DrawPathProps) => {
  const p = clamp01(progress);
  if (finite(strokeWidth, 'strokeWidth') <= 0) throw new RangeError('strokeWidth must be positive');
  if (finite(pulseLength, 'pulseLength') <= 0 || pulseLength > 1) throw new RangeError('pulseLength must be in (0, 1]');
  const pulseProgress = pulse === undefined ? undefined : clamp01(pulse);
  return <g fill="none" strokeWidth={strokeWidth} strokeLinecap="round">
    <path d={d} pathLength={1} stroke={stroke} strokeDasharray="1 1" strokeDashoffset={1 - p} visibility={p === 0 ? 'hidden' : 'visible'} />
    {pulseProgress !== undefined && <path d={d} pathLength={1} stroke={pulseColor}
      strokeDasharray={`${pulseLength} ${1 + pulseLength}`}
      strokeDashoffset={pulseLength - (1 + pulseLength) * pulseProgress}
      visibility={pulseProgress === 0 || pulseProgress === 1 ? 'hidden' : 'visible'} />}
  </g>;
};
