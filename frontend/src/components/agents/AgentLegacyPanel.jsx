import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

const AgentLegacyPanel = ({ agentId }) => {
  const [legacy, setLegacy] = useState(null);

  useEffect(() => {
    if (!agentId) return;
    apiFetch(`/agents/${agentId}/legacy/`)
      .then(setLegacy)
      .catch((err) => console.error("Failed to load legacy", err));
  }, [agentId]);

  if (!legacy) {
    return <div className="text-muted">No legacy data.</div>;
  }

  return (
    <div>
      <h5>Agent Legacy</h5>
      <p className="mb-1">Resurrections: {legacy.resurrection_count}</p>
      <p className="mb-1">Missions Completed: {legacy.missions_completed}</p>
      {legacy.legacy_notes && <p>{legacy.legacy_notes}</p>}
    </div>
  );
};

export default AgentLegacyPanel;

