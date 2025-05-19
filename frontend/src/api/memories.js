const BACKEND_URL = "http://localhost:8000";

export async function mutateMemory(id, style = "clarify") {
  const res = await fetch(`${BACKEND_URL}/api/memory/${id}/mutate/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ style }),
  });
  if (!res.ok) {
    throw new Error("Failed to mutate memory");
  }
  return res.json();
}
