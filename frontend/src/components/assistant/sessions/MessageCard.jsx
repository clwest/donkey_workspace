import { useState } from "react";

export default function MessageCard({ message, onFeedback, onTopicSave }) {
  const [tempTopic, setTempTopic] = useState(message.topic || "");
  const [editing, setEditing] = useState(false);

  if (message.message_type === "system") {
    return (
      <div className="alert alert-secondary text-center my-3">
        {message.content}
      </div>
    );
  }

  const handleTopicSubmit = () => {
    if (tempTopic.trim()) {
      onTopicSave(message.uuid, tempTopic.trim());
      setEditing(false);
      setTempTopic("");
    }
  };

  return (
    <div
      className={`mb-4 card shadow-sm p-3 ${
        message.role === "user" ? "text-end" : "text-start"
      }`}
    >
      <div>
        <span className={`badge ${message.role === "user" ? "bg-primary" : "bg-secondary"} me-2`}>
          {message.role}
        </span>
        <small className="text-muted">{new Date(message.created_at).toLocaleTimeString()}</small>
      </div>

      <div className={message.role === "user" ? "bg-light rounded" : "bg-white border rounded"}>
        <p className="mb-2">{message.content}</p>
        {message.message_type === "image" && message.image_url && (
          <img src={message.image_url} alt="generated" className="img-fluid mb-2" />
        )}
        {message.message_type === "audio" && message.audio_url && (
          <audio controls className="w-100 mb-2">
            <source src={message.audio_url} />
          </audio>
        )}
        {(message.tts_model || message.style) && (
          <span className="badge bg-secondary">
            {message.tts_model && `TTS: ${message.tts_model}`}
            {message.tts_model && message.style && " | "}
            {message.style && message.style}
          </span>
        )}
        {message.role === "assistant" && (
          <div className="mt-1">
            {message.rag_fallback && (message.used_chunks?.[0]?.score || 0) < 0.6 ? (
              <span className="badge bg-warning text-dark">⚠️ Weak Context</span>
            ) : message.rag_used ? (
              (message.used_chunks?.[0]?.score || 0) >= 0.75 ? (
                <span className="badge bg-success">🔗 Good Source</span>
              ) : null
            ) : (
              <span className="badge bg-danger">🚫 No Source Used</span>
            )}
            {" "}
            {message.glossary_present && !message.rag_used ? (
              <span className="badge bg-warning text-dark">⚠️ Ignored Glossary</span>
            ) : (
              <span className="badge bg-secondary">
                📘 Glossary Present: {message.glossary_present ? "✅" : "❌"}
              </span>
            )}
            {message.context_score !== undefined && (
              <span className="badge bg-info text-dark ms-2" title="Context score">
                Context Score: {message.context_score.toFixed(4)}
                {message.context_score < 0.65 ? " (weak)" : ""}
              </span>
            )}
          </div>
        )}

        {/* Feedback */}
        <div className="d-flex align-items-center gap-2 my-2">
          <select
            className="form-select form-select-sm w-auto"
            value={message.feedback || ""}
            onChange={(e) => onFeedback(message.uuid, e.target.value)}
          >
            <option value="">Give Feedback</option>
            <option value="perfect">✅ Perfect</option>
            <option value="helpful">👍 Helpful</option>
            <option value="not_helpful">👎 Not Helpful</option>
            <option value="too_long">💤 Too Long</option>
            <option value="too_short">⚡ Too Short</option>
          <option value="irrelevant">❌ Irrelevant</option>
          <option value="unclear">❓ Unclear</option>
        </select>

        {(message.feedback === "too_long" ||
          message.feedback === "unclear" ||
          message.feedback === "irrelevant") && (
          <span className="badge bg-warning text-dark">Should delegate?</span>
        )}

          {/* Inline topic entry when editing */}
          {message.topic && !editing ? (
                <span
                    className="badge rounded-pill bg-info text-dark"
                    style={{ cursor: "pointer" }}
                    onClick={() => setEditing(true)}
                >
                    🏷️ {message.topic}
                </span>
                ) : (
                <div className="input-group input-group-sm mt-2">
                    <input
                    type="text"
                    className="form-control"
                    placeholder="Topic (e.g. Bray Day)"
                    value={tempTopic}
                    onChange={(e) => setTempTopic(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") handleTopicSubmit();
                    }}
                    />
                    <button className="btn btn-outline-secondary" onClick={handleTopicSubmit}>
                    💾 Save
                    </button>
                </div>
                )}
        </div>
      </div>
    </div>
  );
}