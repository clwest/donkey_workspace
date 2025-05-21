
import React from "react";

export default function AgentLegacyPanel({ legacy }) {
  if (!legacy) {
    return <div className="alert alert-secondary">No legacy data.</div>;
  }
  return (
    <div>
      <p>
        <strong>Resurrections:</strong> {legacy.resurrection_count}
      </p>
      <p>
        <strong>Missions Completed:</strong> {legacy.missions_completed}
      </p>
      {legacy.legacy_notes && <p>{legacy.legacy_notes}</p>}
    </div>
  );
}



