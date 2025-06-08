import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import HintBubble from "../../../components/HintBubble";
import useAssistantHints from "../../../hooks/useAssistantHints";
import apiFetch from "../../../utils/apiClient";
import AssistantCard from "../../../components/assistant/AssistantCard";

export default function AssistantDemoPage() {
  const [assistants, setAssistants] = useState([]);
  const { hints, dismissHint } = useAssistantHints("demo");
  const [showBanner, setShowBanner] = useState(
    () => localStorage.getItem("demo_banner_seen") !== "1",
  );

  const dismissBanner = () => {
    localStorage.setItem("demo_banner_seen", "1");
    setShowBanner(false);
  };

  useEffect(() => {
    apiFetch("/assistants/demos/")
      .then((data) => setAssistants(Array.isArray(data) ? data : []))
      .catch((err) => {
        console.error("Failed to fetch demo assistants:", err);
        setAssistants([]);
      });
  }, []);

  return (
    <div className="container py-5 position-relative">
      <h1 className="mb-4">🧪 AI Assistant Demos</h1>
      {assistants.length > 1 && (
        <div className="mb-3 text-end d-flex justify-content-end gap-2">
          <Link
            to="/assistants/demos/compare"
            className="btn btn-outline-secondary btn-sm"
          >
            Compare Demos
          </Link>
          <Link
            to="/assistants/demos/insights"
            className="btn btn-outline-secondary btn-sm"
          >
            View Insights
          </Link>
          <Link
            to="/assistants/demos/leaderboard"
            className="btn btn-outline-secondary btn-sm"
          >
            Leaderboard
          </Link>
        </div>
      )}
      {showBanner && (
        <div className="alert alert-primary d-flex justify-content-between">
          <span>Meet the Prompt Pal! Start by opening a chat.</span>
          <button className="btn-close" onClick={dismissBanner}></button>
        </div>
      )}
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
                      style={{
                        width: "50px",
                        height: "50px",
                        objectFit: "cover",
                      }}
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
                  <span className="badge bg-info text-dark">
                    {assistant.specialty}
                  </span>
                )}
              </div>
              <div className="card-footer bg-transparent border-0 text-end">
                <Link
                  to={`/assistants/${assistant.demo_slug || assistant.slug}`}
                  className="btn btn-outline-primary btn-sm"
                >
                  View Details
                </Link>
                <div>
                  <Link
                    to={`/assistants/${assistant.demo_slug || assistant.slug}/chat?starter=${encodeURIComponent(
                      assistant.intro_text || "hello",
                    )}`}
                    className="btn btn-outline-primary btn-sm mt-2"
                  >
                    💬 Chat
                  </Link>
                  <button
                    className="btn btn-success btn-sm ms-2 mt-2"
                    onClick={() =>
                      (window.location.href = `/assistants/${assistant.demo_slug || assistant.slug}/chat?starter=${encodeURIComponent(
                        assistant.intro_text || "hello",
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
          <p className="text-muted text-center">No demos found.</p>
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
      <div
        className="position-fixed bottom-0 end-0 m-4 bg-light border rounded p-3 shadow"
        style={{ zIndex: 2000 }}
      >
        <strong>Welcome!</strong>
        <div className="mt-2 d-flex flex-column">
          <button className="btn btn-sm btn-outline-primary mb-1">
            What can I ask?
          </button>
          <button className="btn btn-sm btn-outline-primary mb-1">
            Show me a cool example
          </button>
          <Link className="btn btn-sm btn-success" to="/assistants/create">
            How do I create my own?
          </Link>
        </div>
      </div>
    </div>
  );
}
