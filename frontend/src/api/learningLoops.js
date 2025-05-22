export async function triggerAdaptiveLoop(assistantId) {
  const res = await fetch(
    `http://localhost:8000/api/learning-loops/trigger/${assistantId}/`,
    { method: "POST" }
  );
  if (!res.ok) {
    throw new Error("Failed to trigger adaptive loop");
  }
  return res.json();
}
