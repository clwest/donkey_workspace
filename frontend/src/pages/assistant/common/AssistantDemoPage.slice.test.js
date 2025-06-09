import fs from 'fs';
import path from 'path';

const file = path.resolve(path.dirname(new URL(import.meta.url).pathname), 'AssistantDemoPage.jsx');
const src = fs.readFileSync(file, 'utf8');
if (!src.includes('(successes || []).slice(0, 3)') && !src.includes('topDemos')) {
  throw new Error('slice fallback missing');
}
console.log('AssistantDemoPage slice test passed');

