export async function executeWorkflow(definitionId) {
  const res = await fetch("http://localhost:8000/api/workflows/execute/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workflow_definition_id: definitionId }),
  });
  if (!res.ok) {
    throw new Error("Failed to execute workflow");
  }
  return res.json();
}
