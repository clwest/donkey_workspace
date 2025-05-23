import React, { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import DirectiveTrackerPanel from "./interface/DirectiveTrackerPanel";
import IdentityCardEditor from "./interface/IdentityCardEditor";
import RitualQuickActionsLayer from "./interface/RitualQuickActionsLayer";

export default function AssistantInterfaceFramework({ assistantId }) {
  const [data, setData] = useState(null);
  const [showEditor, setShowEditor] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch(`/assistants/${assistantId}/interface/`);
        setData(res);
      } catch (err) {
        console.error("Failed to load interface", err);
      }
    }
    if (assistantId) {
      load();
    }
  }, [assistantId]);

  if (!data) {
    return <div>Loading interface...</div>;
  }

  return (
    <div className="assistant-interface">
      <h3>{data.assistant.name}</h3>
      {data.active_playbook && (
        <p>Tone: {data.active_playbook.tone_profile}</p>
      )}
      <button
        className="btn btn-sm btn-outline-secondary mb-2"
        onClick={() => setShowEditor(true)}
      >
        Edit Identity
      </button>
      <DirectiveTrackerPanel assistantId={assistantId} />
      <IdentityCardEditor
        assistantId={assistantId}
        show={showEditor}
        onClose={() => setShowEditor(false)}
      />
      <RitualQuickActionsLayer assistantId={assistantId} />
    </div>
  );
}
