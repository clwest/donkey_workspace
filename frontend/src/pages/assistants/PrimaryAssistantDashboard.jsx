import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import { fetchFailureLog } from "../../api/assistants";
import AssistantThoughtCard from "../../components/assistant/thoughts/AssistantThoughtCard";
import AssistantMemoryPanel from "../../components/assistant/memory/AssistantMemoryPanel";
import MemoryChainSettingsPanel from "../../components/assistant/memory/MemoryChainSettingsPanel";
import PrimaryStar from "../../components/assistant/PrimaryStar";
import ThoughtCloudPanel from "../../components/assistant/memory/ThoughtCloudPanel";
import MemoryMoodChart from "../../components/assistant/memory/MemoryMoodChart";

export default function PrimaryAssistantDashboard() {
  const [assistant, setAssistant] = useState(null);
  const [delegations, setDelegations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [memorySummary, setMemorySummary] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [inbox, setInbox] = useState([]);
  const [outbox, setOutbox] = useState([]);
  const [allAssistants, setAllAssistants] = useState([]);
  const [routingHistory, setRoutingHistory] = useState([]);
  const [failureLog, setFailureLog] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [recipient, setRecipient] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/assistants/primary/");
        setAssistant(res);
        const delRes = await apiFetch("/assistants/primary/delegations/");
        setDelegations(delRes || []);
        const summary = await apiFetch(`/assistants/${res.slug}/memory/summary/`);
        setMemorySummary(summary);
        const inboxData = await apiFetch(`/assistants/messages/inbox/${res.slug}`);
        setInbox(inboxData || []);
        const outData = await apiFetch(`/assistants/messages/outbox/${res.slug}`);
        setOutbox(outData || []);
        const all = await apiFetch("/assistants/");
        setAllAssistants(all);
        const history = await apiFetch("/assistants/routing-history/?assistant=" + res.slug);
        setRoutingHistory(history.results || []);
        const failures = await fetchFailureLog(res.slug);
        setFailureLog(failures || []);
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

  const handleSendRelay = async () => {
    if (!newMessage || !recipient) return;
    try {
      await apiFetch("/assistants/messages/send/", {
        method: "POST",
        body: { sender: assistant.slug, recipient, content: newMessage },
      });
      const inboxData = await apiFetch(`/assistants/messages/inbox/${assistant.slug}`);
      const outData = await apiFetch(`/assistants/messages/outbox/${assistant.slug}`);
      setInbox(inboxData || []);
      setOutbox(outData || []);
      setNewMessage("");
    } catch (err) {
      alert("Failed to send message");
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
      <div className="mb-3">
        <ul className="nav nav-tabs">
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "overview" ? "active" : ""}`}
              onClick={() => setActiveTab("overview")}
            >
              Overview
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "relay" ? "active" : ""}`}
              onClick={() => setActiveTab("relay")}
            >
              🛰️ Relay
            </button>
          </li>
        </ul>
      </div>

      {activeTab === "overview" && (
        <>
          <div className="row g-4">
            <div className="col-md-6">
              <h5 className="mb-3">Recent Thoughts</h5>
              {thoughts.length === 0 ? (
                <p>No thoughts yet! 😴</p>
              ) : (
                thoughts.map((t, idx) => (
                  <AssistantThoughtCard key={idx} thought={t} />
                ))
              )}
            </div>
            <div className="col-md-6">
              <h5 className="mb-3">Memory</h5>
              <AssistantMemoryPanel slug={assistant.slug} />
              <MemoryChainSettingsPanel slug={assistant.slug} />
              <Link
                to={`/assistants/${assistant.slug}/memories/`}
                className="btn btn-sm btn-outline-secondary mt-2"
              >
                View All Memories
              </Link>
              {memorySummary && (
                <div className="mt-3">
                  <button
                    className="btn btn-sm btn-outline-info mb-2"
                    data-bs-toggle="collapse"
                    data-bs-target="#memoryPulse"
                  >
                    🧠 Memory Pulse
                  </button>
                  <div className="collapse" id="memoryPulse">
                    <ThoughtCloudPanel tagCounts={memorySummary.recent_tags} />
                    <MemoryMoodChart moodCounts={memorySummary.recent_moods} />
                    <Link to={`/assistants/${assistant.slug}/memories/`} className="btn btn-sm btn-link">Full Visualizer</Link>
                  </div>
                </div>
              )}
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
                      {d.parent} ➡ {" "}
                      <Link to={`/assistants/${d.child_slug}`}>{d.child}</Link>
                    </strong>
                    {d.objective_title && (
                      <div className="small">Objective: {d.objective_title}</div>
                    )}
                    <div>{d.reason}</div>
                    {d.summary && <div className="text-muted small">{d.summary}</div>}
                  </li>
              ))}
            </ul>
          )}
        </div>
        <div className="mt-4">
          <h4>Recent Routing</h4>
          {routingHistory.length === 0 ? (
            <p>No routing suggestions.</p>
          ) : (
            <ul className="list-group">
              {routingHistory.slice(0, 5).map((r) => (
                <li key={r.id} className="list-group-item d-flex justify-content-between">
                  <span>{r.assistant || "none"}</span>
                  <span className="badge bg-secondary">{r.confidence_score.toFixed(2)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="mt-4">
          <h4>Failure Log</h4>
          {failureLog.length === 0 ? (
            <p>No failures detected.</p>
          ) : (
            <ul className="list-group">
              {failureLog.map((f) => (
                <li key={f.id} className="list-group-item">
                  <div className="small text-muted">{new Date(f.created_at).toLocaleString()}</div>
                  {f.text}
                </li>
              ))}
            </ul>
          )}
        </div>
      </>
    )}

      {activeTab === "relay" && (
        <div className="mt-4">
          <div className="mb-3">
            <select
              className="form-select mb-2"
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
            >
              <option value="">Select Assistant...</option>
              {allAssistants
                .filter((a) => a.slug !== assistant.slug)
                .map((a) => (
                  <option key={a.id} value={a.slug}>
                    {a.name}
                  </option>
                ))}
            </select>
            <textarea
              className="form-control mb-2"
              rows="3"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type a message..."
            ></textarea>
            <button className="btn btn-primary" onClick={handleSendRelay}>
              Send
            </button>
          </div>
          <h5>Outgoing</h5>
          <ul className="list-group mb-4">
            {outbox.map((m) => (
              <li key={m.id} className="list-group-item">
                to {m.recipient} - {m.content} ({m.status})
              </li>
            ))}
          </ul>
          <h5>Incoming</h5>
          <ul className="list-group">
            {inbox.map((m) => (
              <li key={m.id} className="list-group-item">
                from {m.sender} - {m.content} ({m.status})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
