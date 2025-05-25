export function getUserIdFromToken() {
  const token = localStorage.getItem("access");
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.user_id || payload.userId || payload.id || null;
  } catch (err) {
    console.error("Failed to decode auth token", err);
    return null;
  }
}
