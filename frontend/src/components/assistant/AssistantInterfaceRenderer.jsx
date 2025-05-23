import React, { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import VisualArchetypeCard from "../swarm/VisualArchetypeCard";
import CodexAnchorPanel from "../swarm/CodexAnchorPanel";
import RitualLaunchpadPanel from "../swarm/RitualLaunchpadPanel";
import BeliefEvolutionDashboard from "./analysis/BeliefEvolutionDashboard";
import DreamframeViewer from "../swarm/DreamframeViewer";

export default function AssistantInterfaceRenderer({ assistantId, showDreams = false }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!assistantId) return;
    async function load() {
      try {
        const res = await apiFetch(`/assistants/${assistantId}/interface/`);
        setData(res);
      } catch (err) {
        console.error("Failed to load interface", err);
        setData(null);
      }
    }
    load();
  }, [assistantId]);

  if (!data) {
    return <div>Loading interface...</div>;
  }

  return (
    <div className="container my-4">
      <VisualArchetypeCard assistantId={assistantId} />
      <div className="row mt-3">
        <div className="col-md-6 mb-3">
          <CodexAnchorPanel assistantId={assistantId} />
        </div>
        <div className="col-md-6 mb-3">
          <RitualLaunchpadPanel assistantId={assistantId} />
        </div>
      </div>
      <BeliefEvolutionDashboard assistantId={assistantId} />
      {showDreams && (
        <div className="mt-3">
          <DreamframeViewer assistantId={assistantId} />
        </div>
      )}
    </div>
  );
}
