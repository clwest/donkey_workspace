import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { fetchDriftFixes } from "../../api/assistants";

export default function DriftFixLogPanel({ slug }) {
  const [logs, setLogs] = useState([]);
  const [open, setOpen] = useState(false);
  const [paused, setPaused] = useState(false);

  const load = async () => {
    if (!slug || !open) return;
    try {
      const data = await fetchDriftFixes(slug);
      setLogs(data);
      setPaused(false);
    } catch (err) {
      setLogs([]);
      if (err.status === 429) setPaused(true);
    }
  };

  useEffect(() => {
    load();
  }, [slug, open]);

  const grouped = { glossary: [], prompt: [], tone: [] };
  logs.forEach((l) => {
    if (l.glossary_terms && l.glossary_terms.length)
      grouped.glossary.push(l);
    if (l.prompt_sections && l.prompt_sections.length)
      grouped.prompt.push(l);
    if (l.tone_tags && l.tone_tags.length) grouped.tone.push(l);
  });

  return (
    <div className="card mt-3">
      <div
        className="card-header"
        role="button"
        onClick={() => setOpen((v) => !v)}
      >
        <strong>Drift Fix History</strong> <span>{open ? "▲" : "▼"}</span>
      </div>
      {open && (
        <div className="card-body">
          {paused && (
            <div className="text-warning mb-2">Paused due to rate limit</div>
          )}
          {logs.length === 0 && (
            <div className="text-muted">No fixes recorded.</div>
          )}
          {logs.length > 0 && (
            <>
              {Object.entries(grouped).map(([key, items]) => (
                items.length > 0 && (
                  <div key={key} className="mb-2">
                    <h6 className="text-capitalize">{key}</h6>
                    <ul className="small mb-0">
                      {items.map((l) => (
                        <li key={l.id}>
                          {key === "glossary" && l.glossary_terms.join(", ")}
                          {key === "prompt" && l.prompt_sections.join(", ")}
                          {key === "tone" && l.tone_tags.join(", ")}
                          {" – "}
                          {l.session_id ? "wizard" : "manual"}
                        </li>
                      ))}
                    </ul>
                  </div>
                )
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

DriftFixLogPanel.propTypes = {
  slug: PropTypes.string.isRequired,
};
