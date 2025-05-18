import React, { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function GroupedReflectionsPage() {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/mcp/reflections/grouped/")
      .then((res) => {
        setData(res);
      })
      .catch((err) => console.error("Failed to fetch reflections:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-4">Loading reflections...</div>;

  return (
    <div className="container mt-4">
      <h2 className="mb-4">🧠 Grouped Reflections</h2>

      {Object.entries(data).map(([group, reflections]) => (
        <div key={group} className="mb-5">
          <h4 className="text-primary border-bottom pb-1">{group}</h4>
          {reflections.map((r, i) => (
            <div key={`${group}-${r.id || i}`} className="card mb-3 shadow-sm">
              <div className="card-body">
                <h5 className="card-title">{r.title || "🧠 Untitled Reflection"}</h5>
                <p className="card-text">
                  <strong>Summary:</strong> {r.summary || "No summary available."}
                </p>
                <div className="text-muted small">
                  🧠 {r.created_at
                        ? new Date(r.created_at).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" })
                        : "Unknown Date"}
                </div>
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}