import React from "react";
import { routeMap } from "../data/routeMap";

export default function RouteMapTable() {
  return (
    <div className="container mt-4">
      <h2 className="mb-4">📊 Frontend ↔ Backend Route Map</h2>
      <table className="table table-bordered table-hover">
        <thead className="table-light">
          <tr>
            <th>Frontend Path</th>
            <th>Backend URL</th>
            <th>View</th>
            <th>Serializer</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {routeMap.map((row, idx) => (
            <tr key={idx}>
              <td><code>{row.frontend}</code></td>
              <td><code>{row.backend}</code></td>
              <td>{row.view}</td>
              <td>{row.serializer}</td>
              <td>{row.notes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
