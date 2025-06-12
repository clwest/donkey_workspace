import { Link } from "react-router-dom";
import PrimaryStar from "./PrimaryStar";
import AssistantBadgeIcon from "./AssistantBadgeIcon";
import PropTypes from "prop-types";
import PreviewPopover from "./PreviewPopover";
import "./styles/AssistantCard.css";

const AVATAR_EMOJI = {
  owl: "🦚",
  fox: "🦊",
  robot: "🤖",
  wizard: "🧙‍♂️",
};

export default function AssistantCard({ assistant, to, chatLink, demo }) {
  if (!assistant) return null;

  const displayName =
    assistant.identity?.display_name ||
    assistant.identity?.persona_name ||
    assistant.identity?.name ||
    assistant.name;

  const isDemo = demo || assistant.is_demo;

  const card = (
    <div className="assistant-card card h-100 shadow-sm border-0">
      <div className="card-body">
        <div className="d-flex align-items-center mb-2">
          {assistant.avatar ? (
            <img
              src={assistant.avatar}
              alt={displayName}
              className="rounded-circle me-2"
              style={{ width: "48px", height: "48px", objectFit: "cover" }}
            />
          ) : (
            <span className="fs-2 me-2">{AVATAR_EMOJI[assistant.avatar_style] || "🤖"}</span>
          )}
          <h5 className="card-title mb-0">
            {assistant.flair && (
              <span className="me-1" role="img" aria-label="badge">
                {assistant.flair}
              </span>
            )}
            {displayName}
            <PrimaryStar isPrimary={assistant.is_primary} />
            <AssistantBadgeIcon badges={assistant.skill_badges} primaryBadge={assistant.primary_badge} />
            {assistant.drift_fix_count >= 3 && (
              <span className="badge bg-primary ms-2">Refined</span>
            )}
            {assistant.glossary_terms_fixed > 5 && <span className="ms-1">✨</span>}
          </h5>
        </div>
        {isDemo && (
          <span className="badge bg-info text-dark mb-2">✨ Demo Assistant</span>
        )}
        {assistant.is_demo_clone && assistant.spawned_by_label && (
          <span className="badge bg-warning text-dark mb-2 ms-2">
            Inspired by {assistant.spawned_by_label}
          </span>
        )}
        {assistant.specialty && <p className="text-muted mb-1 small">{assistant.specialty}</p>}
        <p className="card-text small">
          {assistant.description?.slice(0, 100) || "No description."}
        </p>
        {assistant.is_active !== undefined && (
          <span className={`badge ${assistant.is_active ? "bg-success" : "bg-secondary"}`}>{assistant.is_active ? "Active" : "Inactive"}</span>
        )}
        {assistant.needs_recovery && (
          <span className="badge bg-warning text-dark ms-2">Misaligned</span>
        )}
      </div>
      {(chatLink || (!isWrapped && to)) && (
        <div className="card-footer bg-transparent border-0 text-end">
          {!isWrapped && to && (
            <Link to={to} className="btn btn-outline-primary btn-sm me-2">
              View Details
            </Link>
          )}
          {chatLink && (
            <Link to={chatLink} className="btn btn-outline-primary btn-sm">
              💬 Chat
            </Link>
          )}
        </div>
      )}
    </div>
  );

  const isWrapped = to && !chatLink;
  const wrapped = isWrapped ? (
    <Link to={to} className="text-decoration-none">{card}</Link>
  ) : (
    card
  );

  return (
    <PreviewPopover slug={assistant.slug}>
      {wrapped}
    </PreviewPopover>
  );
}

AssistantCard.propTypes = {
  assistant: PropTypes.object.isRequired,
  to: PropTypes.string,
  chatLink: PropTypes.string,
  demo: PropTypes.bool,
};
