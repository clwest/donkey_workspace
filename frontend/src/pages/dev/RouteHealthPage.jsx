import React, { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { routeMap } from "../../data/routeMap";
import appSource from "../../App.jsx?raw";

function extractPaths(src) {
  const regex = /path="([^"]+)"/g;
  const paths = [];
  let match;
  while ((match = regex.exec(src))) {
    paths.push(match[1]);
  }
  return paths;
}

export default function RouteHealthPage() {
  const [query, setQuery] = useState("");

  const registeredPaths = useMemo(() => extractPaths(appSource), []);

  const filtered = routeMap.filter((row) =>
    row.frontend.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="container mt-4">
      <h2 className="mb-3">🛣 Route Health</h2>
      <input
        type="text"
        className="form-control mb-3"
        placeholder="Search routes"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <table className="table table-bordered table-hover">
        <thead className="table-light">
          <tr>
            <th>Frontend Path</th>
            <th>Backend URL</th>
            <th>Status</th>
            <th>View</th>
            <th>Serializer</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((row, idx) => {
            const active = registeredPaths.includes(row.frontend);
            const statusIcon = active ? "✅" : "❌";
            return (
              <tr key={idx}>
                <td>
                  <Link to={row.frontend}>{row.frontend}</Link>
                </td>
                <td><code>{row.backend}</code></td>
                <td>{statusIcon}</td>
                <td>{row.view}</td>
                <td>{row.serializer}</td>
                <td>{row.notes}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="text-muted">
        ✅ = Route registered in <code>App.jsx</code>; ❌ = missing or placeholder.
      </p>
    </div>
  );
}
