import { normalizeRoutePath } from './appRouteScanner.js';

export function mapFrontendLinks(backendRoutes, appRoutes) {
  const map = new Map(appRoutes.map(r => [r.normalized, r]));
  return backendRoutes.map(r => {
    const norm = normalizeRoutePath(r.path.startsWith('/') ? r.path : '/' + r.path);
    const match = map.get(norm);
    return { ...r, frontend_linked: !!match, component: match ? match.file : null };
  });
}
