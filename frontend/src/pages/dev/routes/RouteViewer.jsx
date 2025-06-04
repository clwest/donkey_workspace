import React, { useState } from 'react';
import useApi from '@/hooks/useApi';

export default function RouteViewer() {
  const { data } = useApi('/dev/routes/fullmap/');
  const [filter, setFilter] = useState('all');

  if (!data) return <div className="p-4">Loading...</div>;

  const routes = data.routes || [];
  const filtered = routes.filter((r) => {
    if (filter === 'working') return !r.error;
    if (filter === 'broken') return r.error;
    if (filter === 'missing-name') return !r.name;
    return true;
  });

  return (
    <div className="container mt-4">
      <h2 className="mb-3">Route Viewer</h2>
      <div className="mb-3">
        <button className="btn btn-sm btn-outline-success me-2" onClick={() => setFilter('working')}>
          ✅ Only working
        </button>
        <button className="btn btn-sm btn-outline-danger me-2" onClick={() => setFilter('broken')}>
          ❌ Show broken
        </button>
        <button className="btn btn-sm btn-outline-warning" onClick={() => setFilter('missing-name')}>
          ⚠️ Missing route name
        </button>
      </div>
      <table className="table table-bordered table-hover">
        <thead className="table-light">
          <tr>
            <th>Path</th>
            <th>View</th>
            <th>Module</th>
            <th>Name</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((route) => (
            <tr key={route.path}>
              <td><code>{route.path}</code></td>
              <td>{route.view || 'Unknown'}</td>
              <td>{route.module || '?'}</td>
              <td>{route.name || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
