import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythWeaverStudio() {
  const [protocols, setProtocols] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/myth-weaving/");
        setProtocols(res.results || res);
      } catch (err) {
        console.error("Failed to load myth protocols", err);
      }
    }
    load();
  }, []);

  return (
    <div className="my-3">
      <h5>Myth Weaver Studio</h5>
      <ul className="list-group">
        {protocols.map((p) => (
          <li key={p.id} className="list-group-item">
            <strong>{p.narrative_theme}</strong>
            <p className="mb-1 small">{p.final_myth_product?.slice(0, 80)}</p>
          </li>
        ))}
        {protocols.length === 0 && (
          <li className="list-group-item text-muted">No myth weaving sessions.</li>
        )}
      </ul>
    </div>
  );
}
