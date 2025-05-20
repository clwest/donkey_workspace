import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function AssistantThoughtMap() {
  const { slug } = useParams();
  const [thoughts, setThoughts] = useState([]);
  const [filters, setFilters] = useState({ mood: "", tag: "", feedback: "", start: "", end: "" });

  useEffect(() => {
    fetchMap();
  }, [slug]);

  async function fetchMap() {
    let params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params.append(k, v);
    });
    try {
      const data = await apiFetch(`/assistants/${slug}/thought-map/?` + params.toString());
      setThoughts(data.thoughts || []);
    } catch (err) {
      console.error("Failed to load thought map", err);
    }
  }

  const handleChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleApply = () => fetchMap();

  return (
    <div className="container my-5">
      <h2 className="mb-4">Thought Evolution Map for {slug}</h2>
      <div className="mb-3 d-flex flex-wrap gap-2">
        <input className="form-control" style={{ maxWidth: "120px" }} placeholder="Mood" name="mood" value={filters.mood} onChange={handleChange} />
        <input className="form-control" style={{ maxWidth: "120px" }} placeholder="Tag" name="tag" value={filters.tag} onChange={handleChange} />
        <input className="form-control" style={{ maxWidth: "140px" }} placeholder="Feedback" name="feedback" value={filters.feedback} onChange={handleChange} />
        <input className="form-control" type="date" name="start" value={filters.start} onChange={handleChange} />
        <input className="form-control" type="date" name="end" value={filters.end} onChange={handleChange} />
        <button className="btn btn-outline-primary" onClick={handleApply}>Apply</button>
      </div>
      {thoughts.length === 0 ? (
        <p>No thoughts found.</p>
      ) : (
        <ul className="list-group">
          {thoughts.map((t) => (
            <li key={t.id} className="list-group-item">
              <div>
                <strong>{new Date(t.created_at).toLocaleString()}</strong> - {t.thought}
              </div>
              <div className="small text-muted">
                {t.mood && <span className="me-2">Mood: {t.mood}</span>}
                {t.feedback && <span className="me-2">Feedback: {t.feedback}</span>}
                {t.parent_thought && <span className="me-2">Parent: {t.parent_thought}</span>}
                {t.linked_memory_summary && <span className="me-2">Memory: {t.linked_memory_summary}</span>}
              </div>
            </li>
          ))}
        </ul>
      )}
      <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary mt-3">
        Back
      </Link>
    </div>
  );
}
