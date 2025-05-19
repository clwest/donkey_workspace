import { useEffect, useState } from "react";
import ProjectRoleModal from "./ProjectRoleModal";
import apiFetch from "../../../utils/apiClient";

export default function ProjectRolesRow({ projectId }) {
  const [roles, setRoles] = useState([]);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchRoles();
  }, [projectId]);

  async function fetchRoles() {
    const data = await apiFetch(`/assistants/projects/${projectId}/roles/`);
    setRoles(data);
  }

  return (
    <div className="mb-3">
      <div className="d-flex flex-wrap align-items-center gap-2">
        {roles.map((r) => (
          <span key={r.id} className="badge bg-secondary">
            {r.assistant_name} – {r.role_name}
          </span>
        ))}
        <button
          className="btn btn-sm btn-outline-primary"
          onClick={() => setShowModal(true)}
        >
          🎭 Assign Role
        </button>
      </div>
      <ProjectRoleModal
        projectId={projectId}
        show={showModal}
        onClose={() => setShowModal(false)}
        onSaved={() => {
          setShowModal(false);
          fetchRoles();
        }}
      />
    </div>
  );
}
