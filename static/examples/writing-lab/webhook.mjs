import { createHmac, timingSafeEqual } from 'node:crypto';

// This public value belongs only to this synthetic fixture.
export const fixtureSecret = 'local-writing-example';
export function sign(body) {
  return createHmac('sha256', fixtureSecret).update(body).digest('hex');
}
export function verify(body, signature) {
  if (typeof signature !== 'string' || !/^[a-f0-9]{64}$/.test(signature)) return false;
  return timingSafeEqual(Buffer.from(sign(body), 'hex'), Buffer.from(signature, 'hex'));
}
