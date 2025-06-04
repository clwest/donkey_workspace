import React from 'react';
import useApi from '@/hooks/useApi';

export default function CapabilityStatus() {
  const { data } = useApi('/api/capabilities/status/simple/');

  if (!data) return <div className="p-4">Loading...</div>;

  return (
    <div className="container mt-4">
      <h2 className="mb-3">Capability Status</h2>
      <table className="table table-bordered table-hover">
        <thead className="table-light">
          <tr>
            <th>Capability</th>
            <th>Status</th>
            <th>Info</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data).map(([cap, info]) => (
            <tr key={cap}>
              <td>{cap}</td>
              <td>{info.connected ? '✅ Connected' : '❌ Missing'}</td>
              <td>{info.reason || info.view}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
