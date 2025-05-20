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

export async function mutateThought(id, style = "clarify") {
  const res = await fetch(
    `http://localhost:8000/api/assistants/thoughts/${id}/mutate/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ style }),
    }
  );

  if (!res.ok) {
    throw new Error("Failed to mutate thought");
  }

  return res.json();
}
export async function planProjectFromMemory(slug, body) {
  const res = await fetch(`http://localhost:8000/api/assistants/${slug}/memory-to-project/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to plan project");
  }
  return res.json();
}

export async function suggestDelegation(slug, body) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/suggest-delegation/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "include",
    }
  );
  if (!res.ok) {
    throw new Error("Failed to get recommendation");
  }
  return res.json();
}

export async function suggestAssistant(body) {
  const res = await fetch("http://localhost:8000/api/assistants/suggest/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to get suggestion");
  }
  return res.json();
}

export async function clarifyPrompt(slug, text) {
  const res = await fetch(`http://localhost:8000/api/assistants/${slug}/clarify_prompt/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to clarify prompt");
  }
  return res.json();
}

export async function fetchFailureLog(slug) {
  const res = await fetch(`http://localhost:8000/api/assistants/${slug}/failure_log/`);
  if (!res.ok) {
    throw new Error("Failed to load failure log");
  }
  return res.json();
}
