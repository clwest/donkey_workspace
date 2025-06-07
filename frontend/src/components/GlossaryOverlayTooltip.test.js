import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { renderToStaticMarkup } from 'react-dom/server';
import GlossaryOverlayTooltip from './GlossaryOverlayTooltip';

const html = renderToStaticMarkup(
  <MemoryRouter>
    <GlossaryOverlayTooltip label="MythPath" tooltip="tip" slug="mythpath" />
  </MemoryRouter>
);

if (!html.includes('MythPath') || !html.includes('More Info')) {
  throw new Error('GlossaryOverlayTooltip render failed');
}
console.log('GlossaryOverlayTooltip test passed');
