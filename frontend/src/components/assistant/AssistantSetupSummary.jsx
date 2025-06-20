import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import apiFetch from "@/utils/apiClient";
import AssistantBadgeIcon from "./AssistantBadgeIcon";
import GlossaryAnchorCard from "../onboarding/GlossaryAnchorCard";
import TonePreview from "../onboarding/TonePreview";
import BoostSummaryPanel from "./BoostSummaryPanel";
import GrowthTrackPanel from "./GrowthTrackPanel";
import AssistantRefinementWizard from "./AssistantRefinementWizard";

const AVATAR_EMOJI = {
  owl: "🦚",
  fox: "🦊",
  robot: "🤖",
  wizard: "🧙‍♂️",
};

export default function AssistantSetupSummary({ assistantId, assistant }) {
  const [data, setData] = useState(assistant || null);
  const [error, setError] = useState(false);
  const [showWizard, setShowWizard] = useState(false);

  useEffect(() => {
    if (assistant || !assistantId) return;
    apiFetch(`/assistants/${assistantId}/setup_summary/`)
      .then(setData)
      .catch(() => setError(true));
  }, [assistantId, assistant]);

  if (error) return <div className="alert alert-warning">Failed to load setup summary.</div>;
  if (!data) return <div>Loading...</div>;

  const avatar = data.avatar ? (
    <img
      src={data.avatar}
      alt="avatar"
      className="rounded-circle me-2"
      width="60"
      height="60"
    />
  ) : (
    <span className="fs-1 me-2">{AVATAR_EMOJI[data.avatar_style] || "🤖"}</span>
  );

  return (
    <div className="card shadow-sm p-3">
      <div className="d-flex align-items-center mb-3">
        {avatar}
        <h5 className="mb-0">{data.name}</h5>
      </div>
      <div className="mb-3">
        <strong className="me-1">Tone:</strong>
        <TonePreview tone={data.tone_profile || data.tone} />
      </div>
      {data.initial_glossary_anchor && (
        <div className="mb-3">
          <h6 className="mb-1">First Glossary Term</h6>
          <GlossaryAnchorCard anchor={data.initial_glossary_anchor} />
        </div>
      )}
      <div>
        <h6 className="mb-1">Badges</h6>
        {data.initial_badges && data.initial_badges.length ? (
          <div className="d-flex gap-2">
            {data.initial_badges.map((b) => (
              <AssistantBadgeIcon key={b.slug} badges={[b.slug]} />
            ))}
          </div>
        ) : (
          <p className="text-muted mb-0">No badges yet.</p>
        )}
      </div>
      <GrowthTrackPanel
        slug={data.slug}
        stage={data.growth_stage}
        points={data.growth_points}
      />
      <BoostSummaryPanel
        summary={data.boost_summary}
        demoSlug={data.demo_origin_slug}
        slug={data.slug}
        inject={data.boost_prompt_in_system}
      />
      <button
        className="btn btn-sm btn-outline-primary mt-2"
        onClick={() => setShowWizard(true)}
      >
        Refine from Drift
      </button>
      <AssistantRefinementWizard
        slug={data.slug}
        sessionId={data.demo_session_id}
        show={showWizard}
        onClose={() => setShowWizard(false)}
      />
    </div>
  );
}

AssistantSetupSummary.propTypes = {
  assistantId: PropTypes.string,
  assistant: PropTypes.object,
};
