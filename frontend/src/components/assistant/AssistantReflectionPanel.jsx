import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import useAssistantDetails from "../../hooks/useAssistantDetails";

export default function AssistantReflectionPanel({ slug }) {
  const [groups, setGroups] = useState([]);
  const [expanded, setExpanded] = useState({});
  const [autoRetry, setAutoRetry] = useState(false);
  const { reflections, paused, refreshAll } = useAssistantDetails(slug, {
    pauseOnError: true,
  });
  const loading = !reflections;

  useEffect(() => {
    if (!reflections) return;
    const grouped = {};
    reflections.forEach((item) => {
      const key = item.group_slug || "default";
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(item);
    });
    setGroups(
      Object.entries(grouped).map(([k, items]) => ({ slug: k, items })),
    );
  }, [reflections]);

  useEffect(() => {
    if (autoRetry && paused) {
      const id = setTimeout(() => refreshAll(), 10000);
      return () => clearTimeout(id);
    }
  }, [autoRetry, paused, refreshAll]);

  if (loading) return <div>Loading reflections...</div>;
  if (groups.length === 0) return <div>No reflections.</div>;

  return (
    <div className="mt-3">
      <h5 className="mb-2">Recent Reflections</h5>
      {paused && (
        <div className="alert alert-warning d-flex align-items-center">
          Paused due to rate limit
          <div className="form-check form-switch ms-2">
            <input
              className="form-check-input"
              type="checkbox"
              id="reflAuto"
              checked={autoRetry}
              onChange={(e) => setAutoRetry(e.target.checked)}
            />
            <label className="form-check-label" htmlFor="reflAuto">
              Auto Retry
            </label>
          </div>
        </div>
      )}
      <ul className="list-group">
        {groups.slice(0, 5).map((g) => (
          <li key={g.slug} className="list-group-item">
            <div
              className="d-flex justify-content-between"
              style={{ cursor: "pointer" }}
              onClick={() => setExpanded((e) => ({ ...e, [g.slug]: !e[g.slug] }))}
            >
              <span>{g.slug}</span>
              <span className="badge bg-secondary">{g.items.length}</span>
            </div>
            {expanded[g.slug] && (
              <ul className="list-unstyled mt-2">
                {g.items.map((r) => (
                  <li key={r.id} className="mb-1">
                    {r.is_summary && <span className="badge bg-info me-1">summary</span>}
                    {r.document_title && (
                      <span className="badge bg-light text-dark me-1">{r.document_title}</span>
                    )}
                    {r.summary}
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

AssistantReflectionPanel.propTypes = {
  slug: PropTypes.string.isRequired,
};
