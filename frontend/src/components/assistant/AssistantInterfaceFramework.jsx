import React, { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AssistantInterfaceFramework({ assistantId }) {
  const [data, setData] = useState(null);

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
      {/* TODO: render layout_config when implemented */}
    </div>
  );
}
