import React, { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

import AssistantNotificationPanel from "./AssistantNotificationPanel";
import RitualStatusBeaconBar from "./RitualStatusBeaconBar";
import { useCodexAlert } from "../../utils/codexStateAlertSystem";


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

  const codexAlert = useCodexAlert(data.codex_state);

  return (
    <div className="assistant-interface">
      <h3>{data.assistant.name}</h3>
      {data.active_playbook && (
        <p>Tone: {data.active_playbook.tone_profile}</p>
      )}

      {codexAlert && (
        <div className={`codex-alert ${codexAlert}`}>Codex state: {codexAlert}</div>
      )}
      <RitualStatusBeaconBar assistantId={assistantId} />
      <AssistantNotificationPanel assistantId={assistantId} />
      {/* TODO: render layout_config when implemented */}

    </div>
  );
}
