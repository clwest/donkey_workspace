import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import appSource from "../../App.jsx?raw";

function parseRoutes(src) {
  const importRegex = /import\s+(\w+)\s+from\s+"(.+?)";/g;
  const routeRegex = /<Route[^>]*path=\"([^\"]+)\"[^>]*element={<(\w+)/g;
  const imports = {};
  let match;
  while ((match = importRegex.exec(src))) {
    imports[match[1]] = match[2];
  }
  const routes = [];
  while ((match = routeRegex.exec(src))) {
    const path = match[1];
    const comp = match[2];
    const modulePath = imports[comp];
    routes.push({ path, comp, modulePath });
  }
  return routes;
}

function groupByPrefix(routes) {
  const groups = {};
  routes.forEach((r) => {
    const prefix = r.modulePath
      ? r.modulePath.split("/pages/")[1].split("/")[0]
      : "unknown";
    if (!groups[prefix]) groups[prefix] = [];
    groups[prefix].push(r);
  });
  return groups;
}

export default function RouteExplorerPage() {
  const [query, setQuery] = useState("");
  const routes = useMemo(() => parseRoutes(appSource), []);
  const pageFiles = useMemo(
    () => Object.keys(import.meta.glob("../../pages/**/*.jsx")),
    []
  );
  const grouped = useMemo(() => groupByPrefix(routes), [routes]);

  const filterFn = (r) =>
    r.path.toLowerCase().includes(query.toLowerCase()) ||
    (r.modulePath || "").toLowerCase().includes(query.toLowerCase());

  const statusTag = (r) => {
    if (!r.modulePath) return "⚠ Missing View";
    if (r.path.includes("/dev") || r.path.includes("/debug")) return "🔒 Private";
    return "🟢 Connected";
  };

  const usedFiles = new Set(routes.map((r) => r.modulePath && r.modulePath.replace("./pages/", "")));
  const orphans = pageFiles
    .map((p) => p.replace("../../pages/", ""))
    .filter((p) => !usedFiles.has(p));

  return (
    <div className="container mt-4">
      <h2 className="mb-3">🗺 Route Explorer</h2>
      <input
        type="text"
        className="form-control mb-3"
        placeholder="Filter routes"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {Object.entries(grouped).map(([prefix, list]) => (
        <div key={prefix} className="mb-4">
          <h4 className="mb-2">{prefix}</h4>
          <table className="table table-bordered table-hover">
            <thead className="table-light">
              <tr>
                <th>Path</th>
                <th>Status</th>
                <th>Component</th>
                <th>Test</th>
              </tr>
            </thead>
            <tbody>
              {list.filter(filterFn).map((r, idx) => (
                <tr key={r.path + idx}>
                  <td>{r.path}</td>
                  <td>{statusTag(r)}</td>
                  <td>{r.modulePath ? r.modulePath.split("/" ).pop() : "-"}</td>
                  <td>
                    {r.modulePath && (
                      <Link
                        className="btn btn-sm btn-outline-secondary"
                        to={r.path}
                        target="_blank"
                      >
                        Test
                      </Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
      {orphans.length > 0 && (
        <div className="mt-4">
          <h4>⚫ Orphaned Pages ({orphans.length})</h4>
          <ul>
            {orphans.map((f) => (
              <li key={f}>{f}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
