import fs from 'fs';
import path from 'path';

const file = path.resolve(path.dirname(new URL(import.meta.url).pathname), 'auth.js');
const src = fs.readFileSync(file, 'utf8');

if (!/loginUser\([\s\S]*allowUnauthenticated:\s*true/.test(src)) {
  throw new Error('loginUser missing allowUnauthenticated');
}
if (!/registerUser\([\s\S]*allowUnauthenticated:\s*true/.test(src)) {
  throw new Error('registerUser missing allowUnauthenticated');
}
if (!/refreshToken\([\s\S]*allowUnauthenticated:\s*true/.test(src)) {
  throw new Error('refreshToken missing allowUnauthenticated');
}
console.log('auth 401 redirect test passed');
