import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import AssistantThoughtCard from "../../components/assistant/thoughts/AssistantThoughtCard";
import AssistantMemoryPanel from "../../components/assistant/memory/AssistantMemoryPanel";
import PrimaryStar from "../../components/assistant/PrimaryStar";

export default function PrimaryAssistantDashboard() {
  const [assistant, setAssistant] = useState(null);
  const [delegations, setDelegations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/assistants/primary/");
        setAssistant(res);
        const delRes = await apiFetch("/assistants/primary/delegations/");
        setDelegations(delRes || []);
      } catch (err) {
        console.error("Failed to load primary assistant", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleReflect = async () => {
    if (!assistant) return;
    try {
      const res = await apiFetch("/assistants/primary/reflect-now/", {
        method: "POST",
        body: { memory_id: assistant.recent_thoughts?.[0]?.id },
      });
      setAssistant((prev) => ({
        ...prev,
        recent_thoughts: [
          { content: res.summary, timestamp: new Date().toISOString(), role: "assistant" },
          ...(prev.recent_thoughts || []),
        ],
      }));
    } catch (err) {
      console.error("Reflection failed", err);
      alert("Failed to trigger reflection");
    }
  };

  if (loading) return <div className="container my-5">Loading...</div>;
  if (!assistant) return <div className="container my-5">Primary assistant not found.</div>;

  const thoughts = assistant.recent_thoughts ? assistant.recent_thoughts.slice(0, 5) : [];

  return (
    <div className="container my-5">
      <div className="card mb-4 shadow-sm">
        <div className="card-body d-flex align-items-center">
          {assistant.avatar && (
            <img
              src={assistant.avatar}
              alt="avatar"
              className="rounded-circle me-3"
              width="60"
              height="60"
            />
          )}
          <div>
            <h3 className="mb-0">
              {assistant.name} <PrimaryStar isPrimary={assistant.is_primary} />
              <span className="badge bg-warning text-dark ms-2">Primary</span>
            </h3>
            <p className="text-muted mb-0">{assistant.specialty}</p>
          </div>
          <div className="ms-auto">
            <button className="btn btn-primary" onClick={handleReflect}>
              Reflect Now
            </button>
          </div>
        </div>
      </div>

      <div className="row g-4">
        <div className="col-md-6">
          <h4 className="mb-3">Recent Thoughts</h4>
          {thoughts.length === 0 ? (
            <p>No recent thoughts.</p>
          ) : (
            thoughts.map((t, idx) => (
              <AssistantThoughtCard key={idx} thought={t} />
            ))
          )}
        </div>
        <div className="col-md-6">
          <h4 className="mb-3">Memory</h4>
          <AssistantMemoryPanel slug={assistant.slug} />
          <Link
            to={`/assistants/${assistant.slug}/memories/`}
            className="btn btn-sm btn-outline-secondary mt-2"
          >
            View All Memories
          </Link>
        </div>
      </div>

      <div className="mt-5">
        <h4>Delegation Log</h4>
        {delegations.length === 0 ? (
          <p>No delegation events.</p>
        ) : (
          <ul className="list-group">
            {delegations.map((d, idx) => (
              <li key={idx} className="list-group-item">
                <strong>
                  {d.parent} ➡ {d.child}
                </strong>
                <div>{d.reason}</div>
                {d.summary && <div className="text-muted small">{d.summary}</div>}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
