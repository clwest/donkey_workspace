import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import CommonModal from "../../CommonModal";
import apiFetch from "../../../utils/apiClient";

export default function ProjectRoleModal({ projectId, show, onClose, onSaved }) {
  const [assistants, setAssistants] = useState([]);
  const [assistantId, setAssistantId] = useState("");
  const [roleName, setRoleName] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    if (show) {
      apiFetch("/assistants/").then(setAssistants);
    }
  }, [show]);

  async function handleAssign() {
    if (!assistantId || !roleName) return;
    try {
      await apiFetch(`/assistants/projects/${projectId}/roles/`, {
        method: "POST",
        body: { assistant: assistantId, role_name: roleName, description },
      });
      setAssistantId("");
      setRoleName("");
      setDescription("");
      if (onSaved) onSaved();
      toast.success("Role assigned!");
    } catch (err) {
      console.error("Failed to assign role", err);
      toast.error(err.message || "Failed to assign role");
    }
  }

  return (
    <CommonModal
      show={show}
      onClose={onClose}
      title="Assign Role"
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
          <button className="btn btn-primary" onClick={handleAssign}>
            ➕ Assign
          </button>
        </>
      }
    >
      <div>
        <select
          className="form-select mb-2"
          value={assistantId}
          onChange={(e) => setAssistantId(e.target.value)}
        >
          <option value="">Select assistant...</option>
          {assistants.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>
        <input
          type="text"
          className="form-control mb-2"
          placeholder="Role name"
          value={roleName}
          onChange={(e) => setRoleName(e.target.value)}
        />
        <textarea
          className="form-control mb-2"
          placeholder="Description"
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
    </CommonModal>
  );
}
