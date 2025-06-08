import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { renderToStaticMarkup } from 'react-dom/server';
import LoginPage from '../pages/auth/LoginPage.jsx';

global.fetch = () => { throw new Error('fetch called'); };

renderToStaticMarkup(
  <MemoryRouter>
    <LoginPage />
  </MemoryRouter>
);
console.log('useAuthGuard no token test passed');
