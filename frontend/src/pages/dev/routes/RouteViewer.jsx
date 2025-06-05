import React, { useState, useMemo } from 'react';
import useApi from '@/hooks/useApi';
import appSource from '@/App.jsx?raw';

function parseFrontendPaths(src) {
  const regex = /<Route[^>]+path="([^"]+)"/g;
  const paths = [];
  let match;
  while ((match = regex.exec(src))) {
    paths.push(match[1]);
  }
  return paths;
}

function normalize(path) {
  return path
    .replace(/^\/?|\/$/g, '')
    .replace(/<[^>]+>/g, ':param')
    .replace(/:[^/]+/g, ':param');
}

export default function RouteViewer() {
  const { data } = useApi('/dev/routes/fullmap/');
  const [filter, setFilter] = useState('all');
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(0);
  const frontendSet = useMemo(() => new Set(parseFrontendPaths(appSource).map(normalize)), []);

  if (!data) return <div className="p-4">Loading...</div>;

  const allRoutes = (data.routes || []).map((r) => ({ ...r, normalized: normalize(r.path) }));

  let filtered = allRoutes.filter((r) => {
    if (filter === 'working' && r.error) return false;
    if (filter === 'broken' && !r.error) return false;
    if (filter === 'missing-name' && r.name) return false;
    if (filter === 'diagnostic' && !r.capability) return false;
    return r.path.toLowerCase().includes(query.toLowerCase());
  });

  const pageSize = 50;
  const pageCount = Math.ceil(filtered.length / pageSize);
  filtered = filtered.slice(page * pageSize, page * pageSize + pageSize);

  const copyPath = (p) => {
    navigator.clipboard.writeText(p);
    alert('Copied!');
  };

  const handleLink = (p, isFrontend) => {
    const url = isFrontend ? `http://localhost:5173/${p}` : `http://localhost:8000/${p}`;
    window.open(url, '_blank');
  };

  return (
    <div className="container mt-4">
      <h2 className="mb-3">Route Health</h2>
      <div className="mb-3 d-flex align-items-center">
        <input
          type="text"
          className="form-control me-3"
          placeholder="Search"
          style={{ maxWidth: '300px' }}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setPage(0);
          }}
        />
        <div className="btn-group" role="group">
          <button className="btn btn-sm btn-outline-secondary" onClick={() => setFilter('all')}>All</button>
          <button className="btn btn-sm btn-outline-success" onClick={() => setFilter('working')}>✅</button>
          <button className="btn btn-sm btn-outline-danger" onClick={() => setFilter('broken')}>❌</button>
          <button className="btn btn-sm btn-outline-warning" onClick={() => setFilter('missing-name')}>⚠️</button>
          <button className="btn btn-sm btn-outline-info" onClick={() => setFilter('diagnostic')}>🧪</button>
        </div>
      </div>
      <table className="table table-bordered table-hover">
        <thead className="table-light">
          <tr>
            <th>Path</th>
            <th>Status</th>
            <th>Frontend</th>
            <th>View</th>
            <th>Module</th>
            <th>Name</th>
            <th>Capability</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((route, idx) => {
            const isFrontend = frontendSet.has(route.normalized);
            let status = '✅';
            if (route.error) status = '❌';
            else if (!route.view) status = '⁉️';
            return (
              <tr key={route.path + '-' + idx} title={route.error || ''}>
                <td>
                  <code>{route.path}</code>
                  <button
                    className="btn btn-sm btn-outline-secondary ms-2"
                    onClick={() => handleLink(route.path, isFrontend)}
                  >
                    🔗
                  </button>
                  <button
                    className="btn btn-sm btn-outline-secondary ms-1"
                    onClick={() => copyPath(route.path)}
                  >
                    📋
                  </button>
                </td>
                <td>{status}</td>
                <td>{isFrontend ? '✅' : '❌'}</td>
                <td>{route.view || '-'}</td>
                <td>{route.module || '-'}</td>
                <td>{route.name || '-'}</td>
                <td>{route.capability || ''}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <div className="d-flex justify-content-between mt-3">
        <div>
          Page {page + 1} of {pageCount || 1}
        </div>
        <div>
          <button
            className="btn btn-sm btn-outline-secondary me-2"
            disabled={page === 0}
            onClick={() => setPage((p) => Math.max(p - 1, 0))}
          >
            Prev
          </button>
          <button
            className="btn btn-sm btn-outline-secondary"
            disabled={page + 1 >= pageCount}
            onClick={() => setPage((p) => Math.min(p + 1, pageCount - 1))}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
