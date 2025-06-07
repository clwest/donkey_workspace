import { parseOverlayResults } from './glossary.js';

const data = {
  results: [
    { label: 'MythPath', tooltip: 'path tip', slug: 'mythpath' },
  ],
};

const parsed = parseOverlayResults(data);
if (!parsed.length || parsed[0].slug !== 'mythpath') {
  throw new Error('parseOverlayResults failed');
}
console.log('glossary hook test passed');
