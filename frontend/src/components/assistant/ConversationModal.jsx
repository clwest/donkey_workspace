// frontend/components/assistants/ConversationModal.jsx

import { useEffect } from "react";
import "../assistants/styles/ConversationModal.css";

export default function ConversationModal({ isOpen, onClose, memory }) {
  useEffect(() => {
    if (isOpen) document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = "auto"; };
  }, [isOpen]);

  if (!isOpen || !memory) return null;

  const transcript = memory.full_transcript || [];

  return (
    <div className="conversation-modal-overlay">
      <div className="conversation-modal">
        <div className="conversation-header">
          <h5>🧠 Conversation Memory</h5>
          <button className="btn-close" onClick={onClose}></button>
        </div>

        <div className="conversation-body">
          {transcript.map((msg, index) => (
            <div
              key={index}
              className={`chat-message ${msg.role === "user" ? "user" : "assistant"}`}
            >
              <div className="chat-meta">
                <span className="role-badge">{msg.role}</span>
                <small className="text-muted">
                  {new Date(msg.timestamp || memory.created_at).toLocaleString()}
                </small>
              </div>
              <div className="chat-content">{msg.content}</div>
              {/* Placeholder for future feedback tools */}
              <div className="feedback-section">
                <button className="btn btn-sm btn-outline-secondary" disabled>
                  💬 Suggest Improvement
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="conversation-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}