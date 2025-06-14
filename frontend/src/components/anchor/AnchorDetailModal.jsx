import { useEffect, useState } from "react";
import CommonModal from "../CommonModal";
import apiFetch from "../../utils/apiClient";

export default function AnchorDetailModal({ show, onClose, anchor }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    if (!show || !anchor) return;
    apiFetch(`/anchor/${anchor.slug}/training/`)
      .then((d) => setLogs(d.reinforcements || []))
      .catch(() => setLogs([]));
  }, [show, anchor]);

  return (
    <CommonModal show={show} onClose={onClose} title="Reinforcement History">
      <ul className="list-group">
        {logs.map((l) => (
          <li key={l.id} className="list-group-item">
            <strong>{l.trigger_source}</strong> ➜ {l.outcome} (
            {l.score_delta >= 0 ? "+" : ""}
            {l.score_delta.toFixed(2)})
            <span className="float-end small text-muted">
              {new Date(l.created_at).toLocaleString()}
            </span>
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No logs</li>
        )}
      </ul>
    </CommonModal>
  );
}
