import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RadianceFieldViewer() {
  const [fields, setFields] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/agents/purpose-radiance/");
        setFields(res.results || res);
      } catch (err) {
        console.error("Failed to load radiance fields", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Purpose Radiance</h5>
      <ul className="list-group">
        {fields.map((f) => (
          <li key={f.id} className="list-group-item">
            <strong>{f.assistant_name || f.assistant}</strong> – {f.emitted_frequency}
          </li>
        ))}
        {fields.length === 0 && (
          <li className="list-group-item text-muted">No radiance detected.</li>
        )}
      </ul>
    </div>
  );
}
