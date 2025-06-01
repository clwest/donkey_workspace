import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";

export default function ChatWithAgentPage() {
  const { slug } = useParams();
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const projectId = query.get("project");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(
        `/api/assistants/projects/${projectId}/thoughts/generate/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        }
      );
      if (!res.ok) throw new Error("Failed to get response");

      const data = await res.json();
      const assistantMessage = { role: "assistant", content: data.thought };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError("Error communicating with assistant.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <div className="container my-5">
      <h1>💬 Chat with Assistant: {slug}</h1>

      <div className="chat-box border rounded p-3 mb-3 bg-light" style={{ minHeight: "300px" }}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-2 ${msg.role === "user" ? "text-end" : "text-start"}`}>
            <span className={`badge ${msg.role === "user" ? "bg-primary" : "bg-secondary"}`}>{msg.role}</span>
            <div className="mt-1">{msg.content}</div>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="d-flex gap-2">
        <input
          type="text"
          className="form-control"
          placeholder="Type your message..."
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
