// frontend/api/assistants.js

export async function generateAssistantThought(slug) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/log_thought/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    }
  );

  if (!res.ok) {
    throw new Error("Failed to generate thought.");
  }

  return res.json();
}
