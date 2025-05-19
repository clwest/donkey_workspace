import { useState } from "react";

export default function MessageCard({ message, onFeedback, onTopicSave }) {
  const [tempTopic, setTempTopic] = useState(message.topic || "");
  const [editing, setEditing] = useState(false);

  const handleTopicSubmit = () => {
    if (tempTopic.trim()) {
      onTopicSave(message.uuid, tempTopic.trim());
      setEditing(false);
      setTempTopic("");
    }
  };

  return (
    <div className={`mb-4 ${message.role === "user" ? "text-end" : "text-start"}`}>
      <div>
        <span className={`badge ${message.role === "user" ? "bg-primary" : "bg-secondary"} me-2`}>
          {message.role}
        </span>
        <small className="text-muted">{new Date(message.created_at).toLocaleTimeString()}</small>
      </div>

      <div className={`p-3 rounded ${message.role === "user" ? "bg-light" : "bg-white border"}`}>
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