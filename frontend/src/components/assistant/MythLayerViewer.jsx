import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythLayerViewer({ assistantSlug }) {
  const [layer, setLayer] = useState(null);

  useEffect(() => {
    if (!assistantSlug) return;
    apiFetch(`/assistants/${assistantSlug}/myth-layer/`)
      .then(setLayer)
      .catch(() => setLayer(null));
  }, [assistantSlug]);

  if (!layer) return <p className="text-muted">No mythos available.</p>;

  return (
    <div className="my-3">
      <h5>{layer.assistant_name} Mythos</h5>
      <p>{layer.origin_story}</p>
      {layer.legendary_traits?.epithet && (
        <p className="fw-bold">Epithet: {layer.legendary_traits.epithet}</p>
      )}
      {layer.legendary_traits?.notable_arcs && (
        <ul>
          {layer.legendary_traits.notable_arcs.map((a, i) => (
            <li key={i}>{a}</li>
          ))}
        </ul>
      )}
      <small className="text-muted">
        Last updated: {new Date(layer.last_updated).toLocaleString()}
      </small>
    </div>
  );
}
