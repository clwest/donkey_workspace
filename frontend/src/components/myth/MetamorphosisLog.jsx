import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MetamorphosisLog({ assistantSlug }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    async function load() {
      if (!assistantSlug) return;
      try {
        const data = await apiFetch(
          `/assistants/${assistantSlug}/metamorphosis/`,
        );
        setLogs(data || []);
      } catch (err) {
        console.error("Failed to fetch metamorphosis log", err);
      }
    }
    load();
  }, [assistantSlug]);

  if (logs.length === 0) return <div>No metamorphosis events.</div>;

  return (
    <div className="card mb-3">
      <div className="card-header">Metamorphosis Log</div>
      <div className="card-body">
        <ul className="list-group">
          {logs.map((l) => (
            <li key={l.id} className="list-group-item">
              {l.title} - {l.created_at}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
