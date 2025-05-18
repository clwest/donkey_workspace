
import React from "react";
import { useGroupedReflection } from "../../hooks/useGroupedReflection";

export default function GroupedReflectionPanel() {
  const { reflection, loading, runSummarize } = useGroupedReflection();

  return (
    <div className="my-4 p-3 border rounded bg-white">
      <h5>🧠 Grouped DevDoc Reflection</h5>
      <button
        className="btn btn-outline-success mb-3"
        onClick={runSummarize}
        disabled={loading}
      >
        {loading ? "Analyzing..." : "🧠 Summarize All DevDocs"}
      </button>

      {reflection && (
        <div>
          <h6 className="text-muted mb-2">
            {new Date(reflection.created_at).toLocaleString()}
          </h6>
          <p>
            <strong>{reflection.summary}</strong>
          </p>

          {(() => {
            try {
              let content = reflection.event.trim();

              // 🔥 Fix: Remove ```json or ``` fences
              if (content.startsWith("```json") || content.startsWith("```")) {
                content = content.replace(/```json\\s*/i, "").replace(/```$/, "").trim();
              }

              const groups = JSON.parse(content);
              return groups.map((group, idx) => (
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
              ));
            } catch (e) {
              console.warn("🧨 Failed to parse grouped reflection JSON:", e);
              return (
                <pre className="bg-light p-2 rounded text-danger">
                  Failed to parse grouped reflection JSON.
                  <br />
                  Raw output:
                  <br />
                  {reflection.event}
                </pre>
              );
            }
          })()}
        </div>
      )}
    </div>
  );
}
