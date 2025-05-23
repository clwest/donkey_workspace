import { useState } from "react";
import WorkflowDesigner from "./WorkflowDesigner";
import WorkflowExecutionLog from "./WorkflowExecutionLog";

export default function WorkflowOrchestrator() {
  const [definition, setDefinition] = useState(null);
  const [log, setLog] = useState(null);

  const saveDefinition = (data) => {
    fetch("http://localhost:8000/api/workflows/definitions/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .then((d) => setDefinition(d));
  };

  const execute = () => {
    if (!definition) return;
    fetch("http://localhost:8000/api/workflows/execute/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        workflow_definition_id: definition.id,
        triggered_by_id: definition.created_by,
      }),
    })
      .then((res) => res.json())
      .then((d) => {
        fetch("http://localhost:8000/api/execution-logs/")
          .then((r) => r.json())
          .then((logs) => setLog(logs[0] || null));
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
