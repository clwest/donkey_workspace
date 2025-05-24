import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import {
  fetchFailureLog,
  runSelfAssessment,
  regeneratePlan,
  fetchRecentReflections,
  createPrimaryAssistant,
} from "../../api/assistants";
import ReflectionToastStatus from "../../components/assistant/ReflectionToastStatus";
import AssistantThoughtCard from "../../components/assistant/thoughts/AssistantThoughtCard";
import AssistantMemoryPanel from "../../components/assistant/memory/AssistantMemoryPanel";
import PrioritizedMemoryPanel from "../../components/assistant/memory/PrioritizedMemoryPanel";
import MemoryChainSettingsPanel from "../../components/assistant/memory/MemoryChainSettingsPanel";
import PrimaryStar from "../../components/assistant/PrimaryStar";
import ThoughtCloudPanel from "../../components/assistant/memory/ThoughtCloudPanel";
import MemoryMoodChart from "../../components/assistant/memory/MemoryMoodChart";
import AssistantDashboardHeader from "./AssistantDashboardHeader";
import SelfAssessmentModal from "../../components/assistant/SelfAssessmentModal";
import SceneMatchesPanel from "../../components/assistant/SceneMatchesPanel";

export default function PrimaryAssistantDashboard() {
  const [assistant, setAssistant] = useState(null);
  const [delegations, setDelegations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [memorySummary, setMemorySummary] = useState(null);
  const [memoryCoverage, setMemoryCoverage] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [inbox, setInbox] = useState([]);
  const [outbox, setOutbox] = useState([]);
  const [allAssistants, setAllAssistants] = useState([]);
  const [routingHistory, setRoutingHistory] = useState([]);
  const [failureLog, setFailureLog] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [recipient, setRecipient] = useState("");
  const [assessment, setAssessment] = useState(null);
  const [showAssess, setShowAssess] = useState(false);
  const [reflectionComplete, setReflectionComplete] = useState(false);
  const [toastStatus, setToastStatus] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/assistants/primary/");
        setAssistant(res);
        let thoughtsData = [];
        try {
          thoughtsData = await apiFetch(`/assistants/${res.slug}/thoughts/`);
          // console.log("🧠 Raw thoughts data", thoughtsData);
        } catch (err) {
          console.warn("Failed to load thoughts", err);
        }
        if (Array.isArray(thoughtsData)) {
          res.recent_thoughts = thoughtsData;
          setAssistant(res);
        }
        const delRes = await apiFetch("/assistants/primary/delegations/");
        setDelegations(delRes || []);
        const summary = await apiFetch(`/assistants/${res.slug}/memory/summary/`);
        
        setMemorySummary(summary);
        const docs = await apiFetch(`/assistants/${res.slug}/memory-documents/`);
        if (docs) {
          let total = 0;
          let embedded = 0;
          docs.forEach((d) => {
            total += d.total_chunks;
            embedded += d.embedded_chunks;
          });
          setMemoryCoverage(total ? Math.round((embedded / total) * 100) : 0);
        }
        const inboxData = await apiFetch(`/assistants/relay/inbox/${res.slug}`);
        setInbox(inboxData || []);
        const outData = await apiFetch(`/assistants/relay/outbox/${res.slug}`);
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

  useEffect(() => {
    if (reflectionComplete && assistant) {
      fetchRecentReflections(assistant.slug)
        .then((data) => {
          setAssistant((prev) => ({
            ...prev,
            recent_thoughts: data.thoughts || [],
          }));
        })
        .catch((err) => console.error("Failed to refresh reflections", err));
      setReflectionComplete(false);
    }
  }, [reflectionComplete, assistant]);

  const handleReflect = async () => {
    if (!assistant) return;
    try {
      let memoryId = null;
      if (memorySummary?.most_recent && memorySummary.most_recent.length > 0) {
        memoryId = memorySummary.most_recent[0].id;
      } else {
        const mems = await apiFetch(`/assistants/${assistant.slug}/memories/`);
      
        memoryId = mems?.[0]?.id;
      }

      if (!memoryId) {
        alert("No memories available for reflection");
        return;
      }

      setToastStatus("retry");
      const res = await apiFetch("/assistants/primary/reflect-now/", {
        method: "POST",
        body: { memory_id: memoryId },
      });
      if (res.status === "ok") {
        setToastStatus("success");
        setReflectionComplete(true);
      } else {
        setToastStatus("error");
      }
    } catch (err) {
      console.error("Reflection failed", err);
      setToastStatus("error");
    }
  };

  const handleSendRelay = async () => {
    if (!newMessage || !recipient) return;
    try {
      await apiFetch(`/assistants/${assistant.slug}/relay/`, {
        method: "POST",
        body: { recipient_slug: recipient, message: newMessage },
      });
      const inboxData = await apiFetch(`/assistants/relay/inbox/${assistant.slug}`);
      const outData = await apiFetch(`/assistants/relay/outbox/${assistant.slug}`);
      setInbox(inboxData || []);
      setOutbox(outData || []);
      setNewMessage("");
    } catch (err) {
      alert("Failed to send message");
    }
  };

  const handleSelfAssess = async () => {
    if (!assistant) return;
    try {
      const res = await runSelfAssessment(assistant.slug);
      setAssessment(res);
      setShowAssess(true);
    } catch (err) {
      console.error("Assessment failed", err);
      alert("Failed to run self assessment");
    }
  };

  const handleRegeneratePlan = async () => {
    if (!assistant?.needs_recovery) return;
    try {
      await regeneratePlan(assistant.slug, { approve: true });
      setAssistant((prev) => ({ ...prev, needs_recovery: false, recovered: true }));
    } catch (err) {
      console.error("Regeneration failed", err);
      alert("Failed to regenerate plan");
    }
  };

  const handleCreatePrimary = async () => {
    try {
      const res = await createPrimaryAssistant();
      setAssistant(res);
    } catch (err) {
      console.error("Failed to create primary", err);
      alert("Failed to create primary assistant");
    }
  };

  if (loading) return <div className="container my-5">Loading...</div>;
  if (!assistant)
    return (
      <div className="container my-5 text-center">
        <h4 className="mb-3">No Primary Assistant</h4>
        <button className="btn btn-primary" onClick={handleCreatePrimary}>
          Create Primary Assistant
        </button>
      </div>
    );

  const thoughts = assistant.recent_thoughts ? assistant.recent_thoughts.slice(0, 5) : [];

  return (
    <>
    <div className="container my-5">
      <AssistantDashboardHeader
        assistant={assistant}
        memoryCoverage={memoryCoverage}
        onReflect={handleReflect}
        onSelfAssess={handleSelfAssess}
        onRegeneratePlan={handleRegeneratePlan}
      />
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
              <PrioritizedMemoryPanel slug={assistant.slug} />
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
              <SceneMatchesPanel assistantSlug={assistant.slug} />
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
          <table className="table table-sm mb-4">
            <thead>
              <tr>
                <th>Recipient</th>
                <th>Preview</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {outbox.map((m) => (
                <tr key={m.id}>
                  <td>{m.recipient}</td>
                  <td>{m.content.slice(0, 30)}...</td>
                  <td>
                    {m.responded ? (
                      <>
                        ✨ Responded{' '}
                        {m.thought_log && (
                          <a href={`/thoughts/${m.thought_log}`}>Open</a>
                        )}
                      </>
                    ) : m.delivered ? (
                      <>✅ Delivered ({new Date(m.delivered_at).toLocaleString()})</>
                    ) : (
                      '🕓 Pending'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <h5>Incoming</h5>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>Sender</th>
                <th>Preview</th>
                <th>Status</th>
                <th>Thought</th>
              </tr>
            </thead>
            <tbody>
              {inbox.map((m) => (
                <tr key={m.id}>
                  <td>{m.sender}</td>
                  <td>{m.content.slice(0, 30)}...</td>
                  <td>{m.responded ? '✨ Responded' : m.delivered ? '✅ Delivered' : '🕓 Pending'}</td>
                  <td>
                    {m.thought_log && (
                      <a href={`/thoughts/${m.thought_log}`}>Open</a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
    <SelfAssessmentModal
      show={showAssess}
      onClose={() => setShowAssess(false)}
      result={assessment}
    />
    <ReflectionToastStatus status={toastStatus} />
    </>
  );
}
