import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation, Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import { assignPrimaryAssistant } from "../../../api/assistants";
import AssistantBadgeIcon from "../../../components/assistant/AssistantBadgeIcon";
import AssistantOriginPanel from "../../../components/assistant/AssistantOriginPanel";
import AssistantPersonalizationPrompt from "../../../components/assistant/AssistantPersonalizationPrompt";
import "../../../components/assistant/styles/AssistantIntroSplash.css";

export default function AssistantIntroSplash() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState(null);
  const [showPersonalize, setShowPersonalize] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);
  const starter = location.state?.starter;

  useEffect(() => {
    apiFetch(`/assistants/${slug}/intro/`)
      .then((res) => {
        setData(res);
        setLoading(false);
        if (res.demo_origin || location.state?.showConfetti) {
          setShowConfetti(true);
          setTimeout(() => setShowConfetti(false), 1500);
        }
        if (res.suggest_personalization) {
          apiFetch(`/assistants/${slug}/`).then(setDetail);
          setShowPersonalize(true);
        }
      })
      .catch(() => setLoading(false));
  }, [slug]);

  const handleContinue = async () => {
    await apiFetch(`/assistants/${slug}/`, {
      method: "PATCH",
      body: { show_intro_splash: false, show_trail_recap: true },
    });
    navigate(`/assistants/${slug}/trail`);
  };

  const handleSaved = async () => {
    const updated = await apiFetch(`/assistants/${slug}/`);
    setDetail(updated);
    setData({ ...data, ...updated, suggest_personalization: false });
  };

  if (loading) return <div className="container my-5">Loading...</div>;
  if (!data) return <div className="container my-5">Failed to load.</div>;

  const avatar = data.avatar_url ? (
    <img
      src={data.avatar_url}
      alt="avatar"
      className="rounded-circle mb-3"
      width="80"
      height="80"
    />
  ) : (
    <span className="fs-1 mb-3 d-block">{data.flair || "🤖"}</span>
  );

  return (
    <div className="container my-5 fade-in text-center position-relative">
      {showConfetti && <div className="confetti" />}
      {avatar}
      <h1 className="display-5">{data.name}</h1>
      {data.demo_origin && (
        <div className="text-muted mb-2 fade-in">Inspired by {data.demo_origin} 🌟</div>
      )}
      {data.archetype && <h5 className="text-muted">{data.archetype}</h5>}
      {data.badges && data.badges.length > 0 && (
        <div className="d-flex justify-content-center gap-2 mt-2">
          {data.badges.map((b) => (
            <AssistantBadgeIcon key={b} badges={[b]} />
          ))}
        </div>
      )}
      {data.intro_text && <p className="mt-4 fs-5">{data.intro_text}</p>}
      {data.birth_reflection && (
        <div className="alert alert-info mx-auto mt-3" style={{ maxWidth: 500 }}>
          <h5 className="mb-1">Birth Reflection</h5>
          <p className="mb-0">{data.birth_reflection}</p>
        </div>
      )}
      {starter && (
        <p className="text-muted mt-2">First Prompt: "{starter}"</p>
      )}
      {data.trail_summary && (
        <div className="alert alert-light mx-auto" style={{ maxWidth: 500 }}>
          <p className="mb-2">{data.trail_summary}</p>
          {data.recent_milestones && (
            <ul className="list-unstyled mb-0">
              {data.recent_milestones.map((m, i) => (
                <li key={i}>📍 {m.marker_type} – {new Date(m.timestamp).toLocaleDateString()}</li>
              ))}
            </ul>
          )}
        </div>
      )}
      <AssistantOriginPanel assistant={data} />
      <div className="d-flex justify-content-center gap-2 mt-4">
        <Link className="btn btn-secondary" to={`/assistants/${slug}/edit`}>
          Edit Assistant
        </Link>
        <button
          className="btn btn-primary"
          onClick={() => navigate(`/assistants/${slug}/chat`)}
        >
          Start Chat
        </button>
        {!data.is_primary && (
          <button
            className="btn btn-outline-warning"
            onClick={async () => {
              await assignPrimaryAssistant(slug);
              setData({ ...data, is_primary: true });
            }}
          >
            ⭐ Pin as Primary
          </button>
        )}
        <button className="btn btn-outline-primary" onClick={handleContinue}>
          View Trail
        </button>
      </div>
      {detail && (
        <AssistantPersonalizationPrompt
          assistant={{ ...detail, personalization_prompt: data.personalization_prompt }}
          show={showPersonalize}
          onClose={() => setShowPersonalize(false)}
          onSaved={handleSaved}
        />
      )}
    </div>
  );
}
