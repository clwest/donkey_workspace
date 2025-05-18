// src/pages/assistants/sessions/AssistantSessionDetailPage.jsx
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import MessageCard from "../../../components/assistant/sessions/MessageCard";

export default function AssistantSessionDetailPage() {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  if (loading) return <div className="container my-5">Loading...</div>;
  if (error) return <div className="container my-5 text-danger">Error: {error}</div>;
  if (!session) return null;

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>🧠 Session: {session.id}</h2>
        <Link to="/assistants/sessions" className="btn btn-outline-secondary">⬅️ Back to Sessions</Link>
      </div>

      <div className="mb-4">
        <p><strong>Assistant:</strong> {session.assistant_name}</p>
        <p><strong>Created:</strong> {new Date(session.created_at).toLocaleString()}</p>
        <p><strong>Total Messages:</strong> {session.messages.length}</p>
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
    </div>
  );
}
