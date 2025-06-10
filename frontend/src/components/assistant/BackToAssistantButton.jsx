import { Link } from "react-router-dom";
import PropTypes from "prop-types";

export default function BackToAssistantButton({ slug }) {
  if (!slug) return null;
  return (
    <Link to={`/assistants/${slug}`} className="btn btn-secondary mb-3">
      ← Back to Assistant
    </Link>
  );
}

BackToAssistantButton.propTypes = {
  slug: PropTypes.string.isRequired,
};
