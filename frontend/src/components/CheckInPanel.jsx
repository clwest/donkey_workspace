import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function CheckInPanel({ assistantId }) {
  const [suggestions, setSuggestions] = useState("");
  const handleCheckIn = async () => {
    const data = await apiFetch(`/assistants/${assistantId}/check-in/`);
    setSuggestions(data.suggestions);
  };
  return (
    <div className="mb-3">
      <button className="btn btn-secondary" onClick={handleCheckIn}>
        Check In
      </button>
      {suggestions && <p className="mt-2">{suggestions}</p>}
    </div>
  );
}
