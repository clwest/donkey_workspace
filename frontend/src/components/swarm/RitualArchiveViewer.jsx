import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualArchiveViewer() {
  const [archives, setArchives] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/ritual-archives/");
        setArchives(res.results || res);
      } catch (err) {
        console.error("Failed to load archives", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Archives</h5>
      <ul className="list-group">
        {archives.map((a) => (
          <li key={a.id} className="list-group-item">
            <strong>{a.name}</strong> – {a.ceremony_type}
          </li>
        ))}
        {archives.length === 0 && (
          <li className="list-group-item text-muted">No ritual archives.</li>
        )}
      </ul>
    </div>
  );
}
