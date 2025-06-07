import { useState } from "react";
import { Modal, Button } from "react-bootstrap";
import { toast } from "react-toastify";
import apiFetch from "@/utils/apiClient";
import { mutateThought } from "../../../api/assistants";
import TagBadge from "../../TagBadge"; // ✅ Display badge-style tags
import "./styles/AssistantCardStyle.css";

function ThoughtTrace({ trace }) {
  const [showRaw, setShowRaw] = useState(false);
  let data = null;
  if (trace) {
    if (typeof trace === "string") {
      try {
        data = JSON.parse(trace);
      } catch (err) {
        data = null;
      }
    } else if (typeof trace === "object") {
      data = trace;
    }
  }

  if (!data) {
    return (
      <div className="bg-light p-3 rounded mt-3">
        <h6 className="text-muted">🧩 Chain of Thought</h6>
        <pre className="mb-0" style={{ whiteSpace: "pre-wrap" }}>{trace}</pre>
      </div>
    );
  }

  return (
    <div className="bg-light p-3 rounded mt-3">
      <h6 className="text-muted">🧩 Chain of Thought</h6>
      <dl className="thought-details">
        {data.score !== undefined && (
          <>
            <dt>Score</dt>
            <dd>{data.score}</dd>
          </>
        )}
        {data.role && (
          <>
            <dt>Role</dt>
            <dd>{data.role}</dd>
          </>
        )}
        {data.summary && (
          <>
            <dt>Summary</dt>
            <dd>{data.summary}</dd>
          </>
        )}
        {data.focus && (
          <>
            <dt>Focus</dt>
            <dd>{data.focus}</dd>
          </>
        )}
        {data.personality && (
          <>
            <dt>Personality</dt>
            <dd>{data.personality}</dd>
          </>
        )}
        {data.prompt_tweaks && (
          <>
            <dt>Prompt Tweaks</dt>
            <dd>{String(data.prompt_tweaks)}</dd>
          </>
        )}
      </dl>
      <button
        className="btn btn-link btn-sm px-0"
        onClick={() => setShowRaw((v) => !v)}
      >
        {showRaw ? "Hide Raw JSON" : "View Raw JSON"}
      </button>
      {showRaw && (
        <pre className="bg-light p-2 mt-2 small">
          {typeof trace === "string" ? trace : JSON.stringify(trace, null, 2)}
        </pre>
      )}
    </div>
  );
}

const typeEmojis = {
  user: "👤",
  assistant: "🤖",
  cot: "🧩",
  reflection: "🪞",
  planning: "🛠️",
  dream: "😴",
};

