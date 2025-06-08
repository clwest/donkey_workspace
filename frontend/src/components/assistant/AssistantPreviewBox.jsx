import PropTypes from "prop-types";

const AVATAR_EMOJI = { owl: "🦚", fox: "🦊", robot: "🤖", wizard: "🧙‍♂️" };

export default function AssistantPreviewBox({
  name,
  tone,
  personality,
  avatarStyle,
}) {
  const emoji = AVATAR_EMOJI[avatarStyle] || "🤖";
  return (
    <div className="card shadow-sm p-3 mb-3">
      <div className="d-flex align-items-center mb-2">
        <span className="fs-2 me-2">{emoji}</span>
        <strong>{name || "Untitled"}</strong>
      </div>
      {tone && <div className="small mb-1">Tone: {tone}</div>}
      {personality && <div className="small text-muted">{personality}</div>}
    </div>
  );
}

AssistantPreviewBox.propTypes = {
  name: PropTypes.string,
  tone: PropTypes.string,
  personality: PropTypes.string,
  avatarStyle: PropTypes.string,
};
