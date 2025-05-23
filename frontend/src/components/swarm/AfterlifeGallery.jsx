import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AfterlifeGallery() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    apiFetch("/afterlife-registry/")
      .then((res) => setEntries(res.results || res))
      .catch(() => setEntries([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Mythic Afterlife Registry</h5>
      <ul className="list-group">
        {entries.map((e) => (
          <li key={e.id} className="list-group-item">
            <strong>{e.assistant}</strong>
          </li>
        ))}
        {entries.length === 0 && (
          <li className="list-group-item text-muted">No afterlife entries.</li>
        )}
      </ul>
    </div>
  );
}
