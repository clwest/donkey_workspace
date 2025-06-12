import { useEffect, useState } from "react";
import { fetchBootStatus, repairAssistant } from "../../api/assistants";
import { toast } from "react-toastify";

export default function AssistantBootStatusPanel({ slug }) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [repairing, setRepairing] = useState(false);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    fetchBootStatus(slug)
      .then(setStatus)
      .catch(() => toast.error("Failed to load boot status"))
      .finally(() => setLoading(false));
  }, [slug]);

  const handleRepair = async () => {
    setRepairing(true);
    try {
      await repairAssistant(slug);
      const data = await fetchBootStatus(slug);
      setStatus(data);
      toast.success("Repair triggered");
    } catch (err) {
      toast.error("Repair failed");
    } finally {
      setRepairing(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!status) return <div className="text-muted">Status unavailable.</div>;

  const rows = [
    ["Context linked", status.has_context],
    ["Intro memory", status.has_intro_memory],
    ["Origin reflection", status.has_origin_reflection],
    ["Profile", status.has_profile],
    ["Narrative thread", status.has_narrative_thread],
    ["Custom prompt", status.has_custom_prompt],
  ];
  const missing = rows.some(([, v]) => !v);

  return (
    <div>
      <h6 className="mt-2">Boot Status</h6>
      <ul className="list-unstyled small mb-2">
        {rows.map(([label, ok]) => (
          <li key={label}>{ok ? "✅" : "❌"} {label}</li>
        ))}
        <li>Documents: {status.rag_linked_docs}</li>
        <li>Chunk Health: {status.rag_chunk_health}</li>
      </ul>
      {missing && (
        <button className="btn btn-sm btn-primary" onClick={handleRepair} disabled={repairing}>
          {repairing ? "Repairing..." : "Repair Assistant"}
        </button>
      )}
    </div>
  );
}
