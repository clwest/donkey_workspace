import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import apiFetch from "@/utils/apiClient";
import { growthRules } from "../../data/growthRules";

export default function GrowthTrackPanel({ slug, stage, points }) {
  const [info, setInfo] = useState({ stage, points });

  useEffect(() => {
    if (stage !== undefined && points !== undefined) return;
    apiFetch(`/assistants/${slug}/`)
      .then((d) => setInfo({ stage: d.growth_stage, points: d.growth_points }))
      .catch(() => {});
  }, [slug]);

  if (!info || info.stage === undefined) return null;
  const current = growthRules[info.stage] || { label: "" };
  const next = growthRules[info.stage + 1];
  const progress = next
    ? Math.min((info.points / next.threshold) * 100, 100)
    : 100;

  const handleUpgrade = async () => {
    try {
      const res = await apiFetch(
        `/assistants/${slug}/growth_stage/upgrade/`,
        { method: "POST" }
      );
      setInfo({ stage: res.stage, points: res.points });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="card my-3">
      <div className="card-header">Growth Track</div>
      <div className="card-body">
        <p className="mb-2">
          Stage {info.stage}: {current.label}
        </p>
        {next && (
          <>
            <div className="progress mb-2" style={{ height: "1rem" }}>
              <div
                className="progress-bar bg-success"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-muted small">
              {info.points}/{next.threshold} points
            </p>
            {progress >= 100 && (
              <button className="btn btn-primary btn-sm" onClick={handleUpgrade}>
                Level Up
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
}

GrowthTrackPanel.propTypes = {
  slug: PropTypes.string.isRequired,
  stage: PropTypes.number,
  points: PropTypes.number,
};
