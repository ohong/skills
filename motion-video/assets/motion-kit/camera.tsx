import React, {type CSSProperties, type ReactNode} from 'react';
import {finite, mix} from './timing';

export type Point = Readonly<{x: number; y: number}>;
export type Rect = Readonly<{x: number; y: number; width: number; height: number}>;
export type Camera = Readonly<{scale: number; x: number; y: number}>;
export const HD: Rect = {x: 0, y: 0, width: 1920, height: 1080};
export const validateRect = (rect: Rect): void => {
  Object.entries(rect).forEach(([name, value]) => finite(value, name));
  if (rect.width <= 0 || rect.height <= 0) throw new RangeError('rect dimensions must be positive');
};
const validateCamera = (camera: Camera): void => {
  finite(camera.x, 'camera x'); finite(camera.y, 'camera y');
  if (finite(camera.scale, 'camera scale') <= 0) throw new RangeError('camera scale must be positive');
};

/** Uniform fit, centered in the destination viewport. Source uses capture/world pixels. */
export const cameraForRect = (source: Rect, viewport: Rect = HD, fit: 'contain' | 'cover' = 'contain'): Camera => {
  validateRect(source); validateRect(viewport);
  if (fit !== 'contain' && fit !== 'cover') throw new RangeError('fit must be contain or cover');
  const scale = Math[fit === 'contain' ? 'min' : 'max'](viewport.width / source.width, viewport.height / source.height);
  return {scale, x: viewport.x + viewport.width / 2 - (source.x + source.width / 2) * scale,
    y: viewport.y + viewport.height / 2 - (source.y + source.height / 2) * scale};
};
export const mixCamera = (from: Camera, to: Camera, p: number): Camera => {
  validateCamera(from); validateCamera(to);
  return {scale: mix(from.scale, to.scale, p), x: mix(from.x, to.x, p), y: mix(from.y, to.y, p)};
};
/** Use this for a screen-size cursor; a cursor inside CameraLayer already receives this mapping. */
export const worldToScreen = (point: Point, camera: Camera): Point => {
  validateCamera(camera); finite(point.x, 'point x'); finite(point.y, 'point y');
  return {x: point.x * camera.scale + camera.x, y: point.y * camera.scale + camera.y};
};
export const cameraStyle = (camera: Camera): CSSProperties => {
  validateCamera(camera);
  return {position: 'absolute', left: 0, top: 0, transformOrigin: '0 0',
    transform: `matrix(${camera.scale}, 0, 0, ${camera.scale}, ${camera.x}, ${camera.y})`};
};
export type CameraLayerProps = Readonly<{camera: Camera; children: ReactNode}>;
export const CameraLayer = ({camera, children}: CameraLayerProps) => <div style={cameraStyle(camera)}>{children}</div>;
