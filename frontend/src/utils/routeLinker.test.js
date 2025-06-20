import { mapFrontendLinks } from './routeLinker.js';

const backend = [
  { path: 'api/assistants/<slug>/reflect_on_self/' },
  { path: 'api/assistants/<slug>/insights/' },
  { path: 'api/foo/' }
];
const frontend = [
  { normalized: 'api/assistants/<slug>/reflect_on_self/' , file: 'Foo.jsx' },
  { normalized: 'api/assistants/<slug>/insights/' , file: 'Bar.jsx' }
];
const mapped = mapFrontendLinks(backend, frontend);
if (!mapped[0].frontend_linked) throw new Error('should link');
if (!mapped[1].frontend_linked) throw new Error('insights should link');
if (mapped[2].frontend_linked) throw new Error('should not link');
console.log('routeLinker test passed');
