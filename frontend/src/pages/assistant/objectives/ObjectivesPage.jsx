import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function ObjectivesPage() {
  const { slug } = useParams();
  const [objectives, setObjectives] = useState([]);
  const [loading, setLoading] = useState(true);
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
      } finally {
        setLoading(false);
      }
    }
    fetchObjectives();
  }, [slug]);

  async function handlePlanTasks(objId) {
    try {
      await apiFetch(`/assistants/${slug}/plan-tasks/${objId}/`, { method: "POST" });
      const data = await apiFetch(`/assistants/${slug}/objectives/`);
      setObjectives(data);
    } catch (err) {
      console.error("Failed to plan tasks", err);
    }
  }

  if (!slug) {
    return <div className="container my-5">Assistant slug missing.</div>;
  }

  if (loading) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">🎯 Objectives for {slug}</h1>
      {objectives.length === 0 ? (
        <p>No objectives found.</p>
      ) : (

        <ul className="list-group mb-4">
          {objectives.map((obj) => (
            <li
              key={obj.id}
              className="list-group-item d-flex justify-content-between align-items-start"
            >
              <div>
                <h5 className={obj.is_completed ? "text-success" : ""}>{obj.title}</h5>
                {obj.description && (
                  <p className="small text-muted mb-1">{obj.description}</p>
                )}
              </div>
              <div className="d-flex gap-2">
                <button
                  className="btn btn-sm btn-outline-primary"
                  onClick={() => handlePlanTasks(obj.id)}
                >
                  📋 Plan Tasks
                </button>
                <button
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => {
                    setSelected(obj);
                    setShowModal(true);
                  }}
                >
                  🤖 Delegate
                </button>
              </div>
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
