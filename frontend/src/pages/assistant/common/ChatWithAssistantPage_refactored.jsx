import { useState, useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import "./styles/ChatView.css";

export default function ChatWithAssistantPage() {
  const { slug } = useParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

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
        body: JSON.stringify({ message: input }),
      });

      if (!res.ok) throw new Error("Failed to send message");
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "user", content: input, timestamp: new Date().toISOString() },
        { role: "assistant", content: data.response, timestamp: new Date().toISOString() },
      ]);
      console.log(data)
      setInput("");
    } catch (err) {
      setError("⚠️ Failed to send message.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchSession = async () => {
      // Removed __ping__ logic; backend no longer supports message history.
      setMessages([]);
      const res = await fetch(`/api/assistants/${slug}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "__ping__" }),
      });

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "user", content: input, timestamp: new Date().toISOString() },
        { role: "assistant", content: data.response, timestamp: new Date().toISOString() },
      ]);
    };

    fetchSession();
  }, [slug]);

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

      {error && <div className="alert alert-danger mt-3">{error}</div>}
    </div>
  );
}