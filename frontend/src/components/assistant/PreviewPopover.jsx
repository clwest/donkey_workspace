import { useState } from "react";
import { OverlayTrigger, Popover } from "react-bootstrap";
import PropTypes from "prop-types";
import apiFetch from "../../utils/apiClient";
import "./styles/PreviewPopover.css";

const AVATAR_EMOJI = { owl: "🦚", fox: "🦊", robot: "🤖", wizard: "🧙‍♂️" };

export default function PreviewPopover({ slug, children, placement = "right" }) {
  const [data, setData] = useState(null);
  const [notFound, setNotFound] = useState(false);

  async function load() {
    if (data || notFound || !slug) return;
    try {
      const res = await apiFetch(`/assistants/${slug}/preview/`);
      setData(res);
    } catch (err) {
      if (String(err).includes("404")) {
        setNotFound(true);
      } else {
        console.error("Failed to load preview", err);
      }
    }
  }

  const pop = (
    <Popover className="assistant-preview-popover">
      <Popover.Body>
        {notFound ? (
          <div className="small">Preview unavailable.</div>
        ) : data ? (
          <div style={{ maxWidth: "250px" }}>
            <div className="d-flex align-items-center mb-2">
              {data.avatar ? (
                <img
                  src={data.avatar}
                  alt={data.name}
                  className="rounded-circle me-2"
                  style={{ width: 32, height: 32, objectFit: "cover" }}
                />
              ) : (
                <span className="fs-4 me-2">{AVATAR_EMOJI[data.avatar_style] || "🤖"}</span>
              )}
              <strong>{data.name}</strong>
              {data.flair && <span className="ms-1">{data.flair}</span>}
            </div>
            {data.description && <p className="small mb-1">{data.description}</p>}
            <div className="small">
              <div>🧠 {data.memory_count}</div>
              <div>✨ {data.glossary_score}</div>
              {data.latest_reflection && <div>💬 {data.latest_reflection}</div>}
              {data.starter_memory_excerpt && <div>📜 {data.starter_memory_excerpt}</div>}
            </div>
          </div>
        ) : (
          <div>Loading...</div>
        )}
      </Popover.Body>
    </Popover>
  );

  return (
    <OverlayTrigger
      overlay={pop}
      placement={placement}
      trigger={["hover", "focus"]}
      onToggle={(show) => show && load()}
    >
      {children}
    </OverlayTrigger>
  );
}

PreviewPopover.propTypes = {
  slug: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  placement: PropTypes.string,
};
