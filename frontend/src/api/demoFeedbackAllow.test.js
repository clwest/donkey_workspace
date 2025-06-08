import fs from 'fs';
const src = fs.readFileSync(new URL('./assistants.js', import.meta.url), 'utf8');
if (!/sendDemoFeedback\([\s\S]*allowUnauthenticated:\s*true/.test(src)) {
  throw new Error('sendDemoFeedback missing allowUnauthenticated');
}
console.log('sendDemoFeedback auth test passed');
