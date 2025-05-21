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

export async function toggleBookmark(id, isBookmarked, label = "Important") {
  const endpoint = isBookmarked ? "unbookmark" : "bookmark";
  const res = await fetch(`${BACKEND_URL}/api/memory/${id}/${endpoint}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: isBookmarked ? null : JSON.stringify({ label }),
  });
  if (!res.ok) {
    throw new Error("Failed to toggle bookmark");
  }
  return res.json();
}
