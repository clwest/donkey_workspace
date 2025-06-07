import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import { OverlayTrigger, Tooltip } from "react-bootstrap";

export default function BadgePreviewPanel({ slug }) {
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    apiFetch(`/badges/?assistant=${slug}`)
      .then((res) => {
        const items = res.badges || res; // support old format
        setBadges(items);
        setError(false);
      })
      .catch(() => {
        setBadges([]);
        setError(true);
      })
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return <div>Loading badges...</div>;
  if (error) return <div className="alert alert-warning">Failed to load badges.</div>;
  if (!badges.length) return <div className="text-muted">No badges yet.</div>;

  return (
    <div>
      <h5 className="mb-2">Skill Badges</h5>
      <div className="d-flex flex-wrap gap-2">
        {badges.map((b) => (
          <OverlayTrigger
            key={b.slug}
            placement="top"
            overlay={<Tooltip>{b.description}</Tooltip>}
          >
            <div
              className={
                "p-2 border rounded text-center" +
                (b.earned ? " bg-success text-light" : " bg-light text-muted")
              }
              style={{ width: "6rem" }}
            >
              <div style={{ fontSize: "1.5rem" }} role="img" aria-label={b.label}>
                {b.emoji}
              </div>
              <small>{b.label}</small>
              {typeof b.progress_percent === "number" && !b.earned && (
                <div className="progress mt-1" style={{ height: "4px" }}>
                  <div
                    className="progress-bar"
                    style={{ width: `${b.progress_percent}%` }}
                  ></div>
                </div>
              )}
            </div>
          </OverlayTrigger>
        ))}
      </div>
    </div>
  );
}
