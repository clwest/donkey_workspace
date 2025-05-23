import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function PersonaTemplateGallery() {
  const [templates, setTemplates] = useState([]);

  useEffect(() => {
    apiFetch("/persona-templates/").then(setTemplates).catch(() => setTemplates([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Persona Templates</h5>
      <ul className="list-group">
        {templates.map((t) => (
          <li key={t.id} className="list-group-item">
            {t.template_name} – {t.default_role}
          </li>
        ))}
        {templates.length === 0 && (
          <li className="list-group-item text-muted">No templates.</li>
        )}
      </ul>
    </div>
  );
}
