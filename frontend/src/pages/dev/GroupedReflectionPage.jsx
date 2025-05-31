import React from "react";
import { useGroupedReflection } from "../../hooks/useGroupedReflection";
import GroupedReflectionHistoryPanel from "../../components/dev/GroupedReflectionHistoryPanel";
import { jsonrepair } from "jsonrepair";
import { useNavigate } from "react-router-dom";
import { downloadFile } from "../../utils/downloadFile";

export default function GroupedReflectionPage() {
  const { reflection, loading, runSummarize } = useGroupedReflection();
  const navigate = useNavigate();


  const exportJson = () => {
    const content = reflection.event
      .replace(/^```json\s*/i, "")
      .replace(/```\s*$/, "")
      .trim();
    downloadFile(content, "grouped_reflection.json", "application/json");
  };

  const exportMarkdown = () => {
    try {
      let content = reflection.event
        .replace(/^```json\s*/i, "")
        .replace(/```\s*$/, "")
        .trim();
      const fixed = jsonrepair(content);
      let parsed = JSON.parse(fixed);
      const groups = Array.isArray(parsed)
        ? parsed
        : parsed.groups || parsed.data || [];

      const md = groups
        .map(
          (g) => `## 🧠 ${g.group_title}

${g.group_summary}

**📄 Related Docs:**
${g.related_document_titles
            .map((d) => `- ${d}`)
            .join("\n")}

**✅ Suggestions / TODOs:**
${g.suggestions_or_todos
            .map((t) => `- ${t}`)
            .join("\n")}
`
        )
        .join("\n---\n");
      downloadFile(md, "grouped_reflection.md", "text/markdown");
    } catch (e) {
      alert("Failed to parse grouped reflection for markdown export.");
    }
  };

  const copyToClipboard = () => {
    const content = reflection.event
      .replace(/^```json\s*/i, "")
      .replace(/```\s*$/, "")
      .trim();
    navigator.clipboard.writeText(content).then(() => {
      alert("Copied grouped reflection JSON to clipboard!");
    });
  };

  const goToDoc = (title) => {
    const slug = title.replace(/\s+/g, "_").toLowerCase();
    navigate(`/dev-dashboard?doc=${slug}`);
  };

  return (
    <div className="container mt-4">
      <h2 className="mb-3">🧠 Grouped Dev Docs Reflection</h2>
      <GroupedReflectionHistoryPanel />
      <button
        className="btn btn-outline-success me-2"
        onClick={runSummarize}
        disabled={loading}
      >
        {loading ? "Analyzing..." : "🧠 Summarize All DevDocs"}
      </button>

      {reflection && (
        <div className="mt-4">
          <div className="mb-3">
            <button
              className="btn btn-sm btn-outline-secondary me-2"
              onClick={copyToClipboard}
            >
              📋 Copy
            </button>
            <button
              className="btn btn-sm btn-outline-secondary me-2"
              onClick={exportJson}
            >
              ⬇️ Export .json
            </button>
            <button
              className="btn btn-sm btn-outline-secondary"
              onClick={exportMarkdown}
            >
              ⬇️ Export .md
            </button>
          </div>

          <h6 className="text-muted mb-2">
            {new Date(reflection.created_at).toLocaleString()}
          </h6>
          <p>
            <strong>{reflection.summary}</strong>
          </p>

          {(() => {
            try {
              let content = reflection.event.trim();
              if (content.startsWith("```json") || content.startsWith("```")) {
                content = content
                  .replace(/^```json\s*/i, "")
                  .replace(/```\s*$/, "")
                  .trim();
              }

              const fixed = jsonrepair(content);
              let parsed = JSON.parse(fixed);
              const groups = Array.isArray(parsed)
                ? parsed
                : parsed.groups || parsed.data || [];
              return groups.map((group, idx) => (
                <div
                  key={idx}
                  className="mb-4 p-3 border rounded bg-light shadow-sm"
                >
                  <h5 className="mb-2">🧠 {group.group_title}</h5>
                  <p>{group.group_summary}</p>

                  <div className="mt-2">
                    <strong>📄 Related Docs:</strong>
                    <ul className="mb-2">
                      {group.related_document_titles?.map((title, i) => (
                        <li key={i}>
                          <a
                            href="#"
                            onClick={(e) => {
                              e.preventDefault();
                              goToDoc(title);
                            }}
                          >
                            {title}
                          </a>
                        </li>
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
