import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import { OverlayTrigger, Tooltip } from "react-bootstrap";
import BackToAssistantButton from "../../../components/assistant/BackToAssistantButton";

const badgeInfo = {
  glossary_apprentice: "Earned for acquiring 10 glossary anchors",
  semantic_master: "Earned for reinforcing 25 anchors",
  reflection_ready: "Earned for completing 5 reflections",
  delegation_ready: "Earned after unlocking 3 badges",
};

export default function AssistantBadgesPage() {
  const { slug } = useParams();
  const [assistant, setAssistant] = useState(null);
  const [badgeData, setBadgeData] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    apiFetch(`/assistants/${slug}/`)
      .then(setAssistant)
      .catch(() => setError(true));
    apiFetch(`/assistants/badges/?assistant=${slug}`)
      .then(setBadgeData)
      .catch(() => setBadgeData({ badges: [] }));
  }, [slug]);

  const handlePrimary = async (e) => {
    const badge = e.target.value;
    setSaving(true);
    try {
      await apiFetch(`/assistants/${slug}/`, {
        method: "PATCH",
        body: { primary_badge: badge },
      });
      setAssistant((a) => ({ ...a, primary_badge: badge }));
    } catch (err) {
      console.error("Failed to update", err);
    } finally {
      setSaving(false);
    }
  };
  if (error)
    return (
      <div className="container my-4 text-warning">Failed to load badges.</div>
    );
  if (!assistant || !badgeData)
    return <div className="container my-4">Loading...</div>;
  const badges = badgeData.badges || [];

  return (
    <div className="container my-4">
      <BackToAssistantButton slug={slug} />
      <h3>{assistant.name} Badges</h3>
      <div className="mb-3">
        {badges.map((b) => (
          <OverlayTrigger
            key={b.slug}
            placement="top"
            overlay={<Tooltip>{b.description}</Tooltip>}
          >
            <span
              className={`badge me-2 mb-2 ${b.earned ? "bg-success" : "bg-secondary"}`}
            >
              {b.slug}
            </span>
          </OverlayTrigger>
        ))}
      </div>
      {assistant.skill_badges.length > 0 && (
        <div className="mb-3">
          <label className="form-label">Primary Badge</label>
          <select
            className="form-select"
            value={assistant.primary_badge || ""}
            onChange={handlePrimary}
            disabled={saving}
          >
            <option value="">(none)</option>
            {assistant.skill_badges.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}
