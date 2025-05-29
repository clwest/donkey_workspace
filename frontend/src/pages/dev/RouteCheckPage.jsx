import React, { useEffect, useMemo, useState } from "react";
import appSource from "../../App.jsx?raw";

function parseRoutes(src) {
  const importRegex = /import\s+(\w+)\s+from\s+"(.+?)";/g;
  const routeRegex = /<Route\s+path=\"([^\"]+)\"\s+element={<([^\s/>]+)[\s/>]/g;
  const imports = {};
  let match;
  while ((match = importRegex.exec(src))) {
    imports[match[1]] = match[2];
  }
  const routes = [];
  while ((match = routeRegex.exec(src))) {
    const path = match[1];
    const comp = match[2];
    routes.push({ path, comp, modulePath: imports[comp] });
  }
  return routes;
}

function resolvePath(p) {
  if (!p) return null;
  if (p.startsWith("./")) {
    return `../..${p.slice(1)}`;
  }
  return p;
}

export default function RouteCheckPage() {
  const routes = useMemo(() => parseRoutes(appSource), []);
  const [status, setStatus] = useState({});

  useEffect(() => {
    routes.forEach(async (r) => {
      const path = resolvePath(r.modulePath);
      if (!path) {
        setStatus((s) => ({ ...s, [r.path]: "❌" }));
        return;
      }
      try {
        const mod = await import(/* @vite-ignore */ path);
        const Component = mod.default || mod[r.comp];
        if (!Component) throw new Error("Missing export");
        React.createElement(Component, {});
        setStatus((s) => ({ ...s, [r.path]: "✅" }));
      } catch (err) {
        console.error("Route check fail", r.path, err);
        setStatus((s) => ({ ...s, [r.path]: "❌" }));
      }
    });
  }, [routes]);

  return (
    <div className="container mt-4">
      <h2 className="mb-3">Route Check</h2>
      <table className="table table-bordered table-hover">
        <thead className="table-light">
          <tr>
            <th>Path</th>
            <th>Component</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {routes.map((r, idx) => (
            <tr key={idx}>
              <td>{r.path}</td>
              <td>{r.comp}</td>
              <td>{status[r.path] || "⌛"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
