import { useEffect, useState } from "react";
import Modal from "../CommonModal";
import { planFromThread } from "../../api/assistants";

export default function ThreadPlanningModal({ slug, threadId, show, onClose }) {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!show) return;
    async function load() {
      setLoading(true);
      try {
        const res = await planFromThread(slug, { thread_id: threadId });
        setActions(res);
      } catch (err) {
        console.error(err);
        setActions([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [show, slug, threadId]);

  return (
    <Modal show={show} onClose={onClose} title="Proposed Plan">
      {loading ? (
        <p>Generating...</p>
      ) : actions.length === 0 ? (
        <p>No actions.</p>
      ) : (
        <ul className="list-group mb-3">
          {actions.map((a) => (
            <li key={a.id} className="list-group-item d-flex justify-content-between align-items-center">
              <span>{a.content}</span>
              {a.assigned_agent_name && (
                <span className="badge bg-secondary ms-2">{a.assigned_agent_name}</span>
              )}
            </li>
          ))}
        </ul>
      )}
      <button className="btn btn-secondary" onClick={onClose}>
        Close
      </button>
    </Modal>
  );
}
