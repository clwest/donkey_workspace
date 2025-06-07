import apiFetch from './apiClient.js';

// Mock browser globals
global.window = {
  location: { origin: 'http://test', pathname: '/', search: '' }
};

// Simple localStorage mock
global.localStorage = {
  store: {},
  setItem(k,v){ this.store[k]=v; },
  getItem(k){ return this.store[k]; },
  removeItem(k){ delete this.store[k]; }
};

// Toast mock
global.toast = { warning: () => {} };

process.env.VITE_API_URL = 'http://test/api';
localStorage.setItem('access','a1');
localStorage.setItem('refresh','r1');

const requests = [];
let refreshCount = 0;

global.fetch = async (url, opts) => {
  requests.push(url);
  if (url.endsWith('/token/refresh/')) {
    refreshCount++;
    return { ok: true, status: 200, json: async () => ({ access: 'a2', refresh: 'r2' }) };
  }
  const callNum = requests.filter(u => !u.endsWith('/token/refresh/')).length;
  if (callNum <= 2) {
    return { ok: false, status: 401, json: async () => ({}) };
  }
  return { ok: true, status: 200, json: async () => ({ ok: true }) };
};

await Promise.all([
  apiFetch('/data1'),
  apiFetch('/data2')
]);

if (refreshCount !== 1) {
  throw new Error(`expected 1 refresh request, got ${refreshCount}`);
}

console.log('apiClient refresh lock test passed');
