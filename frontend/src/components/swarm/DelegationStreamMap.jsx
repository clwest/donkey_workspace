import { useEffect, useState } from "react";
import { fetchDelegationStreams } from "../../api/agents";

export default function DelegationStreamMap() {
  const [streams, setStreams] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchDelegationStreams();
        setStreams(data.results || data);
      } catch (err) {
        console.error("Failed to load streams", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Delegation Streams</h5>
      <ul className="list-group">
        {streams.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.stream_name} – {s.stream_status}
          </li>
        ))}
        {streams.length === 0 && (
          <li className="list-group-item text-muted">No streams.</li>
        )}
      </ul>
    </div>
  );
}
