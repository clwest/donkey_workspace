export async function fetchPerformanceMetrics(assistantId) {
  const res = await fetch(
    `http://localhost:8000/api/metrics/performance/${assistantId}/`
  );
  if (!res.ok) {
    throw new Error("Failed to load metrics");
  }
  return res.json();
}
