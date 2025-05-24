import { Link } from "react-router-dom";

export default function RelayChainNodeCard({ node }) {
  const statusIcons = {
    pending: "\uD83D\uDD53", // 🕓
    delivered: "\u2705", // ✅
    reflected: "\u2728", // ✨
    failed: "\u26A0\uFE0F", // ⚠️
  };

  return (
    <div className="card mb-3">
      <div className="card-body">
        <h5 className="card-title">
          {statusIcons[node.status] || "❔"} {node.assistant}
        </h5>
        {node.message && <p className="card-text">{node.message}</p>}
        {node.timestamp && (
          <p className="card-text">
            <small className="text-muted">
              {new Date(node.timestamp).toLocaleString()}
            </small>
          </p>
        )}
        {node.codex && (
          <div className="small text-muted">Codex: {node.codex}</div>
        )}
        {node.prompt_id && (
          <div className="small text-muted">Prompt: {node.prompt_id}</div>
        )}
        {node.fallback && (
          <div className="small text-danger">Fallback route used</div>
        )}
        {node.thought_log_id && (
          <Link to={`/thoughts/${node.thought_log_id}`}>View Thought Log</Link>
        )}
      </div>
    </div>
  );
}
