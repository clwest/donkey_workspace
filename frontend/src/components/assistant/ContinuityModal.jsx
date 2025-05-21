import { useEffect, useState } from "react";
import Modal from "../CommonModal";
import apiFetch from "../../utils/apiClient";

export default function ContinuityModal({ assistantSlug, projectId, show, onClose }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!show) return;
    async function load() {
      setLoading(true);
      try {
        const data = await apiFetch(`/assistants/${assistantSlug}/evaluate-continuity/`, {
          method: "POST",
          body: projectId ? { project_id: projectId } : {},
        });
        setResult(data);
      } catch (err) {
        console.error("Continuity check failed", err);
        setResult(null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [assistantSlug, projectId, show]);

  const footer = (
    <button className="btn btn-secondary" onClick={onClose}>
      Close
    </button>
  );

  return (
    <Modal show={show} onClose={onClose} title="Continuity Check" footer={footer}>
      {loading ? (
        <p>Loading...</p>
      ) : !result ? (
        <p>No data.</p>
      ) : (
        <div>
          <p>
            <strong>Continuity Score:</strong> {result.continuity_score}
          </p>
          {result.thread_id && (
            <p>
              <strong>Thread:</strong> {result.thread_id}
            </p>
          )}
          {result.recent_thoughts && result.recent_thoughts.length > 0 && (
            <div>
              <h6>Recent Thoughts</h6>
              <ul className="list-group mb-2">
                {result.recent_thoughts.map((t) => (
                  <li key={t.id} className="list-group-item">
                    {t.text.slice(0, 80)}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {result.suggestions && result.suggestions.length > 0 && (
            <div>
              <h6>Suggestions</h6>
              <ul>
                {result.suggestions.map((s, idx) => (
                  <li key={idx}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </Modal>
  );
}
