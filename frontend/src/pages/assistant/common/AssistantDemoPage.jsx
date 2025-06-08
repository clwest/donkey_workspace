import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import HintBubble from "../../../components/HintBubble";
import useAssistantHints from "../../../hooks/useAssistantHints";
import apiFetch from "../../../utils/apiClient";
import AssistantCard from "../../../components/assistant/AssistantCard";
import DemoAssistantShowcase from "../../../components/demo/DemoAssistantShowcase";
import DemoSuccessCarousel from "../../../components/demo/DemoSuccessCarousel";
import DemoTipsModal from "../../../components/demo/DemoTipsModal";
import useDemoSession from "../../../hooks/useDemoSession";
import LoadingSpinner from "../../../components/LoadingSpinner";

export default function AssistantDemoPage() {
  const [assistants, setAssistants] = useState([]);
  const [successes, setSuccesses] = useState(null);
  const { hints, dismissHint } = useAssistantHints("demo");
  const [showBanner, setShowBanner] = useState(
    () => localStorage.getItem("demo_banner_seen") !== "1",
  );
  const { demoSessionId } = useDemoSession();
  const [showTips, setShowTips] = useState(false);
  const [showWelcome, setShowWelcome] = useState(
    () => localStorage.getItem("demo_welcome_dismiss") !== "1",
  );

  const dismissBanner = () => {
    localStorage.setItem("demo_banner_seen", "1");
    setShowBanner(false);
  };

  const dismissWelcome = () => {
    localStorage.setItem("demo_welcome_dismiss", "1");
    setShowWelcome(false);
  };

  useEffect(() => {
    apiFetch("/assistants/demos/")
      .then(async (data) => {
        if (Array.isArray(data) && data.length > 0) {
          setAssistants(data);
        } else {
          const seeded = await apiFetch("/assistants/demos/?force_seed=1");
          setAssistants(Array.isArray(seeded) ? seeded : []);
        }
      })
      .catch(async (err) => {
        console.error("Failed to fetch demo assistants:", err);
        try {
          const seeded = await apiFetch("/assistants/demos/?force_seed=1");
          setAssistants(Array.isArray(seeded) ? seeded : []);
        } catch {
          setAssistants([]);
        }
      });
    apiFetch("/assistants/demo_success/")
      .then((data) => setSuccesses(Array.isArray(data) ? data : []))
      .catch((err) => {
        console.error("Failed to load demo successes", err);
        setSuccesses([]);
      });
  }, []);

  const featured = assistants
    .filter((a) => a.is_featured)
    .sort((a, b) => (a.featured_rank || 0) - (b.featured_rank || 0));

  return (
    <div className="container py-5 position-relative">
      <h1 className="mb-4">🧪 AI Assistant Demos</h1>
      {import.meta.env.DEV && (
        <button
          className="btn btn-warning btn-sm mb-3"
          onClick={async () => {
            await apiFetch("/assistants/demos/?force_seed=1");
            window.location.reload();
          }}
          disabled={assistants.length === 0}
        >
          Reset Demos
        </button>
      )}
      <DemoAssistantShowcase assistants={featured} />
      <DemoSuccessCarousel assistants={successes.slice(0, 5)} />
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
          <Link
            to="/assistants/demos/success"
            className="btn btn-outline-secondary btn-sm"
          >
            Success Stories
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
            <div className="card h-100 shadow-sm border-0 sparkle-hover position-relative">
              {assistant.is_featured && (
                <span className="badge bg-warning position-absolute top-0 start-0">
                  🏆 Featured
                </span>
              )}
              {!assistant.is_featured && assistant.metrics?.conversion_rate > 0.25 && (
                <span className="badge bg-danger position-absolute top-0 start-0">
                  🔥 Trending
                </span>
              )}
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
                {assistant.metrics && (
                  <div className="small text-muted mb-1">
                    💬 {assistant.metrics.avg_messages?.toFixed(1)} chats/session
                  </div>
                )}
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
          <p className="text-muted text-center">
            Demos are being loaded, please refresh soon.
          </p>
        )}
      </div>
      {successes === null ? (
        <LoadingSpinner className="my-4" />
      ) : (
        successes.length > 0 && (
          <div className="mt-4">
            <h2 className="h6 mb-3">✨ Recently Created From Demo</h2>
            <div className="row">
              {successes.map((s) => (
                <div key={s.slug} className="col-md-4 mb-3">
                  <AssistantCard assistant={s} chatLink={`/assistants/${s.slug}/chat`} />
                </div>
              ))}
            </div>
          </div>
        )
      )}
      {hints.find((h) => h.id === "demo_start_chat" && !h.dismissed) && (
        <HintBubble
          label={hints.find((h) => h.id === "demo_start_chat").label}
          content={hints.find((h) => h.id === "demo_start_chat").content}
          highlightSelector="#demo-assistant-cards"
          onDismiss={() => dismissHint("demo_start_chat")}
        />
      )}
      {showWelcome && (
        <div
          className="position-fixed bottom-0 end-0 m-4 bg-light border rounded p-3 shadow"
          style={{ zIndex: 2000 }}
        >
          <div className="d-flex justify-content-between align-items-start">
            <strong>Welcome!</strong>
            <button className="btn-close" onClick={dismissWelcome}></button>
          </div>
          <div className="mt-2 d-flex flex-column">
            <button
              className="btn btn-sm btn-outline-primary mb-1"
              onClick={() => setShowTips(true)}
            >
              What can I ask?
            </button>
            <button
              className="btn btn-sm btn-outline-primary mb-1"
              onClick={() => {
                const slug = assistants[0]?.demo_slug || "prompt_pal";
                const starter =
                  assistants[0]?.intro_text || "Need a better prompt?";
                window.location.href = `/assistants/${slug}/chat?starter=${encodeURIComponent(
                  starter,
                )}&demo=1`;
              }}
            >
              Show me a cool example
            </button>
            <Link className="btn btn-sm btn-success" to="/assistants/create">
              How do I create my own?
            </Link>
          </div>
        </div>
      )}
      <DemoTipsModal
        show={showTips}
        onClose={() => setShowTips(false)}
        slug={assistants[0]?.demo_slug || "prompt_pal"}
        sessionId={demoSessionId}
      />
    </div>
  );
}
