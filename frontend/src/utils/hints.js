export function recordHintSeen(slug, id) {
  if (!slug || !id) return;
  localStorage.setItem(`hint_seen_${slug}_${id}`, "1");
}
