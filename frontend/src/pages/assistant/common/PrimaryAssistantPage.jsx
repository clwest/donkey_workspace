import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function PrimaryAssistantPage() {
  const [slug, setSlug] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPrimary() {
      try {
        const data = await apiFetch("/assistants/primary/");
        setSlug(data.slug);
      } catch (err) {
        setSlug(null);
      } finally {
        setLoading(false);
      }
    }
    fetchPrimary();
  }, []);

  if (loading) return <div className="container my-5">Loading...</div>;
  if (!slug) return <div className="container my-5">No primary assistant configured.</div>;
  return <Navigate to={`/assistants/${slug}`} replace />;
}
