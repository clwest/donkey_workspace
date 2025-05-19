import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function ObjectivesPage() {
  const { slug } = useParams();
  const [objectives, setObjectives] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selected, setSelected] = useState(null);
  const [customPrompt, setCustomPrompt] = useState("");

  useEffect(() => {
    if (!slug) return;
    async function fetchObjectives() {
      try {
        const data = await apiFetch(`/assistants/${slug}/objectives/`);
        setObjectives(data);
      } catch (err) {
        console.error("Failed to load objectives", err);
      }
    }
    fetchObjectives();
  }, [slug]);

  if (!slug) {
    return <div className="container my-5">Assistant slug missing.</div>;
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">🎯 Objectives for {slug}</h1>
      {objectives.length === 0 ? (
        <p>No objectives found.</p>
      ) : (
        <ul className="list-group mb-4">
          {objectives.map((obj) => (
            <li key={obj.id} className="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <strong>{obj.title}</strong>
                {obj.description && (
                  <div className="small text-muted">{obj.description}</div>
                )}
              </div>
              <button
                className="btn btn-sm btn-outline-primary"
                onClick={() => {
                  setSelected(obj);
                  setShowModal(true);
                }}
              >
                🤖 Delegate
              </button>
            </li>
          ))}
        </ul>
      )}

      <Link to="/assistants/projects" className="btn btn-outline-secondary">
        🔙 Back to Projects
      </Link>

      {showModal && selected && (
        <div className="modal d-block" tabIndex="-1" role="dialog">
          <div className="modal-dialog" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Delegate Objective</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <div className="modal-body">
                <p>Spawn a delegate for: <strong>{selected.title}</strong></p>
                <textarea
                  className="form-control"
                  placeholder="Custom prompt (optional)"
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                ></textarea>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={async () => {
                    try {
                      await apiFetch(`/assistants/${slug}/delegate/${selected.id}/`, {
                        method: "POST",
                        body: { prompt: customPrompt },
                      });
                      setShowModal(false);
                    } catch (err) {
                      alert("Delegation failed");
                    }
                  }}
                >
                  Confirm
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
