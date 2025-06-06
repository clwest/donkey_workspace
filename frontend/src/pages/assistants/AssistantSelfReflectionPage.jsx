import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function AssistantSelfReflectionPage() {
  useAuthGuard();
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await apiFetch(`/assistants/${slug}/reflect_on_self/`);
        setData(res);
      } catch (err) {
        console.error("Failed to load self reflection", err);
        setData(null);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [slug]);

  if (loading) return <div className="container my-5">Loading...</div>;

  if (!data || !data.summary) {
    return (
      <div className="container my-5">
        <h2 className="mb-4">Self Reflection</h2>
        <p>No reflections available for this assistant yet.</p>
      </div>
    );
  }

  return (
    <div className="container my-5">
      <h2 className="mb-4">Self Reflection</h2>
      <pre>{data.summary}</pre>
      {data.tags && data.tags.length > 0 && (
        <p className="mt-3">
          <strong>Tags:</strong> {data.tags.join(", ")}
        </p>
      )}
      {data.updated && (
        <p className="text-muted">Last updated: {new Date(data.updated).toLocaleString()}</p>
      )}
    </div>
  );
}
