import { Link } from "react-router-dom";
import { OverlayTrigger, Tooltip } from "react-bootstrap";
import PrimaryStar from "./PrimaryStar";
import AssistantBadgeIcon from "./AssistantBadgeIcon";
import PropTypes from "prop-types";
import "./styles/AssistantCard.css";

const AVATAR_EMOJI = {
  owl: "🦚",
  fox: "🦊",
  robot: "🤖",
  wizard: "🧙‍♂️",
};

export default function AssistantCard({ assistant, to, chatLink, demo }) {
  if (!assistant) return null;
  const tooltipText = assistant.description || assistant.specialty || "No description.";

  const card = (
    <div className="assistant-card card h-100 shadow-sm border-0">
      <div className="card-body">
        <div className="d-flex align-items-center mb-2">
          {assistant.avatar ? (
            <img
              src={assistant.avatar}
              alt={assistant.name}
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
            {assistant.name}
            <PrimaryStar isPrimary={assistant.is_primary} />
            <AssistantBadgeIcon badges={assistant.skill_badges} primaryBadge={assistant.primary_badge} />
          </h5>
        </div>
        {demo && <span className="badge bg-info text-dark mb-2">✨ Demo Assistant</span>}
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
      {(to || chatLink) && (
        <div className="card-footer bg-transparent border-0 text-end">
          {to && (
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

  return (
    <OverlayTrigger placement="top" overlay={<Tooltip>{tooltipText}</Tooltip>}>
      {to && !chatLink ? (
        <Link to={to} className="text-decoration-none">{card}</Link>
      ) : (
        card
      )}
    </OverlayTrigger>
  );
}

AssistantCard.propTypes = {
  assistant: PropTypes.object.isRequired,
  to: PropTypes.string,
  chatLink: PropTypes.string,
  demo: PropTypes.bool,
};
