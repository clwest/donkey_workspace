import fs from 'fs';
const src = fs.readFileSync(new URL('./ChatWithAssistantPage.jsx', import.meta.url), 'utf8');
if (!src.includes('Reset Demo')) {
  throw new Error('Reset Demo button missing');
}
if (!src.includes("chatting with a demo assistant")) {
  throw new Error('Demo helper text missing');
}
console.log('ChatWithAssistantPage test passed');
