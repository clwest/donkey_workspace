import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function DemoOverlayPanel({ slug, sessionId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!slug || !sessionId) return;
    apiFetch(`/assistants/${slug}/demo_overlay/?session_id=${sessionId}`)
      .then(setData)
      .catch(() => {});
  }, [slug, sessionId]);

  if (!data) return null;

  return (
    <div className="demo-overlay border rounded p-3 mt-3">
      <h5 className="mb-2">What your assistant noticed</h5>
      {data.anchors.length > 0 && (
        <div className="mb-2">
          {data.anchors.map((a) => (
            <span key={a.slug} className="badge bg-info text-dark me-1">
              💡 {a.label}
            </span>
          ))}
        </div>
      )}
      {data.tags.length > 0 && (
        <div className="mb-2">
          {data.tags.map((t) => (
            <span key={t.slug} className="badge bg-secondary me-1">
              🧠 {t.slug}
            </span>
          ))}
        </div>
      )}
      {data.reflection_snippet && (
        <div className="small fst-italic mt-2 border-top pt-2">
          {data.reflection_snippet}
        </div>
      )}
    </div>
  );
}
