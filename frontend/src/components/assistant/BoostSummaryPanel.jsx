import PropTypes from "prop-types";
import { Link } from "react-router-dom";

import apiFetch from "@/utils/apiClient";

export default function BoostSummaryPanel({ summary, traits = [], demoSlug, slug, inject }) {
  const toggle = async () => {
    await apiFetch(`/assistants/${slug}/`, { method: "PATCH", body: { boost_prompt_in_system: !inject } });
    window.location.reload();
  };
  if (!summary) return null;
  return (
    <div className="alert alert-success mt-3">
      <h6 className="mb-1">Boost Summary</h6>
      <p className="mb-2">{summary}</p>
      {traits.length > 0 && (
        <p className="mb-2">
          <strong>Traits:</strong> {traits.join(", ")}
        </p>
      )}
      {demoSlug && (
        <Link to={`/assistants/${demoSlug}`}>View Original Demo</Link>
      )}
      {slug && (
        <div className="form-check mt-2">
          <input
            className="form-check-input"
            type="checkbox"
            checked={inject}
            onChange={toggle}
            id="boostToggle"
          />
          <label className="form-check-label" htmlFor="boostToggle">
            Inject summary into system prompt
          </label>
        </div>
      )}
    </div>
  );
}

BoostSummaryPanel.propTypes = {
  summary: PropTypes.string,
  traits: PropTypes.array,
  demoSlug: PropTypes.string,
  slug: PropTypes.string,
  inject: PropTypes.bool,
};
