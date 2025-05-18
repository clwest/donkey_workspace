const BACKEND_URL = "http://localhost:8000"; // Your Django server!

export async function fetchPrompts() {
  const response = await fetch(`${BACKEND_URL}/api/prompts/search/`);
  if (!response.ok) {
    throw new Error("Failed to fetch prompts");
  }
  return response.json();
}

export async function fetchPromptBySlug(slug) {
  const response = await fetch(`${BACKEND_URL}/api/prompts/${slug}/`);
  if (!response.ok) {
    throw new Error("Failed to fetch prompt");
  }
  return response.json();
}
