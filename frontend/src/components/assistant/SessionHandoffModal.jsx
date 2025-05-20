import { useState, useEffect } from "react";
import Modal from "../CommonModal";
import apiFetch from "../../utils/apiClient";

export default function SessionHandoffModal({ sessionId, show, onClose }) {
  const [assistants, setAssistants] = useState([]);
  const [toAgent, setToAgent] = useState("");
  const [reason, setReason] = useState("");
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!show) return;
    async function load() {
      const list = await apiFetch("/assistants/");
      setAssistants(list);
    }
    load();
  }, [show]);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await apiFetch("/assistants/handoff/", {
        method: "POST",
        body: {
          from: assistants.find((a) => a.is_primary)?.slug || assistants[0]?.slug,
          to: toAgent,
          session_id: sessionId,
          reason,
        },
      });
      setSummary(res.handoff_summary);
    } catch (err) {
      console.error(err);
      alert("Failed to handoff session");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onClose={onClose} title="Delegate to Agent">
      {summary ? (
        <div>
          <h6>Context Bridge Summary</h6>
          <p>{summary}</p>
          <button className="btn btn-primary" onClick={() => onClose(true)}>
            Done
          </button>
        </div>
      ) : (
        <div>
          <div className="mb-2">
            <label className="form-label">Delegate To</label>
            <select
              className="form-select"
              value={toAgent}
              onChange={(e) => setToAgent(e.target.value)}
            >
              <option value="">Select...</option>
              {assistants.map((a) => (
                <option key={a.slug} value={a.slug}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>
          <div className="mb-3">
            <label className="form-label">Reason</label>
            <input
              className="form-control"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </div>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading || !toAgent}>
            {loading ? "Delegating..." : "Confirm"}
          </button>
        </div>
      )}
    </Modal>
  );
}
