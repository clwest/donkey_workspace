export function normalizeRoutePath(path) {
  let p = path.replace(/^\//, "").replace(/\/?$/, "");
  p = p.replace(/:([A-Za-z0-9_]+)/g, '<$1>');
  if (!p.startsWith('api/')) p = 'api/' + p;
  if (!p.endsWith('/')) p += '/';
  return p;
}

export function parseAppSource(src) {
  const imports = {};
  const importRegex = /import\s+(\w+)\s+from\s+"(.+?)";/g;
  let m;
  while ((m = importRegex.exec(src))) {
    imports[m[1]] = m[2];
  }

  const routeRegex = /<Route[^>]*path="([^"]+)"[^>]*element={<(\w+)/g;
  const routes = [];
  while ((m = routeRegex.exec(src))) {
    const routePath = m[1];
    const comp = m[2];
    const filePath = imports[comp];
    let file = null;
    if (filePath) {
      const parts = filePath.split('/');
      file = parts[parts.length - 1];
      if (!file.endsWith('.jsx')) file += '.jsx';
    }
    routes.push({
      path: routePath,
      normalized: normalizeRoutePath(routePath),
      component: comp,
      file,
    });
  }
  return routes;
}
