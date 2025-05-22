import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function CollaborationPanel({ assistantId }) {
  const [ids, setIds] = useState("");
  const [message, setMessage] = useState("");
  const [thread, setThread] = useState(null);

  const start = async () => {
    const assistantIds = ids
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    const payload = {
      assistant_ids: assistantIds,
      messages: message ? [{ role: "user", content: message }] : [],
    };
    const data = await apiFetch(`/assistants/${assistantId}/collaborate/`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setThread(data.thread_id);
  };

  return (
    <div className="mb-3">
      <input
        className="form-control mb-2"
        placeholder="Assistant IDs comma separated"
        value={ids}
        onChange={(e) => setIds(e.target.value)}
      />
      <input
        className="form-control mb-2"
        placeholder="Initial message"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <button className="btn btn-primary" onClick={start}>
        Start Collaboration
      </button>
      {thread && <div className="mt-2">Thread: {thread}</div>}
    </div>
  );
}
