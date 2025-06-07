import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";
import { suggestDelegation } from "../../../api/assistants";

export default function ObjectivesPage() {
  const { slug } = useParams();
  const [objectives, setObjectives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selected, setSelected] = useState(null);
  const [customPrompt, setCustomPrompt] = useState("");
  const [events, setEvents] = useState([]);
  const [planningId, setPlanningId] = useState(null);


  useEffect(() => {
    if (!slug) {
      console.warn("ObjectivesPage: missing assistant slug");
      return;
    }
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
    async function fetchEvents() {
      try {
        const data = await apiFetch("/storyboard/");
        setEvents(data);
      } catch (err) {
        console.error("Failed to load events", err);
      }
    }
    fetchEvents();
  }, [slug]);

  async function handlePlanTasks(objId) {
    setPlanningId(objId);
    try {
      const tasks = await apiFetch(`/assistants/${slug}/plan-tasks/${objId}/`, {
        method: "POST",
      });
      setObjectives((prev) =>
        prev.map((o) => (o.id === objId ? { ...o, tasks } : o))
      );
    } catch (err) {
      console.error("Failed to plan tasks", err);
    } finally {
      setPlanningId(null);
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
                <h5 className={obj.is_completed ? "text-success" : ""}>
                  {obj.title}
                  {obj.generated_from_reflection && (
                    <span
                      className="badge bg-info ms-2"
                      title={`Evolved from reflection on ${new Date(obj.reflection_created_at).toLocaleDateString()}`}
                    >
                      🔄
                    </span>
                  )}
                </h5>
                {obj.description && (
                  <p className="small text-muted mb-1">{obj.description}</p>
                )}
                {obj.linked_event_title && (
                  <p className="small text-muted mb-1">
                    📌 {obj.linked_event_title}
                  </p>
                )}
              </div>
              <div className="d-flex gap-2">
                <button
                  className="btn btn-sm btn-outline-primary"
                  onClick={() => handlePlanTasks(obj.id)}
                  disabled={planningId === obj.id}
                >
                  {planningId === obj.id ? (
                    <>
                      <span
                        className="spinner-border spinner-border-sm me-2"
                        role="status"
                      />
                      Planning...
                    </>
                  ) : (
                    "📋 Plan Tasks"
                  )}
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
                <button
                  className="btn btn-sm btn-outline-primary"
                  onClick={async () => {
                    try {
                      const data = await suggestDelegation(slug, {
                        context_type: "objective",
                        context_id: obj.id,
                      });
                      if (data.recommended_assistant) {
                        alert(
                          `Recommend: ${data.recommended_assistant.name}\nReason: ${data.recommended_assistant.reason}`
                        );
                      } else {
                        alert("No suggestion available");
                      }
                    } catch (err) {
                      alert("Failed to get recommendation");
                    }
                  }}
                >
                  💡 Suggest Agent
                </button>
              </div>
              {obj.tasks?.length > 0 && (
                <ul className="list-group mt-2">
                  {obj.tasks.map((task) => (
                    <li key={task.id} className="list-group-item small">
                      {task.title}
                    </li>
                  ))}
                </ul>
              )}
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
