// See frontend/docs/route_sync_checklist.md step 3
import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch, { API_URL } from "../../utils/apiClient";
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

export default function RoutesDebugPage() {
  const frontendRoutes = useMemo(
    () => Array.from(new Set(extractPaths(appSource))),
    []
  );
  const [backendRoutes, setBackendRoutes] = useState([]);
  const [status, setStatus] = useState({});

  useEffect(() => {
    const loadRoutes = async () => {
      try {
        const res = await apiFetch("/routes/");
        const unique = Array.from(new Set(res.routes || []));
        setBackendRoutes(unique);
      } catch (err) {
        console.error("Failed to fetch backend routes", err);
      }
    };
    loadRoutes();
  }, []);

  const ping = async (route) => {
    const url = route.startsWith("/api")
      ? `${API_URL}${route.slice(4)}`
      : route;
    try {
      const res = await fetch(url, { credentials: "include" });
      setStatus((prev) => ({ ...prev, [route]: res.status }));
    } catch (err) {
      console.error("Ping failed", err);
      setStatus((prev) => ({ ...prev, [route]: "err" }));
    }
  };

  return (
    <div className="container mt-4">
      <h2 className="mb-3">🛣 Routes Debug</h2>
      <div className="row">
        <div className="col-md-6">
          <h4>Frontend Routes</h4>
          <ul className="list-group">
            {frontendRoutes.map((p, idx) => (
              <li key={`${p}-${idx}`} className="list-group-item">
                <Link to={p}>{p}</Link>
              </li>
            ))}
          </ul>
        </div>
        <div className="col-md-6">
          <h4>Backend Routes</h4>
          <table className="table table-bordered">
            <thead className="table-light">
              <tr>
                <th>Route</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {backendRoutes.map((r, idx) => (
                <tr key={`${r}-${idx}`}>
                  <td><code>{r}</code></td>
                  <td>{status[r] || ""}</td>
                  <td>
                    <button
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => ping(r)}
                    >
                      Ping
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

