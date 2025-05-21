import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LongTermObjectiveEditor({ thread, onUpdated }) {
  const [value, setValue] = useState(thread.long_term_objective || "");

  async function save() {
    const data = await apiFetch(`/mcp/threads/${thread.id}/set_objective/`, {
      method: "POST",
      body: { objective: value },
    });
    onUpdated && onUpdated(data);
  }

  return (
    <div>
      <textarea
        className="form-control"
        rows={3}
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <button className="btn btn-primary mt-2" onClick={save}>
        Save Objective
      </button>
    </div>
  );
}
