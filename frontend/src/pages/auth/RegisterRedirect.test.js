import { getPostRegisterPath } from './RegisterPage.js';

if (getPostRegisterPath({ onboarding_complete: false }) !== '/onboarding/world') {
  throw new Error('register redirect failed');
}
console.log('RegisterRedirect test passed');
