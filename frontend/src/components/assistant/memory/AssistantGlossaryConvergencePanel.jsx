import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function AssistantGlossaryConvergencePanel() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await apiFetch(`/assistants/${slug}/glossary/convergence/`);
        setData(res);
      } catch (err) {
        console.error("Failed to load convergence", err);
        setData(null);
      } finally {
        setLoading(false);
      }
    }
    if (slug) load();
  }, [slug]);

  if (loading) return <div>Loading convergence...</div>;
  if (!data) return <div className="text-danger">Failed to load convergence.</div>;

  return (
    <div className="card mt-3">
      <div className="card-body">
        <h5 className="card-title">Glossary Convergence</h5>
        <div className="d-flex flex-wrap gap-2 mb-2">
          <span className="badge bg-primary">Total {data.total_anchors}</span>
          <span className="badge bg-success">Grounded {data.grounded}</span>
          <span className="badge bg-danger">Failing {data.failing}</span>
          <span className="badge bg-info text-dark">
            Mutations {data.mutated_recently}
          </span>
          <span className="badge bg-secondary">
            Inferred {data.inferred_recently}
          </span>
          <span className="badge bg-warning text-dark">
            {data.convergence_score?.toFixed(1)}% Convergence
          </span>
        </div>
        <Link
          to={`/assistants/${slug}/glossary`}
          className="btn btn-sm btn-outline-primary"
        >
          View Drift
        </Link>
      </div>
    </div>
  );
}
