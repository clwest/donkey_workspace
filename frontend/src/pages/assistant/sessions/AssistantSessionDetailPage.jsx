// src/pages/assistants/sessions/AssistantSessionDetailPage.jsx
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import MessageCard from "../../../components/assistant/sessions/MessageCard";
import { downloadFile } from "../../../utils/downloadFile";
import CommonModal from "../../../components/CommonModal";

export default function AssistantSessionDetailPage() {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showReplay, setShowReplay] = useState(false);

  useEffect(() => {
    async function fetchSessionDetail() {
      try {
        const res = await fetch(`http://localhost:8000/api/assistants/sessions/detail/${sessionId}/`);
        if (!res.ok) throw new Error("Failed to fetch session details");
        const data = await res.json();
        setSession(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchSessionDetail();
  }, [sessionId]);
  
  function handleFeedback(uuid, value) {
    fetch(`http://localhost:8000/api/assistants/messages/${uuid}/update/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback: value }),
    }).then(() => {
      setSession((prev) => ({
        ...prev,
        messages: prev.messages.map((msg) =>
          msg.uuid === uuid ? { ...msg, feedback: value } : msg
        ),
      }));
    });
  }
  
  async function handleTopicChange(uuid, topic) {
    try {
      await fetch(`http://localhost:8000/api/assistants/messages/${uuid}/update/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
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
    fetch(`http://localhost:8000/api/assistants/messages/${uuid}/update/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: value }),
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
        {session.messages.map((msg) => (
          <MessageCard
            key={msg.uuid}
            message={msg}
            onFeedback={handleFeedback}
            onTopicSave={handleTopicChange}
          />
        ))}
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
    </div>
  );
}
