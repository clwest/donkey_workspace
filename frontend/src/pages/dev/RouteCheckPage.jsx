import React, { useEffect, useMemo, useState } from "react";
import appSource from "../../App.jsx?raw";
import apiFetch from "../../utils/apiClient";
import { routeMap } from "../../data/routeMap";

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
  const [backendRoutes, setBackendRoutes] = useState([]);
  const [gitMeta, setGitMeta] = useState({});

  useEffect(() => {
    const loadBackendRoutes = async () => {
      try {
        const res = await apiFetch("/routes/");
        const unique = Array.from(new Set(res.routes || [])).map((r) =>
          r.startsWith("/") ? r : `/${r}`
        );
        setBackendRoutes(unique);
      } catch (err) {
        console.error("Failed to fetch backend routes", err);
      }
    };
    loadBackendRoutes();

    fetch("/static/git-meta.json")
      .then((r) => (r.ok ? r.json() : {}))
      .then((data) => setGitMeta(data))
      .catch(() => {});

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

  const report = useMemo(() => {
    const valid_routes = [];
    const missing_components = [];
    const broken_imports = [];
    const backendMap = Object.fromEntries(
      routeMap.map((r) => [r.frontend, r.backend])
    );
    routes.forEach((r) => {
      const stat = status[r.path];
      if (stat === "✅") {
        valid_routes.push(r.path);
      } else if (stat === "❌") {
        if (!r.modulePath) missing_components.push(r.path);
        else broken_imports.push(r.path);
      }
    });
    const undefined_backends = routeMap
      .filter((m) => backendRoutes.length > 0 && !backendRoutes.includes(m.backend))
      .map((m) => m.backend);
    const api_only = backendRoutes.filter(
      (br) => !routeMap.some((r) => r.backend === br)
    );
    return { valid_routes, missing_components, broken_imports, undefined_backends, api_only };
  }, [routes, status, backendRoutes]);

  const downloadReport = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "route-health-report.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2 className="m-0">Route Check</h2>
        <button className="btn btn-sm btn-outline-secondary" onClick={downloadReport}>
          📥 Download Report
        </button>
      </div>
      <table className="table table-bordered table-hover">
        <thead className="table-light">
          <tr>
            <th>Path</th>
            <th>Component</th>
            <th>Status</th>
            <th>Backend</th>
          </tr>
        </thead>
        <tbody>
          {routes.map((r, idx) => {
            const mapping = routeMap.find((m) => m.frontend === r.path);
            const backend = mapping ? mapping.backend : "";
            const backendOk = backend ? backendRoutes.includes(backend) : false;
            const rowClass =
              status[r.path] === "✅" && backendOk
                ? ""
                : status[r.path] === "✅"
                ? "table-warning"
                : "table-danger";
            return (
              <tr key={idx} className={rowClass}>
                <td>{r.path}</td>
                <td title={gitMeta[r.modulePath + ".jsx"] || ""}>{r.comp}</td>
                <td>{status[r.path] || "⌛"}</td>
                <td>{backend || ""}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="text-muted">
        <span className="table-danger me-2">&nbsp;&nbsp;&nbsp;</span>
        Broken or missing component.
        <span className="table-warning ms-3 me-2">&nbsp;&nbsp;&nbsp;</span>
        Backend mismatch
      </p>
      {backendRoutes.length > 0 && (
        <div className="mt-4">
          <h4>API-only Endpoints</h4>
          <ul className="list-group">
            {report.api_only.map((br, idx) => (
              <li key={br + '-' + idx} className="list-group-item">
                <code>{br}</code>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
