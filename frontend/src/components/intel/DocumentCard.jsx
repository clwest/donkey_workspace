import { Link } from "react-router-dom";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { countTokens } from "../../utils/tokenCount";
import { Badge } from "react-bootstrap";
import { useState } from "react";
import { Star, StarFill } from "react-bootstrap-icons";

dayjs.extend(relativeTime);

const sourceColors = {
  url: "primary",
  pdf: "danger",
  youtube: "dark",
  video: "dark",
  markdown: "warning",
  text: "secondary",
};

export default function DocumentCard({ group, onToggleFavorite, onDelete }) {
  if (!group) return null;

  const {
    id,
    title,
    source_url,
    source_type,
    created_at,
    metadata,
    content,
    is_favorited = false,
  } = group;

  const tokenCount =
    metadata?.token_count || (content ? countTokens(content) : 0);

  const domain = source_url
    ? new URL(source_url).hostname.replace("www.", "")
    : "No URL";

  const [favorite, setFavorite] = useState(is_favorited);

  const handleToggleFavorite = (e) => {
    e.preventDefault();
    const newFavorite = !favorite;
    setFavorite(newFavorite);
    if (onToggleFavorite) onToggleFavorite(id, newFavorite);
  };

  const handleDelete = (e) => {
    e.preventDefault();
    if (!onDelete) return;
    if (window.confirm("Delete this document?")) {
      onDelete(id);
    }
  };

  return (
    <div className="card mb-3 shadow-sm p-3 position-relative h-100">
      <div className="d-flex justify-content-between align-items-start">
        <div>
          <h5 className="mb-1">{title || "Untitled Document"}</h5>
          <small className="text-muted">
            {domain} • {dayjs(created_at).fromNow()}
          </small>
        </div>
        <div className="btn-group">
          <button
            onClick={handleToggleFavorite}
            className="btn btn-sm btn-outline-warning border-0"
            title={favorite ? "Unpin" : "Pin to favorites"}
          >
            {favorite ? <StarFill /> : <Star />}
          </button>
          {onDelete && (
            <button
              onClick={handleDelete}
              className="btn btn-sm btn-outline-danger border-0"
              title="Delete document"
            >
              🗑️
            </button>
          )}
        </div>
      </div>

      <div className="mt-2 text-muted small">
        {tokenCount} tokens
        <Badge bg={sourceColors[source_type] || "secondary"} className="ms-2">
          {source_type?.toUpperCase()}
        </Badge>
      </div>
    </div>
  );
}