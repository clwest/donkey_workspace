import { useState } from "react";
import { toast } from "react-toastify";
import apiFetch from "../../../utils/apiClient";

export default function DelegationSummaryPanel({ slug }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSummarize = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/assistants/${slug}/summarize_delegations/`, {
        method: "POST",
      });
      setSummary(res.summary);
      toast.success("Delegation summary generated!");
    } catch (err) {
      console.error("Summary failed", err);
      toast.error("Failed to summarize delegations");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-3">
      <button
        className="btn btn-outline-info mb-2"
        onClick={handleSummarize}
        disabled={loading}
      >
        {loading ? "Summarizing..." : "🧠 Summarize Delegations"}
      </button>
      {summary && (
        <div className="alert alert-secondary" style={{ whiteSpace: "pre-wrap" }}>
          {summary}
        </div>
      )}
    </div>
  );
}
