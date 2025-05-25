import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PromptCapsuleList() {
  const [capsules, setCapsules] = useState([]);

  useEffect(() => {
    apiFetch("/prompts/capsules/")
      .then((res) => setCapsules(res.results || res))
      .catch(() => setCapsules([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Prompt Capsules</h5>
      <ul className="list-group">
        {capsules.map((c) => (
          <li key={c.id} className="list-group-item">
            {c.title}
          </li>
        ))}
        {capsules.length === 0 && (
          <li className="list-group-item text-muted">No capsules.</li>
        )}
      </ul>
    </div>
  );
}
