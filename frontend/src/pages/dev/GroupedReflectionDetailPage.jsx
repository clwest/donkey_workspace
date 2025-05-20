import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import { jsonrepair } from "jsonrepair";
import { useNavigate } from "react-router-dom";


export default function GroupedReflectionDetailPage() {
  const { id } = useParams();
  const [reflection, setReflection] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) {
      console.warn("GroupedReflectionDetailPage: missing reflection id");
      return;
    }
    const loadReflection = async () => {
      try {
        const res = await apiFetch(`/mcp/dev_docs/grouped/${id}/`);
        console.log(res)
        setReflection(res);
      } catch (err) {
        console.error("❌ Failed to load reflection detail:", err);
      } finally {
        setLoading(false);
      }
    };

    loadReflection();
  }, [id]);

  if (loading) return <div className="container mt-4">Loading reflection...</div>;

  if (!reflection)
    return <div className="container mt-4">❌ Reflection not found.</div>;

  let groups = [];
  try {
    const cleaned = reflection.raw_json
      .replace(/^```json\s*/i, "")
      .replace(/```\s*$/, "")
      .trim();
    groups = JSON.parse(jsonrepair(cleaned));
  } catch (e) {
    return (
      <div className="container mt-4">
        <h2>Grouped Reflection Error</h2>
        <p className="text-danger">❌ Failed to parse JSON</p>
        <pre className="bg-light p-2 rounded">{reflection.raw_json}</pre>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h2 className="mb-3">🧠 Reflection from {new Date(reflection.created_at).toLocaleString()}</h2>
      <button className="btn btn-link" onClick={() => navigate("/grouped-reflections")}>
        ← Back to Reflections
      </button>
      <p>
        <strong>{reflection.summary}</strong>
      </p>

      {groups.map((group, idx) => (
        <div key={idx} className="mb-4 p-3 border rounded bg-light shadow-sm">
          <h5 className="mb-2">🧠 {group.group_title}</h5>
          <p>{group.group_summary}</p>

          <div className="mt-2">
            <strong>📄 Related Docs:</strong>
            <ul className="mb-2">
              {group.related_document_titles?.map((title, i) => (
                <li key={i}>{title}</li>
              ))}
            </ul>
          </div>

          <div className="mt-2">
            <strong>✅ Suggestions / TODOs:</strong>
            <ul>
              {group.suggestions_or_todos?.map((todo, i) => (
                <li key={i}>{todo}</li>
              ))}
            </ul>
          </div>
        </div>
      ))}
    </div>
  );
}