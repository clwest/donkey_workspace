import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";

export default function ReflectionTagsPage() {
  const { tag } = useParams();
  const [reflections, setReflections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:8000/api/mcp/reflection-tags/${tag}/`)
      .then(res => res.json())
      .then(data => {
        setReflections(data);
        setLoading(false);
      });
  }, [tag]);

  if (loading) return <div className="container mt-5">Loading reflections...</div>;

  return (
    <div className="container mt-5">
      <h1 className="mb-4">Reflections tagged with "{tag}" 🏷️</h1>

      {reflections.length === 0 ? (
        <p>No reflections found for this tag.</p>
      ) : (
        <div className="list-group">
          {reflections.map(reflection => (
            <Link
              key={reflection.id}
              to={`/reflections/${reflection.id}`}
              className="list-group-item list-group-item-action"
            >
              <div className="d-flex w-100 justify-content-between">
                <h5 className="mb-1">{reflection.title}</h5>
                <small>{reflection.created_at}</small>
              </div>
              <p className="mb-1">{reflection.summary.slice(0, 150)}...</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}