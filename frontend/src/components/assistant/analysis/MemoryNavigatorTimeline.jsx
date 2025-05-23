import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function MemoryNavigatorTimeline({ assistantId }) {
  const [entries, setEntries] = useState([]);
  const [tag, setTag] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");

  useEffect(() => {
    if (!assistantId) return;
    async function load() {
      try {
        const params = new URLSearchParams();
        params.append("assistant_slug", assistantId);
        if (tag) params.append("tag", tag);
        if (start) params.append("start", start);
        if (end) params.append("end", end);
        const res = await apiFetch(`/memory/list?${params.toString()}`);
        setEntries(res);
      } catch (err) {
        console.error("Failed to load timeline", err);
        setEntries([]);
      }
    }
    load();
  }, [assistantId, tag, start, end]);

  return (
    <div className="my-3">
      <div className="d-flex gap-2 mb-3 flex-wrap">
        <input
          type="text"
          placeholder="Ritual tag"
          className="form-control form-control-sm"
          value={tag}
          onChange={(e) => setTag(e.target.value)}
          style={{ maxWidth: "120px" }}
        />
        <input
          type="date"
          className="form-control form-control-sm"
          value={start}
          onChange={(e) => setStart(e.target.value)}
        />
        <input
          type="date"
          className="form-control form-control-sm"
          value={end}
          onChange={(e) => setEnd(e.target.value)}
        />
      </div>
      <ul className="list-group">
        {entries.map((m) => (
          <li
            key={m.id}
            className={`list-group-item${m.tags?.includes('ritual') ? ' list-group-item-warning' : ''}`}
          >
            <div className="fw-bold">
              {new Date(m.created_at).toLocaleString()}
            </div>
            <div>{m.title || m.summary || m.event}</div>
          </li>
        ))}
        {entries.length === 0 && (
          <li className="list-group-item text-muted">No memory found.</li>
        )}
      </ul>
    </div>
  );
}
