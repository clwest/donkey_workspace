import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import "./styles/ReflectionPrimerPanel.css";

const AVATAR_EMOJI = { owl: "🦚", fox: "🦊", robot: "🤖", wizard: "🧙‍♂️" };

export default function ReflectionPrimerPanel({ slug, onDismiss }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!slug) return;
    apiFetch(`/assistants/${slug}/reflection_review_primer/`)
      .then(setData)
      .catch(() => {});
  }, [slug]);

  if (!data) return null;

  const avatar = data.assistant.avatar ? (
    <img
      src={data.assistant.avatar}
      alt="avatar"
      className="rounded-circle me-2"
      width="40"
      height="40"
    />
  ) : (
    <span className="fs-3 me-2">
      {AVATAR_EMOJI[data.assistant.avatar_style] || "🤖"}
    </span>
  );

  const repeated = new Set();
  data.top_anchors.forEach((a) => {
    if (a.count > 1) repeated.add(a.slug);
  });
  const celebration = data.top_anchors.reduce((t, a) => t + a.count, 0) > 10;

  return (
    <div
      className="card shadow-sm p-3 fade-in mb-3"
      data-testid="reflection-primer"
    >
      <div className="d-flex justify-content-between align-items-start mb-2">
        <div className="d-flex align-items-center">
          {avatar}
          <h6 className="mb-0">Recent Reflections</h6>
        </div>
        {onDismiss && <button className="btn-close" onClick={onDismiss} />}
      </div>
      <ul className="list-unstyled small mb-3">
        {data.reflections.map((r) => (
          <li key={r.id} className="mb-2">
            <div>{r.summary}</div>
            <div>
              {r.related_anchors.map((a) => (
                <span
                  key={a}
                  className={`badge bg-secondary me-1 ${
                    repeated.has(a) ? "bg-success" : ""
                  }`}
                >
                  {a}
                </span>
              ))}
            </div>
          </li>
        ))}
      </ul>
      <Link
        to={data.full_view}
        className="btn btn-sm btn-primary"
        onClick={onDismiss}
      >
        Review Full Memory {celebration && <span>🌟</span>}
      </Link>
    </div>
  );
}

ReflectionPrimerPanel.propTypes = {
  slug: PropTypes.string.isRequired,
  onDismiss: PropTypes.func,
};
