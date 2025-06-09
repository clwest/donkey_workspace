import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import apiFetch from "@/utils/apiClient";
import TrustBadge from "./TrustBadge";

export default function AssistantTrustPanel({ slug }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    if (!slug) return;
    apiFetch(`/assistants/${slug}/trust_profile/`)
      .then(setData)
      .catch(() => {});
  }, [slug]);

  if (!data) return null;
  const levelMap = {
    ready: { icon: "🟢", label: "Ready" },
    training: { icon: "🟡", label: "Training" },
    needs_attention: { icon: "🔴", label: "Needs Work" },
  };
  const lvl = levelMap[data.trust_level] || levelMap.training;
  return (
    <div className="card my-3">
      <div className="card-header">Trust &amp; Signals</div>
      <div className="card-body">
        <h6 className="mb-2">
          {lvl.icon} {lvl.label} – {data.trust_score}/100
          <TrustBadge label={data.trust_level === "ready" ? "trusted" : data.trust_level === "needs_attention" ? "unreliable" : "neutral"} />
        </h6>
        <div className="d-flex flex-wrap gap-3 small">
          <div>📚 Glossary Hits: {Math.round(data.glossary_hit_ratio * 100)}%</div>
          <div>🧠 Reflections 7d: {data.reflections_last_7d}</div>
          <div>🛠️ Drift Fixes: {data.drift_fix_count}</div>
          <div>🏅 Badges: {data.earned_badge_count}</div>
        </div>
      </div>
    </div>
  );
}

AssistantTrustPanel.propTypes = {
  slug: PropTypes.string.isRequired,
};
