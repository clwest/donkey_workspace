import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DialogueExchangeStream({ sessionId }) {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    if (!sessionId) return;
    apiFetch(`/simulation/dialogue-exchange/?session=${sessionId}`)
      .then((res) => setMessages(res.results || res))
      .catch(() => setMessages([]));
  }, [sessionId]);

  return (
    <div className="my-2">
      <ul className="list-group">
        {messages.map((m) => (
          <li key={m.id} className="list-group-item">
            <strong>{m.sender}</strong>: {m.message_content}
          </li>
        ))}
        {messages.length === 0 && (
          <li className="list-group-item text-muted">No messages.</li>
        )}
      </ul>
    </div>
  );
}
