import { Link } from "react-router-dom";

export default function LinkedChainList({ chains }) {
  if (!chains || chains.length === 0) {
    return <div className="alert alert-secondary">No linked chains.</div>;
  }

  return (
    <ul className="list-group">
      {chains.map((chain) => (
        <li key={chain.id} className="list-group-item">
          <Link to={`/memories/chains/${chain.id}`}>{chain.title}</Link>
          {chain.summary && (
            <p className="mb-1 small text-muted">
              {chain.summary.length > 120
                ? chain.summary.slice(0, 120) + "..."
                : chain.summary}
            </p>
          )}
          {chain.projects && chain.projects.length > 0 && (
            <div className="small text-muted mb-1">
              Projects:{" "}
              {chain.projects.map((p) => (
                <span key={p} className="badge bg-secondary me-1">
                  {p}
                </span>
              ))}
            </div>
          )}
          {chain.assistants && chain.assistants.length > 0 && (
            <div className="small text-muted">
              Assistants:{" "}
              {chain.assistants.map((a) => (
                <span key={a} className="badge bg-info me-1">
                  {a}
                </span>
              ))}
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}
