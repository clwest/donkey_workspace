// src/pages/assistants/sessions/AssistantSessionDetailPage.jsx
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import MessageCard from "../../../components/assistant/sessions/MessageCard";
import { downloadFile } from "../../../utils/downloadFile";
import CommonModal from "../../../components/CommonModal";
import SessionHandoffModal from "../../../components/assistant/SessionHandoffModal";

export default function AssistantSessionDetailPage() {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showReplay, setShowReplay] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [summary, setSummary] = useState(null);
  const [handoffs, setHandoffs] = useState([]);
  const [showHandoff, setShowHandoff] = useState(false);

  useEffect(() => {
    async function fetchSessionDetail() {
      try {
        const data = await apiFetch(
          `/assistants/sessions/detail/${sessionId}/`
        );
        setSession(data);
        const handData = await apiFetch(`/assistants/handoff/${sessionId}/`);
        setHandoffs(handData || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchSessionDetail();
  }, [sessionId]);
  
  function handleFeedback(uuid, value) {
    if (!uuid) return;
    apiFetch(`/assistants/messages/${uuid}/update/`, {
      method: "PATCH",
      body: { feedback: value },
    }).then(() => {
      setSession((prev) => {
        const updated = {
          ...prev,
          messages: prev.messages.map((msg) =>
            msg.uuid === uuid ? { ...msg, feedback: value } : msg
          ),
        };
        if (prev.token_usage) {
          apiFetch(`/assistants/${prev.assistant_slug}/evaluate-delegation/`, {
            method: "POST",
            body: {
              session_id: prev.session_id,
              token_count: prev.token_usage.total_tokens,
              feedback_flag: value,
            },
          }).then((data) => {
              if (data.should_delegate && data.suggested_agent) {
                alert(`Suggested agent: ${data.suggested_agent}`);
              }
            });
        }
        return updated;
      });
    });
  }
  
  async function handleTopicChange(uuid, topic) {
    if (!uuid) return;
    try {
      await apiFetch(`/assistants/messages/${uuid}/update/`, {
        method: "PATCH",
        body: { topic },
      });
  
      // Update state in real-time
      setSession((prev) => ({
        ...prev,
        messages: prev.messages.map((msg) =>
          msg.uuid === uuid ? { ...msg, topic } : msg
        ),
      }));
    } catch (err) {
      console.error("Error updating topic:", err);
    }
  }
  
  function handleTopicSubmit(uuid, value) {
    if (!uuid) return;
    apiFetch(`/assistants/messages/${uuid}/update/`, {
      method: "PATCH",
      body: { topic: value },
    }).then(() => {
      setSession((prev) => ({
        ...prev,
        messages: prev.messages.map((msg) =>
          msg.uuid === uuid ? { ...msg, topic: value, topicInput: "" } : msg
        ),
      }));
    });
  }

  const copyTranscript = () => {
    const content = JSON.stringify(session, null, 2);
    navigator.clipboard.writeText(content).then(() => {
      alert("Copied session transcript to clipboard!");
    });
  };

  const exportJson = () => {
    const content = JSON.stringify(session, null, 2);
    downloadFile(content, `session_${session.session_id}.json`, "application/json");
  };

  const exportMarkdown = () => {
    const md = [
      `# Session ${session.session_id}`,
      `**Assistant:** ${session.assistant_name}`,
      `**Created:** ${new Date(session.created_at).toLocaleString()}`,
      "",
      "## Messages",
      ...session.messages.map(
        (m) => `### ${m.role} — ${new Date(m.created_at).toLocaleString()}\n\n${m.content}`
      ),
    ].join("\n\n");
    downloadFile(md, `session_${session.session_id}.md`, "text/markdown");
  };

  const loadSummary = async () => {
    if (!session) return;
    try {
      const data = await apiFetch(
        `/assistants/${session.assistant_slug}/session-summary/${sessionId}/`
      );
      setSummary(data.entries || []);
      setShowSummary(true);
    } catch (err) {
      console.error("Failed to load summary", err);
    }
  };

  const handleHandoff = async () => {
    if (!session) return;
    const target = prompt("Target assistant slug?");
    if (!target) return;
    const reason = prompt("Reason for handoff?", "deep reasoning required") || "";
    try {
      await apiFetch(`/assistants/${session.assistant_slug}/handoff/`, {
        method: "POST",
        body: {
          target_slug: target,
          reason,
          session_id: sessionId,
        },
      });
      alert(`Session handed off to ${target}`);
      const res = await apiFetch(`/assistants/sessions/detail/${sessionId}/`);
      setSession(res);
    } catch (err) {
      alert("Handoff failed");
    }
  };

  if (loading) return <div className="container my-5">Loading...</div>;
  if (error) return <div className="container my-5 text-danger">Error: {error}</div>;
  if (!session) return null;

  const hasAudio = session.messages.some((m) => m.audio_url);

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>🧠 Session: {session.session_id}</h2>
        <Link to="/assistants/sessions" className="btn btn-outline-secondary">⬅️ Back</Link>
      </div>

      <div className="mb-4">
        <p><strong>Assistant:</strong> {session.assistant_name}</p>
        <p><strong>Created:</strong> {new Date(session.created_at).toLocaleString()}</p>
        <p><strong>Total Messages:</strong> {session.messages.length}</p>
        {session.token_usage && (
          <span className="badge bg-info me-2">
            📊 Token Usage: {session.token_usage.total_tokens}
          </span>
        )}
        {session.close_to_threshold && (
          <span className="badge bg-warning text-dark ms-2">
            ⚠️ Delegation Soon
          </span>
        )}
        <div className="mt-2">
          <button className="btn btn-sm btn-outline-secondary me-2" onClick={copyTranscript}>
            📋 Copy to Clipboard
          </button>
          <button className="btn btn-sm btn-outline-secondary me-2" onClick={exportJson}>
            ⬇️ Download .json
          </button>
          <button className="btn btn-sm btn-outline-secondary" onClick={exportMarkdown}>
            ⬇️ Download .md
          </button>
          <button
            className="btn btn-sm btn-outline-info ms-2"
            onClick={loadSummary}
          >
            🧠 View Summary Replay
          </button>
          <button
            className="btn btn-sm btn-outline-warning ms-2"
            onClick={handleHandoff}
          >
            🔁 Handoff to Agent
          </button>
          {hasAudio && (
            <button
              className="btn btn-sm btn-outline-primary ms-2"
              onClick={() => setShowReplay(true)}
            >
              🎧 Play Session
            </button>
          )}
        </div>
      </div>

      <div className="chat-box border rounded p-3 bg-light" style={{ maxHeight: "500px", overflowY: "auto" }}>
        {session.messages.map((msg, idx) => (
          <MessageCard
            key={msg.uuid || msg.created_at || idx}
            message={msg}
            onFeedback={handleFeedback}
            onTopicSave={handleTopicChange}
          />
        ))}
      </div>
      <div className="my-4">
        <h5>Handoff History</h5>
        {handoffs.length === 0 ? (
          <p>No handoffs recorded.</p>
        ) : (
          <ul className="list-group">
            {handoffs.map((h) => (
              <li key={h.id} className="list-group-item">
                {h.from_assistant} → {h.to_assistant} – {h.reason}
              </li>
            ))}
          </ul>
        )}
        <button className="btn btn-sm btn-outline-primary mt-2" onClick={() => setShowHandoff(true)}>
          Delegate to Agent
        </button>
      </div>
      <CommonModal
        show={showReplay}
        onClose={() => setShowReplay(false)}
        title="Session Replay"
      >
        {session.messages.map(
          (m, idx) =>
            m.audio_url && (
              <div key={idx} className="mb-3">
                <p className="mb-1">
                  <strong>{m.role}</strong> - {new Date(m.created_at).toLocaleString()}
                </p>
                <audio controls className="w-100">
                  <source src={m.audio_url} />
                </audio>
              </div>
            )
        )}
      </CommonModal>
      <CommonModal
        show={showSummary}
        onClose={() => setShowSummary(false)}
        title="Summary Replay"
      >
        {summary &&
          summary.map((e, idx) => (
            <div key={idx} className="mb-2">
              <div>
                <strong>{e.type === "thought" ? e.assistant : `${e.assistant} → ${e.child}`}</strong>
              </div>
              {e.content && <div>{e.content}</div>}
              {e.reason && <div className="small text-muted">{e.reason}</div>}
            </div>
          ))}
      </CommonModal>
      <SessionHandoffModal
        sessionId={session.session_id}
        show={showHandoff}
        onClose={(didCreate) => {
          setShowHandoff(false);
          if (didCreate) {
            apiFetch(`/assistants/handoff/${sessionId}/`).then(setHandoffs);
          }
        }}
      />
    </div>
  );
}
