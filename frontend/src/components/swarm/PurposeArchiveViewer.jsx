import { useEffect, useState } from "react";
import { fetchPurposeArchives } from "../../api/agents";

export default function PurposeArchiveViewer() {
  const [archives, setArchives] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchPurposeArchives();
        setArchives(data.results || data);
      } catch (err) {
        console.error("Failed to load purpose archives", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Purpose Archives</h5>
      <ul className="list-group">
        {archives.map((a) => (
          <li key={a.id} className="list-group-item">
            {a.assistant} – {a.symbolic_tags && Object.keys(a.symbolic_tags).join(", ")}
          </li>
        ))}
        {archives.length === 0 && (
          <li className="list-group-item text-muted">No archives.</li>
        )}
      </ul>
    </div>
  );
}
