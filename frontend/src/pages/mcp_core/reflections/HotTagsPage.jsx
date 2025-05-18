import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

export default function HotTagsPage() {
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:8000/api/mcp/top-tags/`)
      .then(res => res.json())
      .then(data => {
        setTags(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="container mt-5">Loading top tags...</div>;

  return (
    <div className="container mt-5">
      <h1 className="mb-4">🔥 Hot Tags</h1>

      {tags.length === 0 ? (
        <p>No tags found yet.</p>
      ) : (
        <div className="list-group">
          {tags.map(tagData => (
            <Link
              key={tagData.tag}
              to={`/reflection-tags/${tagData.tag}`}
              className="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
            >
              {tagData.tag}
              <span className="badge bg-primary rounded-pill">{tagData.count}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}