export default function AssistantThoughtCard({
  thought,
  onUpdate,
  onDelete,
  badge,
  color = "secondary",
  icon,
}) {
  if (!thought) {
    console.warn("AssistantThoughtCard missing thought prop");
    return (
      <div className="alert alert-warning">⚠️ Invalid thought object.</div>
    );
  }

  if (!thought.summary && !thought.thought && !thought.content) {
    console.warn("Invalid thought object", thought);
    return (
      <div className="alert alert-warning">⚠️ Invalid thought object.</div>
    );
  }

  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(
    thought.thought || thought.summary || thought.content || "",
  );
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [feedbackValue, setFeedbackValue] = useState(thought.feedback || "");
  const [mutating, setMutating] = useState(false);

  const getApiPath = () => {
    if (thought.project) {
      return `/api/assistants/projects/${thought.project}/thoughts/${thought.id}/`;
    } else if (thought.assistant) {
      return `/api/assistants/${thought.assistant}/submit_thought/`;
    }
    return null;
  };

  const handleSave = async () => {
    const apiPath = getApiPath();
    if (!apiPath) return toast.error("❌ Missing endpoint.");

    setSaving(true);
    try {
      const data = await apiFetch(apiPath, {
        method: "POST",
        body: { thought: editValue },
      });
      if (data) {
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
      await apiFetch(apiPath, { method: "DELETE" });
      {
        onDelete(thought.id);
        toast.success("🗑️ Thought deleted!");
        setShowModal(false);
      }
    } catch (err) {
      console.error("Delete error:", err);
      toast.error("❌ Server error.");
    } finally {
      setDeleting(false);
    }
  };

  // --- New handlers to prevent undefined errors ---
  const handleFeedbackChange = (value) => {
    setFeedbackValue(value);
    // TODO: hit your PATCH endpoint to persist feedback if needed
    // e.g. fetch(getApiPath(), { method: "PATCH", body: JSON.stringify({ feedback: value }) })
  };

  const handleMutate = async (mutationType) => {
    setMutating(true);
    try {
      // assumes mutateThought(thoughtId, action) returns { updated_text }
      const data = await mutateThought(thought.id, mutationType);
      onUpdate(thought.id, data.updated_text || data.text || editValue);
      toast.success("✨ Thought mutated!");
      setShowModal(false);
    } catch (err) {
      console.error("Mutate error:", err);
      toast.error("❌ Mutation failed.");
    } finally {
      setMutating(false);
    }
  };
  // -----------------------------------------------------

  const baseText = thought.summary || thought.thought || thought.content || "";
  const preview =
    baseText.length > 120 ? baseText.slice(0, 120) + "..." : baseText;
  const moodClash = thought.mood === "frustrated" || thought.mood === "angry";

  return (
    <>
      <div
        className={`card mb-3 shadow-sm border-light${
          thought.mode === "dream" ? " dream-bg" : ""
        }`}
        onClick={() => setShowModal(true)}
        style={{ cursor: "pointer" }}
      >
        <div className="card-body p-3">
          <div className="mb-2">
            <span className={`badge bg-${color}`}>
              {icon || typeEmojis[thought.thought_type] || "💭"}{" "}
              {badge || "Thought"}
            </span>{" "}
            {moodClash && (
              <span className="text-warning ms-2">⚠️ Mood clash</span>
            )}
            <small className="text-muted">
              🕒{' '}
              {new Date(
                thought.created_at || thought.timestamp || Date.now(),
              ).toLocaleString()}
            </small>
            {thought.thought_type === "prompt_clarification" && (
              <span className="badge bg-warning text-dark ms-2">
                ⚠️ Clarified Prompt
              </span>
            )}
          </div>

          {thought.parent_thought && (
            <div className="text-muted small mb-1">
              🧬 Refined from {thought.parent_thought.slice(0, 8)}
            </div>
          )}

          {thought.tags?.length > 0 && (
            <div className="mb-2">
              {thought.tags.map((tag, idx) => (
                <TagBadge tag={tag} key={idx} />
              ))}
            </div>
          )}

          <p className="mb-0 text-truncate" style={{ maxWidth: "100%" }}>
            {preview}
          </p>

          <div className="mt-2">
            <select
              className="form-select form-select-sm w-auto"
              value={feedbackValue}
              onChange={(e) => handleFeedbackChange(e.target.value)}
            >
              <option value="">💬 Feedback</option>
              <option value="perfect">✅ Perfect</option>
              <option value="helpful">👍 Helpful</option>
              <option value="not_helpful">👎 Not Helpful</option>
              <option value="too_long">💤 Too Long</option>
              <option value="too_short">⚡ Too Short</option>
              <option value="irrelevant">❌ Irrelevant</option>
              <option value="unclear">❓ Unclear</option>
            </select>
          </div>
        </div>
      </div>

      {/* 🔍 Modal */}
      <Modal
        show={showModal}
        onHide={() => setShowModal(false)}
        centered
        size="lg"
      >
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
              <p style={{ whiteSpace: "pre-line" }}>
                {thought.thought || thought.summary}
              </p>

              {thought.thought_trace && (
                <ThoughtTrace trace={thought.thought_trace} />
              )}

              {thought.linked_memory_preview && (
                <div className="alert alert-light mt-3">
                  <strong>🧠 Linked Memory:</strong>
                  <p className="mb-0" style={{ whiteSpace: "pre-wrap" }}>
                    {thought.linked_memory_preview}
                  </p>
                </div>
              )}

              {thought.linked_memories?.length > 0 && (
                <div className="mt-2">
                  <strong>Memories:</strong>{" "}
                  {thought.linked_memories.map((m) => (
                    <span key={m} className="badge bg-secondary me-1">
                      {m.slice(0, 8)}
                    </span>
                  ))}
                </div>
              )}

              {thought.linked_reflection && (
                <div className="mt-2">
                  <a href={`/reflections/${thought.linked_reflection}`}>
                    View Reflection
                  </a>
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

              <div className="mt-3">
                <select
                  className="form-select form-select-sm w-auto"
                  value={feedbackValue}
                  onChange={(e) => handleFeedbackChange(e.target.value)}
                >
                  <option value="">💬 Feedback</option>
                  <option value="perfect">✅ Perfect</option>
                  <option value="helpful">👍 Helpful</option>
                  <option value="not_helpful">👎 Not Helpful</option>
                  <option value="too_long">💤 Too Long</option>
                  <option value="too_short">⚡ Too Short</option>
                  <option value="irrelevant">❌ Irrelevant</option>
                  <option value="unclear">❓ Unclear</option>
                </select>
              </div>
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
              <Button
                variant="outline-primary"
                onClick={() => setIsEditing(true)}
              >
                ✏️ Edit
              </Button>
              {onDelete && (
                <Button
                  variant="outline-danger"
                  onClick={handleDelete}
                  disabled={deleting}
                >
                  🗑️ Delete
                </Button>
              )}
              {["unclear", "too_long", "irrelevant"].includes(
                feedbackValue,
              ) && (
                <div className="dropdown ms-2">
                  <button
                    className="btn btn-outline-secondary dropdown-toggle"
                    data-bs-toggle="dropdown"
                    disabled={mutating}
                  >
                    🛠️ Refine Thought
                  </button>
                  <ul className="dropdown-menu">
                    <li>
                      <button
                        className="dropdown-item"
                        onClick={() => handleMutate("clarify")}
                      >
                        Clarify
                      </button>
                    </li>
                    <li>
                      <button
                        className="dropdown-item"
                        onClick={() => handleMutate("shorten")}
                      >
                        Shorten
                      </button>
                    </li>
                    <li>
                      <button
                        className="dropdown-item"
                        onClick={() => handleMutate("rephrase")}
                      >
                        Rephrase
                      </button>
                    </li>
                  </ul>
                </div>
              )}
            </>
          )}
        </Modal.Footer>
      </Modal>
    </>
  );
}
