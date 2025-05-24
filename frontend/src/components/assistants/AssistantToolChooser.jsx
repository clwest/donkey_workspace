import { useEffect, useState } from "react";
import { fetchToolAssignments, saveToolAssignments } from "../../api/assistants";

export default function AssistantToolChooser({ assistantId }) {
  const [tools, setTools] = useState([]);
  const [assigned, setAssigned] = useState([]);

  useEffect(() => {
    if (!assistantId) return;
    fetchToolAssignments(assistantId)
      .then((res) => {
        setTools(res.tools || []);
        setAssigned(res.assigned || []);
      })
      .catch(() => {
        setTools([]);
        setAssigned([]);
      });
  }, [assistantId]);

  const toggle = (id) => {
    setAssigned((a) =>
      a.includes(id) ? a.filter((x) => x !== id) : [...a, id]
    );
  };

  const handleSave = async () => {
    try {
      await saveToolAssignments(assistantId, { tools: assigned });
      alert("Saved");
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="my-3">
      <h5>Tool Chooser</h5>
      <ul className="list-group mb-2">
        {tools.map((t) => (
          <li key={t.id} className="list-group-item">
            <label>
              <input
                type="checkbox"
                className="form-check-input me-2"
                checked={assigned.includes(t.id)}
                onChange={() => toggle(t.id)}
              />
              {t.name}
            </label>
          </li>
        ))}
      </ul>
      <button className="btn btn-primary" onClick={handleSave}>
        Save
      </button>
    </div>
  );
}
