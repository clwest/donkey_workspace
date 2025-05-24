import React from "react";

export default function SymbolicChunkLogViewer({ log }) {
  if (!log || log.length === 0) return null;
  return (
    <div className="mt-3" style={{ maxHeight: "200px", overflowY: "auto" }}>
      <ul className="list-group list-group-flush">
        {log.map((msg, idx) => (
          <li key={idx} className="list-group-item p-1">
            {msg}
          </li>
        ))}
      </ul>
    </div>
  );
}
