import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { renderToStaticMarkup } from 'react-dom/server';
import OnboardingPage from './OnboardingPage';

const html = renderToStaticMarkup(
  <MemoryRouter>
    <OnboardingPage />
  </MemoryRouter>
);
if (!html.includes('Create Your First Assistant')) {
  throw new Error('OnboardingPage render failed');
}
console.log('OnboardingPage test passed');
