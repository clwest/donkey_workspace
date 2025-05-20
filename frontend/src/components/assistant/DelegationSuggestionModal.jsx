import { useEffect, useState } from "react";
import Modal from "../CommonModal";
import apiFetch from "../../utils/apiClient";

export default function DelegationSuggestionModal({ memoryId, show, onClose }) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!show) return;
    async function load() {
      setLoading(true);
      try {
        const res = await apiFetch("/assistants/suggest_delegate/", {
          method: "POST",
          body: { memory_id: memoryId },
        });
        setResults(res.suggestions);
      } catch (err) {
        console.error(err);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [show, memoryId]);

  return (
    <Modal show={show} onClose={onClose} title="Delegate Suggestions">
      {loading ? (
        <p>Loading...</p>
      ) : results.length === 0 ? (
        <p>No suggestions.</p>
      ) : (
        <ul className="list-group mb-3">
          {results.map((r) => (
            <li key={r.slug} className="list-group-item d-flex justify-content-between align-items-center">
              {r.name}
              <span className="badge bg-secondary">{r.score.toFixed(2)}</span>
            </li>
          ))}
        </ul>
      )}
      <button className="btn btn-secondary" onClick={onClose}>Close</button>
    </Modal>
  );
}
