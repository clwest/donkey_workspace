// components/mcp_core/ThreadCard.jsx

import React from "react";
import { Link } from "react-router-dom";
import TagBadge from "../TagBadge"; 

function ThreadCard({ thread }) {
  if (!thread) return null;

  const {
    id,
    title,
    summary,
    tags = [],
    created_at,
    origin_memory,
  } = thread;

  const formattedDate = created_at
    ? new Date(created_at).toLocaleDateString()
    : "";

  return (
    <div className="card mb-3 shadow-sm">
      <div className="card-body">
        <h5 className="card-title mb-1">
          <Link to={`/threads/${id}`}>{title}</Link>
        </h5>
        <p className="card-text text-muted small">{formattedDate}</p>
        <p className="card-text">{summary}</p>

        {tags.length > 0 && (
          <div className="mb-2">
            {tags.map((tag) => (
              <TagBadge key={tag.slug || tag.id || tag.name} tag={tag} />
            ))}
          </div>
        )}

        {origin_memory?.text && (
          <blockquote className="blockquote mb-0 small text-muted">
            <em>"{origin_memory.text.slice(0, 120)}..."</em>
          </blockquote>
        )}
      </div>
    </div>
  );
}

export default ThreadCard;