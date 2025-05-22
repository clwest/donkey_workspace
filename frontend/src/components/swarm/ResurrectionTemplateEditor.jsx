import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ResurrectionTemplateEditor() {
  const [templates, setTemplates] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/resurrection-templates/");
        setTemplates(res.results || res);
      } catch (err) {
        console.error("Failed to load templates", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Resurrection Templates</h5>
      <ul className="list-group">
        {templates.map((t) => (
          <li key={t.id} className="list-group-item">
            {t.title} – {t.recommended_archetype}
          </li>
        ))}
        {templates.length === 0 && (
          <li className="list-group-item text-muted">No templates defined.</li>
        )}
      </ul>
    </div>
  );
}
