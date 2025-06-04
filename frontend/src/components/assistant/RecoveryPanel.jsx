import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";

export default function RecoveryPanel({ assistantSlug }) {
  const [assistant, setAssistant] = useState(null);
  const [thoughts, setThoughts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recovering, setRecovering] = useState(false);
  const [reflecting, setReflecting] = useState(false);
  const [repairing, setRepairing] = useState(false);
  const [summary, setSummary] = useState("");
  const [promptTip, setPromptTip] = useState("");
  const loadAssistant = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/assistants/${assistantSlug}/`);
      setAssistant(data);
      if (data.recent_drift) {
        const t = await apiFetch(`/assistants/${assistantSlug}/thoughts/?before=${data.recent_drift.timestamp}`);
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
    setRecovering(true);
    try {
      const res = await apiFetch(`/assistants/${assistantSlug}/recover/`, {
        method: "POST",
      });
      setSummary(res.summary);
      setPromptTip(res.prompt_suggestion);
    } catch (err) {
      console.error("Recovery failed", err);
      setSummary("Recovery failed");
    } finally {
      setRecovering(false);
    }
  };

  const handleReflect = async () => {
    setReflecting(true);
    try {
      await apiFetch(`/assistants/${assistantSlug}/reflect_again/`, {
        method: "POST",
      });
      toast.success("Reflection triggered");
      await loadAssistant();
    } catch (err) {
      console.error("Reflection failed", err);
      toast.error("Reflection failed");
    } finally {
      setReflecting(false);
    }
  };

  const handleRepairDocs = async () => {
    setRepairing(true);
    try {
      await apiFetch(`/assistants/${assistantSlug}/repair_documents/`, {
        method: "POST",
      });
      toast.info("Repair triggered");
      await loadAssistant();
    } catch (err) {
      console.error("Repair failed", err);
      toast.error("Repair failed");
    } finally {
      setRepairing(false);
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
                {d.title} — {(d.embedded_chunks ?? d.num_embedded)}/{d.chunk_count}
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
            disabled={recovering}
          >
            {recovering ? "Recovering..." : "Run Recovery"}
          </button>
          <button
            className="btn btn-outline-secondary"
            onClick={handleReflect}
            disabled={reflecting}
          >
            {reflecting ? "Reflecting..." : "Reflect Again"}
          </button>
          <button
            className="btn btn-outline-secondary"
            onClick={handleRepairDocs}
            disabled={repairing}
          >
            {repairing ? "Repairing..." : "Repair Documents"}
          </button>
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
