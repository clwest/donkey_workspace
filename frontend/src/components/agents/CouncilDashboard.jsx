import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CouncilDashboard() {
  const [councils, setCouncils] = useState([]);

  useEffect(() => {
    apiFetch("/assistants/councils/")
      .then(setCouncils)
      .catch((err) => console.error("Failed to load councils", err));
  }, []);

  return (
    <div className="my-4">
      <h4 className="mb-3">Assistant Councils</h4>
      {councils.map((c) => (
        <div key={c.id} className="border rounded p-3 mb-2">
          <h6 className="mb-1">{c.name}</h6>
          <p className="mb-1">
            Mission: {c.mission_node_name || "N/A"}
          </p>
          <p className="mb-0 text-muted">
            Members: {c.members.map((m) => m.name).join(", ")}
          </p>
        </div>
      ))}
      {councils.length === 0 && (
        <p className="text-muted">No councils found.</p>
      )}
    </div>
  );
}
