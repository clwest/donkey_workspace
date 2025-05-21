import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MemoryCompressionPanel({ threadId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!threadId) return;
    apiFetch(`/memory/threads/${threadId}/compress/`)
      .then(setData)
      .catch(() => {});
  }, [threadId]);

  if (!data) return <div>Loading compression...</div>;

  const tokenSavings =
    (data.full_text ? data.full_text.length : 0) -
    (data.compressed ? data.compressed.length : 0);

  return (
    <div className="mt-3">
      <h5>Compressed Summary</h5>
      <pre style={{ whiteSpace: "pre-wrap" }}>{data.summary}</pre>
      <div className="text-muted">Token savings: {tokenSavings}</div>
    </div>
  );
}
