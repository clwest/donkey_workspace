import fs from 'fs';
const src = fs.readFileSync(new URL('./GrowthTrackPanel.jsx', import.meta.url), 'utf8');
if (!src.includes('growthRecapSeen-')) {
  throw new Error('Growth recap localStorage key missing');
}
console.log('GrowthTrackPanel test passed');
