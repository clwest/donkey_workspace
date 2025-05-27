import { useState, useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { suggestAssistant, suggestSwitch, switchAssistant } from "../../../api/assistants";
import "./styles/ChatView.css";

export default function ChatWithAssistantPage() {
  const { slug } = useParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [switchSuggestion, setSwitchSuggestion] = useState(null);
  const [sessionId] = useState(() => crypto.randomUUID());
  const messagesEndRef = useRef(null);
  const [sourceInfo, setSourceInfo] = useState(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`/api/assistants/${slug}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, session_id: sessionId }),
      });

      if (!res.ok) throw new Error("Failed to send message");
      const data = await res.json();
      const msgs = data.messages || [];
      if (msgs.length && data.rag_meta) {
        const last = msgs[msgs.length - 1];
        if (last.role === "assistant") {
          last.rag_used = data.rag_meta.rag_used;
          last.used_chunks = data.rag_meta.used_chunks || [];
          last.rag_ignored_reason = data.rag_meta.rag_ignored_reason;
          last.rag_fallback = data.rag_meta.rag_fallback;
        }
        setSourceInfo(data.rag_meta);
      }
      setMessages(msgs);
      console.log(data);
      setInput("");
    } catch (err) {
      setError("⚠️ Failed to send message.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchSession = async () => {
      const res = await fetch(`/api/assistants/${slug}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "__ping__", session_id: sessionId }),
      });

      const data = await res.json();
      setMessages(data.messages || []);
    };

    fetchSession();
  }, [slug]);

  const handleSuggest = async () => {
    try {
      const summary = messages.map((m) => m.content).join(" ");
      const data = await suggestAssistant({
        context_summary: summary.slice(-500),
        tags: [],
        recent_messages: messages.slice(-5),
      });
      if (data.suggested_assistant) {
        alert(`Try: ${data.suggested_assistant.name}\nReason: ${data.reasoning}`);
      } else {
        alert("No suggestion available");
      }
    } catch (err) {
      alert("Failed to get suggestion");
    }
  };

  const handleSwitchSuggest = async () => {
    try {
      const data = await suggestSwitch(sessionId);
      if (data.suggested_assistant) {
        const a = data.suggested_assistant;
        if (window.confirm(`Switch to ${a.name}?\nReason: ${a.reason}`)) {
          const res = await switchAssistant(sessionId, a.slug);
          window.location.href = `/assistants/${a.slug}/chat/`;
        }
      } else {
        alert("No switch suggested");
      }
    } catch (err) {
      alert("Failed to suggest switch");
    }
  };

  const handleCheckSource = async (text) => {
    try {
      const res = await fetch("/api/rag/check-source/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assistant_id: slug, content: text, mode: "response" }),
      });
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        const top = data.results[0];
        alert(`Top match ${Math.round(top.similarity_score * 100)}%\n${top.text.slice(0, 120)}...`);
      } else {
        alert("No matching source chunk found.");
      }
    } catch (err) {
      alert("Failed to check source");
    }
  };

  return (
    <div className="container my-5">
      <h1>💬 Chat with Assistant: <span className="text-primary">{slug}</span></h1>

      <div className="chat-box border rounded p-3 mb-4 bg-light" style={{ maxHeight: "500px", overflowY: "auto" }}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-4 ${msg.role === "user" ? "text-end" : "text-start"}`}>
            <div className="d-flex justify-content-between">
              <span className={`badge ${msg.role === "user" ? "bg-primary" : "bg-secondary"}`}>
                {msg.role}
              </span>
              <small className="text-muted ms-2">{new Date(msg.timestamp).toLocaleString()}</small>
            </div>

            <div className="mt-2 text-break">
              {msg.content?.split("\n").map((line, i) =>
                line.trim() === "" ? <br key={i} /> : <p key={i} className="mb-1">{line}</p>
              )}
            </div>

            {msg.tags?.length > 0 && (
              <div className="mt-1">
                {msg.tags.map((tag, i) => (
                  <span key={i} className="badge rounded-pill bg-info text-dark me-1">
                    #{tag}
                  </span>
                ))}
              </div>
            )}

            {msg.role === "assistant" && (
              <div className="mt-1">
                {msg.rag_fallback && (msg.used_chunks?.[0]?.score || 0) < 0.6 ? (
                  <span className="badge bg-warning text-dark">⚠️ Weak Context</span>
                ) : msg.rag_used ? (
                  (msg.used_chunks?.[0]?.score || 0) >= 0.75 ? (
                    <span className="badge bg-success">🔗 Good Source</span>
                  ) : null
                ) : (
                  <span className="badge bg-danger">🚫 No Source Used</span>
                )}
              </div>
            )}

            <button
              className="btn btn-sm btn-outline-info mt-1"
              onClick={() => handleCheckSource(msg.content)}
            >
              📄 Check Source
            </button>

            {msg.memory_id && (
              <div className="mt-2">
                <Link to={`/memory/${msg.memory_id}`} className="btn btn-sm btn-outline-dark">
                  🧠 View Memory
                </Link>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="d-flex gap-2">
        <input
          type="text"
          className="form-control"
          placeholder="Ask something..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button className="btn btn-success" type="submit" disabled={loading}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>
      {sourceInfo && (
        <div className="mt-2">
          {sourceInfo.rag_fallback &&
          (sourceInfo.used_chunks?.[0]?.score || 0) < 0.6 ? (
            <span className="badge bg-warning text-dark">⚠️ Weak Context</span>
          ) : sourceInfo.rag_used ? (
            (sourceInfo.used_chunks?.[0]?.score || 0) >= 0.75 ? (
              <span className="badge bg-success">🔗 Good Source</span>
            ) : null
          ) : (
            <span className="badge bg-danger">🚫 No Source Used</span>
          )}
        </div>
      )}
      <button className="btn btn-outline-primary mt-2" onClick={handleSuggest}>
        🤖 Suggest Assistant
      </button>
      <button className="btn btn-outline-warning mt-2 ms-2" onClick={handleSwitchSuggest}>
        🔄 Suggest Switch
      </button>

      {error && <div className="alert alert-danger mt-3">{error}</div>}
    </div>
  );
}