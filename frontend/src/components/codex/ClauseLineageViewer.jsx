import React from "react";

export default function ClauseLineageViewer({ lineage = [] }) {
  return (
    <div className="card my-3">
      <div className="card-body">
        <h6 className="card-title">Clause Lineage</h6>
        {lineage.length === 0 ? (
          <div className="text-muted">No lineage data.</div>
        ) : (
          <ul className="list-group list-group-flush">
            {lineage.map((cl, idx) => (
              <li key={idx} className="list-group-item">
                {typeof cl === "string" ? cl : JSON.stringify(cl)}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
