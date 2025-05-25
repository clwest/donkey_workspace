import { useState } from "react";
import WorkflowDesigner from "./WorkflowDesigner";
import WorkflowExecutionLog from "./WorkflowExecutionLog";
import apiFetch from "../utils/apiClient";

export default function WorkflowOrchestrator() {
  const [definition, setDefinition] = useState(null);
  const [log, setLog] = useState(null);

  const saveDefinition = (data) => {
    apiFetch(`/workflows/definitions/`, {
      method: "POST",
      body: data,
    }).then((d) => setDefinition(d));
  };

  const execute = () => {
    if (!definition) return;
    apiFetch(`/workflows/execute/`, {
      method: "POST",
      body: {
        workflow_definition_id: definition.id,
        triggered_by_id: definition.created_by,
      },
    }).then(() => {
      apiFetch(`/execution-logs/`).then((logs) => setLog(logs[0] || null));
    });
  };

  return (
    <div className="p-2 border rounded">
      <WorkflowDesigner onSave={saveDefinition} />
      <button className="btn btn-primary mt-2" onClick={execute}>
        Run Workflow
      </button>
      <WorkflowExecutionLog log={log?.outcome_summary} />
    </div>
  );
}
