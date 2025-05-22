import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function TaskDelegationPanel({ assistantId }) {
  const [targetId, setTargetId] = useState("");
  const [desc, setDesc] = useState("");
  const [assignment, setAssignment] = useState(null);

  const delegateTask = async () => {
    const data = await apiFetch(`/assistants/${assistantId}/delegate-task/`, {
      method: "POST",
      body: JSON.stringify({
        target_assistant_id: targetId,
        task_description: desc,
      }),
    });
    setAssignment(data.assignment_id);
  };

  return (
    <div className="mb-3">
      <input
        className="form-control mb-2"
        placeholder="Target assistant ID"
        value={targetId}
        onChange={(e) => setTargetId(e.target.value)}
      />
      <textarea
        className="form-control mb-2"
        placeholder="Task description"
        value={desc}
        onChange={(e) => setDesc(e.target.value)}
      />
      <button className="btn btn-secondary" onClick={delegateTask}>
        Delegate Task
      </button>
      {assignment && <div className="mt-2">Assigned: {assignment}</div>}
    </div>
  );
}
