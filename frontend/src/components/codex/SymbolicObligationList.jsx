import React from "react";

export default function SymbolicObligationList({ obligations = [] }) {
  return (
    <div className="card my-3">
      <div className="card-body">
        <h6 className="card-title">Symbolic Obligations</h6>
        <ul className="list-group list-group-flush">
          {obligations.map((o, idx) => (
            <li key={idx} className="list-group-item">
              {typeof o === "string" ? o : o.description || JSON.stringify(o)}
            </li>
          ))}
          {obligations.length === 0 && (
            <li className="list-group-item text-muted">No obligations.</li>
          )}
        </ul>
      </div>
    </div>
  );
}
