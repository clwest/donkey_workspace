// frontend/api/assistants.js
import { ASSISTANTS_API } from "../config/api";
import apiFetch from "../utils/apiClient";

export async function generateAssistantThought(slug) {
  const res = await fetch(
    `${ASSISTANTS_API}/${slug}/log_thought/`,
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
    `${ASSISTANTS_API}/thoughts/${id}/mutate/`,
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
    `${ASSISTANTS_API}/${slug}/memory-to-project/`,
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
    `${ASSISTANTS_API}/${slug}/suggest-delegation/`,
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
  const res = await fetch(`${ASSISTANTS_API}/suggest/`, {
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
    `${ASSISTANTS_API}/${slug}/clarify_prompt/`,
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
    `${ASSISTANTS_API}/${slug}/failure_log/`,
  );
  if (!res.ok) {
    throw new Error("Failed to load failure log");
  }
  return res.json();
}

export async function runDriftCheck(slug) {
  const res = await fetch(
    `${ASSISTANTS_API}/${slug}/drift-check/`,
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
    `${ASSISTANTS_API}/${slug}/self-assess/`,
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
    `${ASSISTANTS_API}/${slug}/recover/`,
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
    `${ASSISTANTS_API}/${slug}/regenerate_plan/`,
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
    `${ASSISTANTS_API}/suggest_switch/`,
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
  const res = await fetch(`${ASSISTANTS_API}/switch/`, {
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
    `${ASSISTANTS_API}/${slug}/evaluate-collaboration/`,
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

export async function evaluateContinuity(slug, body = {}) {
  const res = await fetch(
    `${ASSISTANTS_API}/${slug}/evaluate-continuity/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to evaluate continuity");
  }
  return res.json();
}

export async function fetchCollaborationLogs(projectId) {
  const res = await fetch(
    `${ASSISTANTS_API}/projects/${projectId}/collaboration_logs/`,
  );
  if (!res.ok) {
    throw new Error("Failed to load collaboration logs");
  }
  return res.json();
}

export async function fetchCollaborationProfile(slug) {
  const res = await fetch(
    `${ASSISTANTS_API}/${slug}/collaboration_profile/`,
  );
  if (!res.ok) {
    throw new Error("Failed to load collaboration profile");
  }
  return res.json();
}

export async function planFromThread(slug, body) {
  const res = await fetch(
    `${ASSISTANTS_API}/${slug}/plan-from-thread/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to generate plan");
  }
  return res.json();
}

export async function assignTrainingDocuments(slug, agentId, documentIds) {
  const res = await fetch(
    `${ASSISTANTS_API}/${slug}/assign-training/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_id: agentId, document_ids: documentIds }),
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to assign training");
  }
  return res.json();
}

export async function evaluateAgentTraining(slug, agentId) {
  const res = await fetch(
    `${ASSISTANTS_API}/${slug}/evaluate-agent/${agentId}/`,
  );
  if (!res.ok) {
    throw new Error("Failed to evaluate agent training");
  }
  return res.json();
}

export async function fetchRecentReflections(slug) {
  const res = await fetch(`${ASSISTANTS_API}/${slug}/reflections/recent/`);
  if (!res.ok) {
    throw new Error("Failed to load recent reflections");
  }
  return res.json();
}

export const fetchDeploymentReadiness = (id) =>
  apiFetch(`/assistants/${id}/deploy/`);

export const triggerDeployment = (id, body) =>
  apiFetch(`/assistants/${id}/deploy/`, { method: "POST", body });

export const fetchToolAssignments = (id) =>
  apiFetch(`/assistants/${id}/tools/`);

export const saveToolAssignments = (id, body) =>
  apiFetch(`/assistants/${id}/tools/`, { method: "POST", body });

export async function createPrimaryAssistant() {
  const res = await apiFetch("/assistants/primary/create/", { method: "POST" });
  if (!res || res.error) {
    throw new Error("Failed to create primary assistant");
  }
  return res;
}

export async function assignPrimaryAssistant(slug) {
  return apiFetch(`/assistants/${slug}/assign-primary/`, { method: "PATCH" });
}

export async function setAssistantActive(slug, active) {
  return apiFetch(`/assistants/${slug}/`, {
    method: "PATCH",
    body: { is_active: active },
  });
}

export async function fetchAssistantDashboard(slug) {
  const res = await apiFetch(`/assistants/${slug}/dashboard/`);
  if (!res || res.error) {
    throw new Error("Failed to load dashboard");
  }
  return res;
}

// Guarded creation to prevent unintended spawns. Only execute when
// `userInitiated` is explicitly true.
export async function createAssistantFromDocuments(body, opts = {}) {
  const { userInitiated = false } = opts;
  if (!userInitiated) {
    console.warn(
      "createAssistantFromDocuments ignored – call missing userInitiated flag"
    );
    return null;
  }
  if (window.location.search.includes("debug_spawn=true")) {
    console.log("[spawn-debug] createAssistantFromDocuments", body);
  }
  return apiFetch("/assistants/from-documents/", {
    method: "POST",
    body,
  });
}

export function onboardAssistant(id, body) {
  return apiFetch(`/assistants/${id}/onboard/`, {
    method: "POST",
    body,
  });
}

export function initiateDream(id, body) {
  return apiFetch(`/assistants/${id}/dream/initiate/`, {
    method: "POST",
    body,
  });
}

export async function reviewIngestDocument(slug, docId) {
  try {
    return await apiFetch(`/assistants/${slug}/review-ingest/${docId}/`, {
      method: "POST",
    });
  } catch (err) {
    console.error("Failed to review ingest", err);
    return null;
  }
}
