import fs from 'fs';
import glob from 'glob';
import { parseAppSource } from './appRouteScanner.js';

const src = fs.readFileSync(new URL('../App.jsx', import.meta.url), 'utf8');
const routes = parseAppSource(src);
const used = new Set(routes.map(r => r.file));
const pages = glob.sync('frontend/src/pages/**/*.jsx');
const orphans = pages.filter(p => !used.has(p.split('/pages/')[1]));
if (orphans.length === 0) {
  throw new Error('no orphaned pages detected');
}
console.log('orphanedPages test passed');
