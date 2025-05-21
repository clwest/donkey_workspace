import { useEffect, useState } from "react";
import { fetchStories } from "../../utils/apiClient";
import { Link } from "react-router-dom";

export default function StoryListPage() {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStories() {
      try {
        const data = await fetchStories();
        const results = data.results || data;
        setStories(results);
      } catch (err) {
        console.error("Failed to load stories", err);
      } finally {
        setLoading(false);
      }
    }
    loadStories();
  }, []);

  return (
    <div className="container py-4">
      <h1 className="mb-4">📚 Stories</h1>
      {loading ? (
        <p className="text-muted">Loading...</p>
      ) : stories.length === 0 ? (
        <p className="text-muted">No stories found.</p>
      ) : (
        <div className="list-group">
          {stories.map((s) => (
            <Link
              key={s.id}
              to={`/storyboard/events/${s.id}`}
              className="list-group-item list-group-item-action"
            >
              <strong>{s.title || s.prompt}</strong>
              {s.image_url && (
                <img
                  src={s.image_url}
                  alt="story"
                  className="img-fluid mt-2"
                />
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
