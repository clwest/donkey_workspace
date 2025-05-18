import { useState } from "react";

export default function MilestoneStatusSelector({ milestone, onStatusChange }) {
  const [updating, setUpdating] = useState(false);

  const statuses = ["Planned", "In Progress", "Completed"];

  async function handleChange(e) {
    const newStatus = e.target.value;
    setUpdating(true);

    const res = await fetch(`http://localhost:8000/api/assistants/milestones/${milestone.id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
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