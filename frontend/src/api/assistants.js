// frontend/api/assistants.js

export async function generateAssistantThought(slug) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/log_thought/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    },
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
    },
  );

  if (!res.ok) {
    throw new Error("Failed to mutate thought");
  }

  return res.json();
}
export async function planProjectFromMemory(slug, body) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/memory-to-project/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "include",
    },
  );
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
    },
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
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/clarify_prompt/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to clarify prompt");
  }
  return res.json();
}

export async function fetchFailureLog(slug) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/failure_log/`,
  );
  if (!res.ok) {
    throw new Error("Failed to load failure log");
  }
  return res.json();
}

export async function runDriftCheck(slug) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/drift-check/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to run drift check");
  }
  return res.json();
}


export async function runSelfAssessment(slug) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/self-assess/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to run self assessment");
  }
  return res.json();
}

export async function recoverAssistant(slug) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/recover/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to run recovery");
  }
  return res.json();
}

export async function regeneratePlan(slug, body = {}) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/regenerate_plan/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to regenerate plan");
  }
  return res.json();
}

export async function suggestSwitch(sessionId) {
  const res = await fetch(
    "http://localhost:8000/api/assistants/suggest_switch/",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to get switch suggestion");
  }
  return res.json();
}

export async function switchAssistant(
  sessionId,
  assistantSlug,
  reason = "switch",
) {
  const res = await fetch("http://localhost:8000/api/assistants/switch/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      assistant_slug: assistantSlug,
      reason,
    }),
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to switch assistant");
  }
  return res.json();
}

export async function evaluateCollaboration(slug, body) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/evaluate-collaboration/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to evaluate collaboration");
  }
  return res.json();
}

export async function fetchCollaborationLogs(projectId) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/projects/${projectId}/collaboration_logs/`,
  );
  if (!res.ok) {
    throw new Error("Failed to load collaboration logs");
  }
  return res.json();
}

export async function fetchCollaborationProfile(slug) {
  const res = await fetch(
    `http://localhost:8000/api/assistants/${slug}/collaboration_profile/`,
  );
  if (!res.ok) {
    throw new Error("Failed to load collaboration profile");
  }
  return res.json();
}
