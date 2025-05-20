import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import DelegationFeedbackModal from "../../components/assistant/DelegationFeedbackModal";
import ToolFeedbackDropdown from "../../components/tools/ToolFeedbackDropdown";

function MemoryRow({ entry, onRate }) {
  const indent = { marginLeft: `${entry.depth * 20}px` };
  return (
    <li style={indent} className="mb-2">
      <div>
        {entry.is_delegated && <span className="me-1">🎯</span>}
        {entry.type === "reflection" && <span className="me-1">🔍</span>}
        <strong>{entry.summary || entry.event}</strong>
        <div className="text-muted small">
          {entry.assistant} {entry.parent && `↳ from ${entry.parent}`}
        </div>
      </div>
      <div className="small">
        <Link to={`/assistants/${entry.assistant_id}`}>View Source Assistant</Link>
        {entry.delegation_event_id && (
          <>
            {" | "}
            <Link to={`/delegations/${entry.delegation_event_id}`}>Jump to Delegation Event</Link>
            {" | "}
            <button
              className="btn btn-sm btn-link p-0"
              onClick={() => onRate(entry.delegation_event_id)}
            >
              📝 Rate This Agent
            </button>
          </>
        )}
        {" | "}
        <Link to={`/assistants/${entry.assistant_id}/reflect`}>Reflect on Sub-Agent Output</Link>
        {entry.tool_usage_id && (
          <>
            {" | "}
            <ToolFeedbackDropdown usageId={entry.tool_usage_id} />
          </>
        )}
      </div>
    </li>
  );
}

export default function DelegationTracePage() {
  const { slug } = useParams();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [feedbackId, setFeedbackId] = useState(null);

  useEffect(() => {
    async function fetchTrace() {
      try {
        const data = await apiFetch(`/assistants/${slug}/hierarchical-memory/`);
        setEntries(data || []);
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
      {entries.length === 0 ? (
        <p>No memories found.</p>
      ) : (
        <ul className="list-unstyled">
          {entries.map((m) => (
            <MemoryRow key={m.id} entry={m} onRate={(id) => setFeedbackId(id)} />
          ))}
        </ul>
      )}
      <Link to={`/assistants/${slug}`} className="btn btn-outline-secondary">
        🔙 Back
      </Link>
      <DelegationFeedbackModal
        eventId={feedbackId}
        show={!!feedbackId}
        onClose={() => setFeedbackId(null)}
      />
    </div>
  );
}
