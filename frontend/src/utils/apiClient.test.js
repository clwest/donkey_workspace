import apiFetch from './apiClient.js';

import { saveAuthTokens } from './auth.js';

// simple localStorage mock
global.localStorage = {
  store: {},
  setItem(k, v) { this.store[k] = v; },
  getItem(k) { return this.store[k]; },
  removeItem(k) { delete this.store[k]; },
};

let mode = 'unauth';
let fetchCount = 0;

global.fetch = async () => {
  fetchCount++;
  if (mode === 'unauth') {
    return new Response('', { status: 401 });
  }
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};

saveAuthTokens({ access: 'a', refresh: 'b' });

// first call fails and marks auth lost
await apiFetch('/test').catch(() => {});

const before = fetchCount;
try {
  await apiFetch('/test');
  throw new Error('auth not blocked');
} catch {}
if (fetchCount !== before) {
  throw new Error('fetch should not occur when auth lost');
}

saveAuthTokens({ access: 'a', refresh: 'b' });
mode = 'ok';
const data = await apiFetch('/test');
if (!data.ok) {
  throw new Error('api call failed after reset');
}
console.log('apiClient reset test passed');

