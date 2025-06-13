import { useEffect, useState, useRef } from "react";
import PropTypes from "prop-types";
import apiFetch from "../../utils/apiClient";

export default function AssistantReflectionPanel({ slug }) {
  const [groups, setGroups] = useState([]);
  const [expanded, setExpanded] = useState({});
  const [loading, setLoading] = useState(true);
  const [paused, setPaused] = useState(false);
  const lastRef = useRef(0);

  useEffect(() => {
    if (!slug) return;
    async function load() {
      if (Date.now() - lastRef.current < 1000) return;
      lastRef.current = Date.now();
      setLoading(true);
      try {
        const data = await apiFetch(`/assistants/${slug}/recent-reflections/`);
        const grouped = {};
        data.forEach((item) => {
          const key = item.group_slug || "default";
          if (!grouped[key]) grouped[key] = [];
          grouped[key].push(item);
        });
        setGroups(Object.entries(grouped).map(([k, items]) => ({ slug: k, items })));
      } catch (err) {
        if (err.status === 429) {
          setPaused(true);
        }
        console.error("Failed to load reflections", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  if (loading) return <div>Loading reflections...</div>;
  if (groups.length === 0) return <div>No reflections.</div>;

  return (
    <div className="mt-3">
      <h5 className="mb-2">Recent Reflections</h5>
      {paused && (
        <div className="alert alert-warning">Paused due to rate limit</div>
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
