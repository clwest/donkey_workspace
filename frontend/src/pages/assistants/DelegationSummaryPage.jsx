import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function DelegationSummaryPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadSummary = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/assistants/${slug}/summarize_delegations/`, {
        method: "POST",
      });
      setData(res);
    } catch (err) {
      console.error("Failed to summarize delegations", err);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, [slug]);

  if (loading && !data) return <div className="container my-5">Loading...</div>;

  if (!data || !data.summary) {
    return (
      <div className="container my-5">
        <h2 className="mb-4">Delegation Summary</h2>
        <p>No delegation memories yet.</p>
        <button className="btn btn-outline-primary" onClick={loadSummary} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>
    );
  }

  return (
    <div className="container my-5">
      <h2 className="mb-4">Delegation Summary</h2>
      <pre>{data.summary}</pre>
      <button className="btn btn-outline-primary mt-3" onClick={loadSummary} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh"}
      </button>
    </div>
  );
}
