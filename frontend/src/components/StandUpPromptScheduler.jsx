import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function StandUpPromptScheduler({ assistantId }) {
  const [time, setTime] = useState("09:00");
  const [status, setStatus] = useState(null);

  const save = async () => {
    const res = await apiFetch(`/assistants/${assistantId}/schedule-standup/`, {
      method: "POST",
      body: { time },
    });
    setStatus(res.status);
  };

  return (
    <div className="mt-3">
      <input
        type="time"
        value={time}
        onChange={(e) => setTime(e.target.value)}
        className="form-control w-auto d-inline-block me-2"
      />
      <button className="btn btn-secondary" onClick={save}>
        Schedule Stand-Up
      </button>
      {status && <span className="ms-2 text-success">{status}</span>}
    </div>
  );
}
