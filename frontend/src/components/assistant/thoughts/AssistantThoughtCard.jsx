import { useState } from "react";
import { Modal, Button } from "react-bootstrap";
import { toast } from "react-toastify";
import TagBadge from "../../TagBadge"; // ✅ Display badge style tags
import "./styles/AssistantCardStyle.css";

const typeEmojis = {
  user: "👤",
  assistant: "🤖",
  cot: "🧩",
  reflection: "🪞",
  planning: "🛠️",
};

export default function AssistantThoughtCard({ thought, onUpdate, onDelete, badge, color = "secondary", icon }) {
  if (!thought || !thought.thought) {
    return <div className="alert alert-warning">⚠️ Invalid thought object.</div>;
  }

  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(thought.thought);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const getApiPath = () => {
    if (thought.project) {
      return `http://localhost:8000/api/assistants/projects/${thought.project}/thoughts/${thought.id}/`;
    } else if (thought.assistant) {
      return `http://localhost:8000/api/assistants/${thought.assistant}/submit_thought/`;
    }
    return null;
  };

  const handleSave = async () => {
    const apiPath = getApiPath();
    if (!apiPath) return toast.error("❌ Missing endpoint.");

    setSaving(true);
    try {
      const res = await fetch(apiPath, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thought: editValue }),
      });
      const data = await res.json();
      if (res.ok) {
        onUpdate(thought.id, data.updated_text || editValue);
        toast.success("💾 Thought updated!");
        setIsEditing(false);
        setShowModal(false);
      } else {
        toast.error("❌ Failed to update thought.");
      }
    } catch (err) {
      console.error("Save failed:", err);
      toast.error("❌ Server error.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!onDelete) return;
    if (!window.confirm("Delete this thought?")) return;

    const apiPath = getApiPath();
    if (!apiPath) return toast.error("❌ Missing endpoint for deletion.");

    setDeleting(true);
    try {
      const res = await fetch(apiPath, { method: "DELETE" });
      if (res.ok) {
        onDelete(thought.id);
        toast.success("🗑️ Thought deleted!");
        setShowModal(false);
      } else {
        toast.error("❌ Failed to delete thought.");
      }
    } catch (err) {
      console.error("Delete error:", err);
      toast.error("❌ Server error.");
    } finally {
      setDeleting(false);
    }
  };

  const preview = thought.thought.length > 120
    ? thought.thought.slice(0, 120) + "..."
    : thought.thought;
    console.log("Thought preview:", thought);

  return (
    <>
      <div
        className="card mb-3 shadow-sm hover-shadow-sm border border-light cursor-pointer"
        onClick={() => setShowModal(true)}
        style={{ cursor: "pointer" }}
      >
        <div className="card mb-3 p-3 shadow-sm rounded-4">
          <div className="card-body">
            <div className=" mb-2 p-3">
              <span className={`badge bg-${color}`}>{icon || typeEmojis[thought.thought_type] || "💭"} {badge || "Thought"}</span>
              <small className="text-muted">
                🕒 {new Date(thought.created_at).toLocaleString()}
              </small>
            </div>

            {thought.tags && thought.tags.length > 0 && (
              <div className="mb-2">
                {thought.tags.map((tag, idx) => (
                  <TagBadge tag={tag} key={idx} />
                ))}
              </div>
            )}

            <p className="mb-0 text-truncate" style={{ maxWidth: "100%" }}>
              {thought.thought}
            </p>
          </div>
        </div>
      </div>

      {/* 🔍 Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} centered size="lg">
        <Modal.Header closeButton>
          <Modal.Title>{badge || "🧠 Thought Detail"}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
            {isEditing ? (
              <textarea
                className="form-control"
                rows={6}
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
              />
            ) : (
              <>
                <p style={{ whiteSpace: "pre-line" }}>{thought.thought}</p>

                {thought.thought_trace && (
                  <div className="bg-light p-3 rounded mt-3">
                    <h6 className="text-muted">🧩 Chain of Thought</h6>
                    <pre className="mb-0" style={{ whiteSpace: "pre-wrap" }}>
                      {thought.thought_trace}
                    </pre>
                  </div>
                )}

                {thought.linked_memory_preview && (
                  <div className="alert alert-light mt-3">
                    <strong>🧠 Linked Memory:</strong>
                    <p className="mb-0" style={{ whiteSpace: "pre-wrap" }}>
                      {thought.linked_memory_preview}
                    </p>
                  </div>
                )}
                {thought.linked_memories && thought.linked_memories.length > 0 && (
                  <div className="mt-2">
                    <strong>Memories:</strong>{" "}
                    {thought.linked_memories.map((m, idx) => (
                      <span key={m} className="badge bg-secondary me-1">
                        {m.slice(0, 8)}
                      </span>
                    ))}
                  </div>
                )}
                {thought.linked_reflection && (
                  <div className="mt-2">
                    <a href={`/reflections/${thought.linked_reflection}`}>View Reflection</a>
                  </div>
                )}

                {thought.tags?.length > 0 && (
                  <div className="mt-3">
                    <strong className="d-block mb-2">🏷️ Tags:</strong>
                    {thought.tags.map((tag) => (
                      <TagBadge key={tag.slug} tag={tag} />
                    ))}
                  </div>
                )}
              </>
            )}
          </Modal.Body>
        <Modal.Footer>
          {isEditing ? (
            <>
              <Button variant="success" onClick={handleSave} disabled={saving}>
                💾 {saving ? "Saving..." : "Save"}
              </Button>
              <Button variant="secondary" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
            </>
          ) : (
            <>
              <Button variant="outline-primary" onClick={() => setIsEditing(true)}>
                ✏️ Edit
              </Button>
              {onDelete && (
                <Button variant="outline-danger" onClick={handleDelete} disabled={deleting}>
                  🗑️ Delete
                </Button>
              )}
            </>
          )}
        </Modal.Footer>
      </Modal>
    </>
  );
}
