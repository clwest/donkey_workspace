import fs from 'fs';
const src = fs.readFileSync(new URL('./assistants.js', import.meta.url), 'utf8');
if (!/resetDemoAssistant\([\s\S]*allowUnauthenticated:\s*true/.test(src)) {
  throw new Error('resetDemoAssistant missing allowUnauthenticated');
}
console.log('resetDemoAssistant auth test passed');
