import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function BookmarkedMemoriesPage() {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      const data = await apiFetch("/memory/bookmarked/");
      setMemories(data);
      setLoading(false);
    }
    fetchData();
  }, []);

  if (loading) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-4">⭐️ Bookmarked Memories</h2>
      {memories.length === 0 ? (
        <p>No bookmarked memories.</p>
      ) : (
        <ul className="list-group">
          {memories.map((m) => (
            <li key={m.id} className="list-group-item d-flex justify-content-between align-items-start">
              <div>
                <Link to={`/memories/${m.id}`} className="fw-bold">
                  {m.summary || m.event || "Untitled Memory"}
                </Link>
                {m.bookmark_label && (
                  <div className="text-muted small">{m.bookmark_label}</div>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

