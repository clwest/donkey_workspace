import { useEffect, useState } from "react";
import { fetchCollaborationThreads } from "../../api/agents";

export default function CollaborationThreadBoard() {
  const [threads, setThreads] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchCollaborationThreads();
        setThreads(data.results || data);
      } catch (err) {
        console.error("Failed to load threads", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Collaboration Threads</h5>
      <ul className="list-group">
        {threads.map((t) => (
          <li key={t.id} className="list-group-item">
            <strong>{t.title}</strong> – {t.narrative_focus}
          </li>
        ))}
        {threads.length === 0 && (
          <li className="list-group-item text-muted">No threads.</li>
        )}
      </ul>
    </div>
  );
}
