import { useEffect, useState } from "react";
import {

  fetchAssistantTools,
  assignAssistantTools,
  reflectOnTools,
} from "../../api/assistants";
import { fetchTools } from "../../api/tools";


export default function AssistantToolChooser({ assistantId }) {
  const [assigned, setAssigned] = useState([]);

  const [available, setAvailable] = useState([]);
  const [reflection, setReflection] = useState("");


  useEffect(() => {
    if (!assistantId) return;
    fetchAssistantTools(assistantId)
      .then((res) => {
        const slugs = (res.tools || []).map((t) => t.slug);
        setAssigned(slugs);
      })

      .catch(() => setAssigned([]));
    fetchTools()
      .then((all) => setAvailable(all || []))
      .catch(() => setAvailable([]));

  }, [assistantId]);

  const toggle = (slug) => {
    setAssigned((a) =>
      a.includes(slug) ? a.filter((x) => x !== slug) : [...a, slug]
    );
  };

  const handleSave = async () => {
    try {
      await assignAssistantTools(assistantId, { tools: assigned });
      alert("Saved");
    } catch (e) {
      console.error(e);
    }
  };

  const handleReflect = async () => {
    try {
      const res = await reflectOnTools(assistantId);
      setReflection(res.summary || "");
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="my-3">
      <h5>Tool Chooser</h5>
      <ul className="list-group mb-2">
        {available.map((t) => (
          <li key={t.slug} className="list-group-item">
            <label>
              <input
                type="checkbox"
                className="form-check-input me-2"
                checked={assigned.includes(t.slug)}
                onChange={() => toggle(t.slug)}
              />
              {t.name}
            </label>
          </li>
        ))}
      </ul>
      <button className="btn btn-primary" onClick={handleSave}>
        Save
      </button>

      <button className="btn btn-secondary ms-2" onClick={handleReflect}>
        Reflect
      </button>
      {reflection && (
        <pre className="mt-2 bg-light p-2 border rounded">
          {reflection}
        </pre>
      )}

    </div>
  );
}
