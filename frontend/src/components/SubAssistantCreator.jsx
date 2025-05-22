import { useState } from "react";
import apiFetch from "../utils/apiClient";

export default function SubAssistantCreator({ assistantId, documents }) {
  const [selected, setSelected] = useState([]);
  const [createdId, setCreatedId] = useState(null);

  const toggleDoc = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    );
  };

  const handleCreate = async () => {
    const res = await apiFetch(`/assistants/${assistantId}/sub-assistants/`, {
      method: "POST",
      body: { document_ids: selected },
    });
    setCreatedId(res.sub_assistant_id);
  };

  return (
    <div>
      <ul className="list-unstyled">
        {documents.map((d) => (
          <li key={d.id}>
            <label>
              <input
                type="checkbox"
                checked={selected.includes(d.id)}
                onChange={() => toggleDoc(d.id)}
              />
              {d.title}
            </label>
          </li>
        ))}
      </ul>
      <button className="btn btn-primary" onClick={handleCreate} disabled={!selected.length}>
        Create Sub-Assistant
      </button>
      {createdId && <p className="mt-2">Created: {createdId}</p>}
    </div>
  );
}
