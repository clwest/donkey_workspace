import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import RouteViewer from './RouteViewer.jsx';

const html = renderToStaticMarkup(<RouteViewer />);
if (!html.includes('Frontend Linked')) {
  throw new Error('RouteViewer missing column');
}
console.log('RouteViewer test passed');
