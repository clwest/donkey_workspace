import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";
import useTaskStatus from "../../hooks/useTaskStatus";
import TaskStatusBadge from "../TaskStatusBadge";

export default function RecoveryPanel({ assistantSlug }) {
  const [assistant, setAssistant] = useState(null);
  const [thoughts, setThoughts] = useState([]);
  const [loading, setLoading] = useState(true);
  const recoverTask = useTaskStatus(`/assistants/${assistantSlug}/recover/`);
  const reflectTask = useTaskStatus(
    `/assistants/${assistantSlug}/reflect_again/`,
  );
  const repairTask = useTaskStatus(
    `/assistants/${assistantSlug}/repair_documents/`,
  );
  const [summary, setSummary] = useState("");
  const [promptTip, setPromptTip] = useState("");
  const loadAssistant = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/assistants/${assistantSlug}/`);
      setAssistant(data);
      if (data.recent_drift) {
        const t = await apiFetch(
          `/assistants/${assistantSlug}/thoughts/?before=${data.recent_drift.timestamp}`,
        );
        setThoughts(t.results || t);
      }
    } catch (err) {
      console.error("Failed to load recovery info", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssistant();
  }, [assistantSlug]);

  const handleRecover = async () => {
    try {
      const res = await recoverTask.trigger();
      setSummary(res.summary);
      setPromptTip(res.prompt_suggestion);
    } catch (err) {
      console.error("Recovery failed", err);
      setSummary("Recovery failed");
    }
  };

  const handleReflect = async () => {
    try {
      await reflectTask.trigger();
      toast.success("Reflection triggered");
      await loadAssistant();
    } catch (err) {
      console.error("Reflection failed", err);
      toast.error("Reflection failed");
    }
  };

  const handleRepairDocs = async () => {
    try {
      await repairTask.trigger();
      toast.info("Repair triggered");
      await loadAssistant();
    } catch (err) {
      console.error("Repair failed", err);
      toast.error("Repair failed");
    }
  };

  if (loading) return <div>Loading recovery info...</div>;

  return (
    <div className="card mb-3">
      <div className="card-header">Recovery</div>
      <div className="card-body">
        {assistant?.documents?.length > 0 && (
          <ul className="mb-3">
            {assistant.documents.map((d) => (
              <li key={d.id}>
                {d.title} — {d.embedded_chunks ?? d.num_embedded}/
                {d.chunk_count}
              </li>
            ))}
          </ul>
        )}
        {summary && <p className="small text-muted">{summary}</p>}
        {promptTip && <p className="small text-muted">{promptTip}</p>}
        <div className="d-flex gap-2 mb-2">
          <button
            className="btn btn-warning"
            onClick={handleRecover}
            disabled={recoverTask.isRunning}
          >
            {recoverTask.isRunning ? "Recovering..." : "Run Recovery"}
          </button>
          <TaskStatusBadge
            status={
              recoverTask.isRunning
                ? "running"
                : recoverTask.isError
                  ? "error"
                  : recoverTask.hasRun
                    ? "complete"
                    : null
            }
            label="Recovery"
          />
          <button
            className="btn btn-outline-secondary"
            onClick={handleReflect}
            disabled={reflectTask.isRunning}
          >
            {reflectTask.isRunning ? "Reflecting..." : "Reflect Again"}
          </button>
          <TaskStatusBadge
            status={
              reflectTask.isRunning
                ? "running"
                : reflectTask.isError
                  ? "error"
                  : reflectTask.hasRun
                    ? "complete"
                    : null
            }
            label="Reflection"
          />
          <button
            className="btn btn-outline-secondary"
            onClick={handleRepairDocs}
            disabled={repairTask.isRunning}
          >
            {repairTask.isRunning ? "Repairing..." : "Repair Documents"}
          </button>
          <TaskStatusBadge
            status={
              repairTask.isRunning
                ? "running"
                : repairTask.isError
                  ? "error"
                  : repairTask.hasRun
                    ? "complete"
                    : null
            }
            label="Repair"
          />
        </div>
        {thoughts.length > 0 && (
          <ul className="mt-3">
            {thoughts.slice(0, 3).map((t) => (
              <li key={t.id}>{t.thought}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
