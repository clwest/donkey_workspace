import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function SubAgentReflectionPage() {
  useAuthGuard();
  const { slug, event_id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await apiFetch(`/assistants/${slug}/subagent_reflect/${event_id}/`);
        setData(res);
      } catch (err) {
        console.error("Failed to load reflection", err);
        setData({ summary: "Unable to fetch reflection." });
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [slug, event_id]);

  if (loading) return <div className="container my-5">Loading...</div>;

  if (!data) return null;

  return (
    <div className="container my-5">
      <h2 className="mb-4">Sub-Agent Reflection</h2>
      <pre>{data.summary}</pre>
      {data.linked_thoughts && data.linked_thoughts.length > 0 && (
        <>
          <h4 className="mt-4">Linked Thoughts</h4>
          <ul>
            {data.linked_thoughts.map((t, idx) => (
              <li key={idx}>{t}</li>
            ))}
          </ul>
        </>
      )}
      {data.assistant_slug && (
        <Link to={`/assistants/${data.assistant_slug}`} className="btn btn-outline-primary mt-3 me-2">
          View Assistant
        </Link>
      )}
    </div>
  );
}
