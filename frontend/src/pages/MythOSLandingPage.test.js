import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { renderToStaticMarkup } from 'react-dom/server';
import MythOSLandingPage from './MythOSLandingPage.jsx';

const html = renderToStaticMarkup(
  <MemoryRouter>
    <MythOSLandingPage />
  </MemoryRouter>
);
if (!html.includes('Welcome to MythOS')) {
  throw new Error('Landing page render failed');
}
console.log('MythOSLandingPage test passed');
