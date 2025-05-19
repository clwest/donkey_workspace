import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

function TraceNode({ node }) {
  return (
    <li>
      <strong>
        <Link to={`/assistants/${node.child_slug}`}>{node.child}</Link>
      </strong>
      {node.reason && <div>{node.reason}</div>}
      {node.summary && <div className="text-muted small">{node.summary}</div>}
      {node.delegations && node.delegations.length > 0 && (
        <ul className="ms-4">
          {node.delegations.map((child, idx) => (
            <TraceNode key={idx} node={child} />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function DelegationTracePage() {
  const { slug } = useParams();
  const [trace, setTrace] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTrace() {
      try {
        const data = await apiFetch(`/assistants/${slug}/delegation-trace/`);
        setTrace(data);
      } catch (err) {
        console.error("Failed to load trace", err);
      } finally {
        setLoading(false);
      }
    }
    fetchTrace();
  }, [slug]);

  if (loading) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-4">Delegation Trace for {slug}</h2>
      {trace.length === 0 ? (
        <p>No delegations found.</p>
      ) : (
        <ul className="list-unstyled">
          {trace.map((node, idx) => (
            <TraceNode key={idx} node={node} />
          ))}
        </ul>
      )}
      <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
        🔙 Back
      </Link>
    </div>
  );
}
