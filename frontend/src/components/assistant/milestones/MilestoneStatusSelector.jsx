import { useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function MilestoneStatusSelector({ milestone, onStatusChange }) {
  const [updating, setUpdating] = useState(false);

  const statuses = ["Planned", "In Progress", "Completed"];

  async function handleChange(e) {
    const newStatus = e.target.value;
    setUpdating(true);

    const res = await apiFetch(`/assistants/milestones/${milestone.id}/`, {
      method: "PATCH",
      body: { status: newStatus },
    });

    if (res.ok) {
      onStatusChange(newStatus);
    } else {
      alert("Failed to update milestone status");
    }
    setUpdating(false);
  }

  return (
    <select
      className="form-select form-select-sm"
      value={milestone.status || "Planned"}
      onChange={handleChange}
      disabled={updating}
    >
      {statuses.map((status) => (
        <option key={status} value={status}>
          {status}
        </option>
      ))}
    </select>
  );
}