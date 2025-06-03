import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RecoveryPanel({ assistantSlug }) {
  const [assistant, setAssistant] = useState(null);
  const [thoughts, setThoughts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recovering, setRecovering] = useState(false);
  const [summary, setSummary] = useState("");
  const [promptTip, setPromptTip] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await apiFetch(`/assistants/${assistantSlug}/`);
        setAssistant(data);
        if (data.recent_drift) {
          const t = await apiFetch(
            `/assistants/${assistantSlug}/thoughts/?before=${data.recent_drift.timestamp}`
          );
          setThoughts(t.results || t);
        }
      } catch (err) {
        console.error("Failed to load recovery info", err);
      } finally {
        setLoading(false);
      }
    }
    load();
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
    if (!assistant?.id || !assistant?.current_project?.id) return;
    try {
      await apiFetch(`/assistants/thoughts/reflect_on_assistant/`, {
        method: "POST",
        body: {
          assistant_id: assistant.id,
          project_id: assistant.current_project.id,
          reason: "manual recovery",
        },
      });
    } catch (err) {
      console.error("Reflection failed", err);
    }
  };

  const handleRepairDocs = async () => {
    if (!assistant?.documents) return;
    for (const doc of assistant.documents) {
      try {
        await apiFetch(`/intel/debug/repair-progress/`, {
          method: "POST",
          body: { doc_id: doc.id },
        });
      } catch {
        // ignore individual failures
      }
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
          <button className="btn btn-outline-secondary" onClick={handleReflect}>
            Reflect Again
          </button>
          <button className="btn btn-outline-secondary" onClick={handleRepairDocs}>
            Repair Documents
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
