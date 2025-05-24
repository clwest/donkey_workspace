import React from "react";

export default function PromptContractCard({ contract }) {
  if (!contract) return null;
  return (
    <div className="card mb-3 shadow-sm">
      <div className="card-body">
        <h5 className="card-title">{contract.prompt_title || "Prompt Contract"}</h5>
        <p className="card-text text-muted">
          Clauses: {contract.clauses ? contract.clauses.length : 0}
        </p>
        <pre className="mb-0 text-muted" style={{ whiteSpace: "pre-wrap" }}>
          {contract.summary || "Contract summary pending..."}
        </pre>
      </div>
    </div>
  );
}
