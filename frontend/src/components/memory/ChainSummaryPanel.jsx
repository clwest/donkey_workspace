import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function ChainSummaryPanel({ summary }) {
  if (!summary) {
    return <div className="alert alert-secondary">No summary generated yet.</div>;
  }
  return (
    <div className="bg-light p-3 rounded">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{summary}</ReactMarkdown>
    </div>
  );
}
