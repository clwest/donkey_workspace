import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RoleAdaptiveTaskAssignmentEngine() {
  const [taskType, setTaskType] = useState("ritual");
  const [desc, setDesc] = useState("");
  const [recommendation, setRecommendation] = useState(null);

  const handleAssign = async () => {
    try {
      const res = await apiFetch("/plan/assign/", {
        method: "POST",
        body: { task_type: taskType, description: desc },
      });
      setRecommendation(res);
    } catch (err) {
      console.error("Assignment failed", err);
    }
  };

  return (
    <div className="my-3">
      <h5>Task Assignment Engine</h5>
      <select
        className="form-select mb-2"
        value={taskType}
        onChange={(e) => setTaskType(e.target.value)}
      >
        <option value="ritual">ritual</option>
        <option value="research">research</option>
        <option value="build">build</option>
        <option value="respond">respond</option>
      </select>
      <textarea
        className="form-control mb-2"
        placeholder="Task description"
        value={desc}
        onChange={(e) => setDesc(e.target.value)}
      />
      <button className="btn btn-primary" onClick={handleAssign}>
        Assign Task
      </button>
      {recommendation && (
        <div className="mt-3">
          Recommended assistant: {recommendation.assistant_name || recommendation.assistant}
        </div>
      )}
    </div>
  );
}
