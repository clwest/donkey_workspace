import apiFetch from "../utils/apiClient";

export async function executeWorkflow(definitionId) {
  const res = await apiFetch(`/workflows/execute/`, {
    method: "POST",
    body: { workflow_definition_id: definitionId },
  });
  return res;
}
