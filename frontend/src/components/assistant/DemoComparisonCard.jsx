import PropTypes from "prop-types";
import { Link } from "react-router-dom";

const AVATAR_EMOJI = {
  owl: "🦚",
  fox: "🦊",
  robot: "🤖",
  wizard: "🧙‍♂️",
};

export default function DemoComparisonCard({ assistant }) {
  if (!assistant) return null;
  const emoji = AVATAR_EMOJI[assistant.avatar_style] || "🤖";
  return (
    <div className="card h-100 shadow-sm sparkle-hover">
      <div className="card-body">
        <h5 className="card-title">
          {assistant.flair && <span className="me-1">{assistant.flair}</span>}
          <span className="me-1">{emoji}</span>
          {assistant.name}
        </h5>
        {assistant.tone && (
          <p className="text-muted mb-1">Tone: {assistant.tone}</p>
        )}
        {assistant.traits && assistant.traits.length > 0 && (
          <p className="small mb-1">Traits: {assistant.traits.join(", ")}</p>
        )}
        {assistant.motto && (
          <p className="fst-italic small">"{assistant.motto}"</p>
        )}
        {assistant.preview_chat && (
          <div className="bg-light rounded p-2 mb-2">
            {assistant.preview_chat.map((line, idx) => (
              <div key={idx} className="small">
                {line}
              </div>
            ))}
          </div>
        )}
        <Link
          to={`/assistants/create?prefill=${assistant.demo_slug}`}
          className="btn btn-success btn-sm"
        >
          Customize This
        </Link>
      </div>
    </div>
  );
}

DemoComparisonCard.propTypes = {
  assistant: PropTypes.object.isRequired,
};
