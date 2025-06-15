import { useEffect, useState } from "react";
import CommonModal from "../CommonModal";
import apiFetch from "../../utils/apiClient";
import useTaskStatus from "../../hooks/useTaskStatus";
import TaskStatusBadge from "../TaskStatusBadge";

export default function AnchorDetailModal({ show, onClose, anchor }) {
  const [logs, setLogs] = useState([]);

  const trustTask = useTaskStatus(
    anchor ? `/glossary/anchor/${anchor.slug}/trust/` : null,
  );

  const handleTrust = async () => {
    if (!anchor) return;
    try {
      await trustTask.trigger();
      onClose();
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    if (!show || !anchor) return;
    apiFetch(`/anchor/${anchor.slug}/training/`)
      .then((d) => setLogs(d.reinforcements || []))
      .catch(() => setLogs([]));
  }, [show, anchor]);

  return (
    <CommonModal show={show} onClose={onClose} title="Reinforcement History">
      {anchor && (
        <div className="mb-2">
          Forecast Success:{" "}
          <span
            className={
              anchor.mutation_forecast_score > 0
                ? "text-success"
                : anchor.mutation_forecast_score < 0
                  ? "text-danger"
                  : "text-muted"
            }
          >
            {anchor.mutation_forecast_score?.toFixed(2)}
          </span>
          {anchor.is_trusted && (
            <span className="badge bg-success ms-2">Trusted</span>
          )}
          {!anchor.is_trusted && (
            <>
              <button
                className="btn btn-sm btn-primary ms-2"
                onClick={handleTrust}
                disabled={trustTask.isRunning}
              >
                {trustTask.isRunning ? "Marking..." : "Mark Trusted"}
              </button>
              <TaskStatusBadge
                status={
                  trustTask.isRunning
                    ? "running"
                    : trustTask.isError
                      ? "error"
                      : trustTask.hasRun
                        ? "complete"
                        : null
                }
                label="Trusted"
              />
            </>
          )}
        </div>
      )}
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
