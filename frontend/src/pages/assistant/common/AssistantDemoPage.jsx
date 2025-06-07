import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import HintBubble from "../../../components/HintBubble";
import useAssistantHints from "../../../hooks/useAssistantHints";
import apiFetch from "../../../utils/apiClient";

export default function AssistantDemoPage() {
  const [assistants, setAssistants] = useState([]);
  const { hints, dismissHint } = useAssistantHints("demo");

  useEffect(() => {
    apiFetch("/api/assistants/demos/")
      .then((data) => setAssistants(Array.isArray(data) ? data : []))
      .catch((err) => console.error("Failed to fetch demo assistants:", err));
  }, []);

  return (
    <div className="container py-5 position-relative">
      <h1 className="mb-4">🧪 AI Assistant Demos</h1>
      {hints.find((h) => h.id === "demo_intro" && !h.dismissed) && (
        <HintBubble
          label={hints.find((h) => h.id === "demo_intro").label}
          content={hints.find((h) => h.id === "demo_intro").content}
          position={{ top: 60, right: 20 }}
          onDismiss={() => dismissHint("demo_intro")}
        />
      )}
      <div className="row" id="demo-assistant-cards">
        {assistants.map((assistant) => (
          <div key={assistant.id} className="col-md-4 mb-4">
            <div className="card h-100 shadow-sm border-0 sparkle-hover">
              <div className="card-body">
                <div className="d-flex align-items-center mb-3">
                  {assistant.avatar ? (
                    <img
                      src={assistant.avatar}
                      alt={assistant.name}
                      className="rounded-circle me-3"
                      style={{ width: "50px", height: "50px", objectFit: "cover" }}
                    />
                  ) : (
                    <div
                      className="rounded-circle bg-secondary me-3 d-flex justify-content-center align-items-center"
                      style={{ width: "50px", height: "50px", color: "white" }}
                    >
                      🤖
                    </div>
                  )}
                  <h5 className="mb-0">{assistant.name}</h5>
                </div>
                <p className="text-muted" style={{ fontSize: "0.9rem" }}>
                  {assistant.description || "No description provided."}
                </p>
                {assistant.specialty && (
                  <span className="badge bg-info text-dark">{assistant.specialty}</span>
                )}
              </div>
              <div className="card-footer bg-transparent border-0 text-end">
                <Link
                  to={`/assistants/${assistant.slug}`}
                  className="btn btn-outline-primary btn-sm"
                >
                  View Details
                </Link>
                <div>
                <Link
                  to={`/assistants/${assistant.slug}/chat?starter=${encodeURIComponent(
                    assistant.intro_text || "hello"
                  )}`}
                  className="btn btn-outline-primary btn-sm mt-2"
                >
                    💬 Chat
                </Link>
                <button
                  className="btn btn-success btn-sm ms-2 mt-2"
                  onClick={() =>
                    (window.location.href = `/assistants/${assistant.slug}/chat?starter=${encodeURIComponent(
                      assistant.intro_text || "hello"
                    )}`)
                  }
                >
                  Try This
                </button>
                </div>
              </div>
            </div>
          </div>
        ))}
        {assistants.length === 0 && (
          <p className="text-muted text-center">No demo assistants available yet.</p>
        )}
      </div>
      {hints.find((h) => h.id === "demo_start_chat" && !h.dismissed) && (
        <HintBubble
          label={hints.find((h) => h.id === "demo_start_chat").label}
          content={hints.find((h) => h.id === "demo_start_chat").content}
          highlightSelector="#demo-assistant-cards"
          onDismiss={() => dismissHint("demo_start_chat")}
        />
      )}
    </div>
  );
}
