import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import TagBadge from "../../../components/TagBadge";

export default function AssistantReflectionListPage() {
  const { slug } = useParams();
  const [reflections, setReflections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/assistants/${slug}/reflections/`);
        setReflections(data || []);
      } catch (err) {
        console.error("Failed to load reflections", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">Reflection Log for {slug}</h2>
        <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
          Back to Assistant
        </Link>
      </div>

      {loading ? (
        <p>Loading reflections...</p>
      ) : reflections.length === 0 ? (
        <p>No reflections found.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Summary</th>
              <th>Memory</th>
              <th>Project</th>
            </tr>
          </thead>
          <tbody>
            {reflections.map((r) => (
              <tr key={r.id}>
                <td>{new Date(r.created_at).toLocaleString()}</td>
                <td>
                  <Link to={`/assistants/reflections/${r.id}`}>{r.summary}</Link>
                  {r.tags && r.tags.length > 0 && (
                    <div className="mt-1">
                      {r.tags.map((t) => (
                        <TagBadge key={t.id} tag={t} className="me-1" />
                      ))}
                    </div>
                  )}
                </td>
                <td>{r.linked_memory || "-"}</td>
                <td>{r.project || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
