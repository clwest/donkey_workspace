import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MemoryReformationForm() {
  const [actions, setActions] = useState([]);
  const [notes, setNotes] = useState("");

  useEffect(() => {
    apiFetch("/agents/restorative-memory/")
      .then((d) => setActions(d.results || d))
      .catch(() => setActions([]));
  }, []);

  const submitAction = async () => {
    if (!notes) return;
    const res = await apiFetch("/agents/restorative-memory/", {
      method: "POST",
      body: { reformation_notes: notes, initiating_assistant: null, damaged_memory: null },
    });
    setActions([res, ...actions]);
    setNotes("");
  };

  return (
    <div className="my-3">
      <h5>Restorative Memory Actions</h5>
      <div className="input-group mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="Reformation notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <button className="btn btn-primary" onClick={submitAction}>
          Submit
        </button>
      </div>
      <ul className="list-group">
        {actions.map((a) => (
          <li key={a.id} className="list-group-item">
            {a.reformation_notes}
          </li>
        ))}
        {actions.length === 0 && (
          <li className="list-group-item text-muted">No actions recorded.</li>
        )}
      </ul>
    </div>
  );
}
