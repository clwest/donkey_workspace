import fs from 'fs';
import { parseAppSource, normalizeRoutePath } from './appRouteScanner.js';

const src = fs.readFileSync(new URL('../App.jsx', import.meta.url), 'utf8');
const routes = parseAppSource(src);
const hasReflect = routes.some(r => r.path.includes('/assistants/:slug/reflect_on_self'));
if (!hasReflect) {
  throw new Error('reflect_on_self route missing');
}
const hasInsights = routes.some(r => r.path.includes('/assistants/:slug/insights'));
if (!hasInsights) {
  throw new Error('insights route missing');
}
const norm = normalizeRoutePath('/assistants/:slug/reflect_on_self');
if (norm !== 'api/assistants/<slug>/reflect_on_self/') {
  throw new Error('normalize failed');
}
const norm2 = normalizeRoutePath('/assistants/:slug/insights/');
if (norm2 !== 'api/assistants/<slug>/insights/') {
  throw new Error('normalize insights failed');
}
console.log('appRouteScanner test passed');
