import { useEffect, useState, useRef } from "react";
import PropTypes from "prop-types";
import apiFetch from "@/utils/apiClient";
import { exportAssistantTrustIndex } from "@/api/devtools";
import TrustBadge from "./TrustBadge";

export default function AssistantTrustPanel({ slug }) {
  const [data, setData] = useState(null);
  const loadedRef = useRef({});
  useEffect(() => {
    if (!slug || loadedRef.current[slug]) return;
    apiFetch(`/assistants/${slug}/trust_profile/`)
      .then((res) => {
        loadedRef.current[slug] = true;
        setData(res);
      })
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
      <div className="card-body text-center">
        <div className="display-6 fw-bold">
          {data.trust_score}
          <span className="fs-6 ms-1">/100</span>
        </div>
        <div className="mb-2">
          <TrustBadge
            label={
              data.trust_level === "ready"
                ? "trusted"
                : data.trust_level === "needs_attention"
                  ? "unreliable"
                  : "neutral"
            }
          />
          <span className="ms-2">
            {lvl.icon} {lvl.label}
          </span>
        </div>
        <div className="d-flex flex-wrap gap-3 justify-content-center small">
          <div>🏅 Badges: {data.earned_badge_count}</div>
          <div>📚 Precision: {Math.round(data.glossary_hit_ratio * 100)}%</div>
          <div>🛠️ Stability: {data.drift_fix_count}</div>
          <div>🧠 Insight Rate: {data.reflections_last_7d}</div>
        </div>
        <button
          className="btn btn-sm btn-outline-primary mt-3"
          onClick={() => exportAssistantTrustIndex(slug)}
        >
          📤 Export Trust Index
        </button>
      </div>
    </div>
  );
}

AssistantTrustPanel.propTypes = {
  slug: PropTypes.string.isRequired,
};
