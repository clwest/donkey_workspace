import { useState } from "react";
import Modal from "../../CommonModal";

export default function ThoughtDetailModal({ show, onClose, thought }) {
  if (!thought) return null;
  const [showRaw, setShowRaw] = useState(false);

  let trace = null;
  if (thought.thought_trace) {
    try {
      trace =
        typeof thought.thought_trace === "string"
          ? JSON.parse(thought.thought_trace)
          : thought.thought_trace;
    } catch (err) {
      trace = null;
    }
  }

  const renderTrace = () => {
    if (!trace) {
      return (
        <pre className="bg-light p-2 small">{thought.thought_trace}</pre>
      );
    }
    return (
      <>
        <dl className="thought-details">
          {trace.score !== undefined && (
            <>
              <dt>Score</dt>
              <dd>{trace.score}</dd>
            </>
          )}
          {trace.role && (
            <>
              <dt>Role</dt>
              <dd>{trace.role}</dd>
            </>
          )}
          {trace.summary && (
            <>
              <dt>Summary</dt>
              <dd>{trace.summary}</dd>
            </>
          )}
          {trace.focus && (
            <>
              <dt>Focus</dt>
              <dd>{trace.focus}</dd>
            </>
          )}
          {trace.personality && (
            <>
              <dt>Personality</dt>
              <dd>{trace.personality}</dd>
            </>
          )}
          {trace.prompt_tweaks && (
            <>
              <dt>Prompt Tweaks</dt>
              <dd>{String(trace.prompt_tweaks)}</dd>
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
          <pre className="bg-light p-2 small mt-2">
            {typeof thought.thought_trace === "string"
              ? thought.thought_trace
              : JSON.stringify(thought.thought_trace, null, 2)}
          </pre>
        )}
      </>
    );
  };

  return (
    <Modal show={show} onClose={onClose} title="🧠 Thought Detail">
      <p style={{ whiteSpace: "pre-line" }}>{thought.thought || thought.summary}</p>
      {renderTrace()}
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
          <a href={`/reflections/${thought.linked_reflection}`}>View Reflection</a>
        </div>
      )}
      {thought.tags?.length > 0 && (
        <div className="mt-3">
          <strong className="d-block mb-2">🏷️ Tags:</strong>
          {thought.tags.map((tag) => (
            <span key={tag.slug} className="badge bg-secondary me-1">
              {tag.name || tag.slug}
            </span>
          ))}
        </div>
      )}
    </Modal>
  );
}
