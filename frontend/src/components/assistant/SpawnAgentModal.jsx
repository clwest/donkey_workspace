import { useState } from "react";
import Modal from "../CommonModal";
import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";

export default function SpawnAgentModal({ slug, show, onClose, contextType = "memory", contextId = "" }) {
  const [type, setType] = useState(contextType);
  const [id, setId] = useState(contextId);
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSpawn = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/assistants/${slug}/spawn/`, {
        method: "POST",
        body: { context_type: type, context_id: id, reason },
      });
      toast.success(`Spawned agent ${res.slug}`);
      onClose(true);
    } catch (err) {
      console.error(err);
      toast.error("Failed to spawn agent");
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onClose={() => onClose(false)} title="Spawn Delegated Agent">
      <div className="mb-2">
        <label>Context Type</label>
        <select className="form-select" value={type} onChange={(e) => setType(e.target.value)}>
          <option value="memory">Memory</option>
          <option value="document">Document</option>
        </select>
      </div>
      <div className="mb-2">
        <label>Context ID</label>
        <input className="form-control" value={id} onChange={(e) => setId(e.target.value)} />
      </div>
      <div className="mb-3">
        <label>Reason</label>
        <input className="form-control" value={reason} onChange={(e) => setReason(e.target.value)} />
      </div>
      <button className="btn btn-primary" onClick={handleSpawn} disabled={loading}>
        {loading ? "Spawning..." : "Spawn"}
      </button>
    </Modal>
  );
}
