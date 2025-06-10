import fs from 'fs';
const src = fs.readFileSync(new URL('./ChatWithAssistantPage.jsx', import.meta.url), 'utf8');
if (!src.includes('Reset Demo')) {
  throw new Error('Reset Demo button missing');
}
if (!src.includes('Create Your Own')) {
  throw new Error('Create Your Own link missing');
}
if (!src.includes("demo assistant")) {
  throw new Error('Demo helper text missing');
}
if (!src.includes('identityLoaded')) {
  throw new Error('Identity loading guard missing');
}
console.log('ChatWithAssistantPage test passed');
