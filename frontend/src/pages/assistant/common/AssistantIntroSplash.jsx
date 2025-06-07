import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import AssistantBadgeIcon from "../../../components/assistant/AssistantBadgeIcon";
import AssistantOriginPanel from "../../../components/assistant/AssistantOriginPanel";
import AssistantPersonalizationPrompt from "../../../components/assistant/AssistantPersonalizationPrompt";
import "../../../components/assistant/styles/AssistantIntroSplash.css";

export default function AssistantIntroSplash() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState(null);
  const [showPersonalize, setShowPersonalize] = useState(false);

  useEffect(() => {
    apiFetch(`/assistants/${slug}/intro/`)
      .then((res) => {
        setData(res);
        setLoading(false);
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
      body: { show_intro_splash: false },
    });
    navigate(`/assistants/${slug}`);
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
    <div className="container my-5 fade-in text-center">
      {avatar}
      <h1 className="display-5">{data.name}</h1>
      {data.archetype && <h5 className="text-muted">{data.archetype}</h5>}
      {data.badges && data.badges.length > 0 && (
        <div className="d-flex justify-content-center gap-2 mt-2">
          {data.badges.map((b) => (
            <AssistantBadgeIcon key={b} badges={[b]} />
          ))}
        </div>
      )}
      {data.intro_text && <p className="mt-4 fs-5">{data.intro_text}</p>}
      <AssistantOriginPanel assistant={data} />
      <button className="btn btn-primary mt-4" onClick={handleContinue}>
        Let&apos;s Begin
      </button>
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
