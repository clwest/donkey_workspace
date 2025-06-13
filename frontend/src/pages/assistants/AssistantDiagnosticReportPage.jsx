import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function AssistantDiagnosticReportPage() {
  const { slug } = useParams();
  const [report, setReport] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/assistants/${slug}/diagnostic_report/`);
        setReport(data);
      } catch {
        setReport(null);
      }
    }
    load();
  }, [slug]);

  if (!report) return <div className="container my-4">No report available.</div>;

  return (
    <div className="container my-4">
      <h3 className="mb-3">Diagnostic Report</h3>
      <p>
        <strong>Generated:</strong> {new Date(report.generated_at).toLocaleString()}
      </p>
      <p>
        <strong>Fallback Rate:</strong> {(report.fallback_rate * 100).toFixed(1)}%
      </p>
      <p>
        <strong>Glossary Success:</strong> {(report.glossary_success_rate * 100).toFixed(1)}%
      </p>
      <p>
        <strong>Avg Chunk Score:</strong> {report.avg_chunk_score.toFixed(2)}
      </p>
      <p>
        <strong>Logs:</strong> {report.rag_logs_count}
      </p>
    </div>
  );
}
