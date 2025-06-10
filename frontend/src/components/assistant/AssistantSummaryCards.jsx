import { OverlayTrigger, Tooltip } from "react-bootstrap";
import { Link } from "react-router-dom";
import PropTypes from "prop-types";

export default function AssistantSummaryCards({ summary, slug }) {
  if (!summary) return null;
  const items = [
    {
      key: "memory_count",
      icon: "🧠",
      label: "Memory Entries",
      to: `/assistants/${slug}/memories`,
      tooltip: `${summary.memory_count} total memories`,
    },
    {
      key: "glossary_score",
      icon: "📘",
      label: "Glossary Terms",
      to: `/assistants/${slug}/glossary`,
      tooltip: `Score ${summary.glossary_score}`,
    },
    {
      key: "badge_count",
      icon: "🏅",
      label: "Badges",
      to: `/assistants/${slug}/badges`,
      tooltip: `${summary.badge_count} earned badges`,
    },
    {
      key: "reflection_count",
      icon: "🔍",
      label: "Reflections",
      to: `/assistants/${slug}/reflections`,
      tooltip: `${summary.reflection_count} reflections logged`,
    },
    {
      key: "drifted_anchors",
      icon: "⚠️",
      label: "Drifted Anchors",
      to: `/assistants/${slug}/anchor-health`,
      tooltip: `${summary.drifted_anchors} drift issues`,
    },
  ];
  return (
    <div className="row g-3 mb-3">
      {items.map((i) => (
        <div className="col" key={i.key}>
          <OverlayTrigger
            placement="top"
            overlay={<Tooltip>{i.tooltip}</Tooltip>}
          >
            <Link to={i.to} className="text-decoration-none">
              <div className="card text-center h-100">
                <div className="card-body">
                  <div className="fs-3" role="img" aria-label={i.label}>
                    {i.icon}
                  </div>
                  <div className="h5 mb-0">{summary[i.key]}</div>
                  <small className="text-muted">{i.label}</small>
                </div>
              </div>
            </Link>
          </OverlayTrigger>
        </div>
      ))}
    </div>
  );
}

AssistantSummaryCards.propTypes = {
  summary: PropTypes.object,
  slug: PropTypes.string.isRequired,
};
