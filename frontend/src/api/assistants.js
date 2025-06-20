// frontend/api/assistants.js
import { ASSISTANTS_API } from "../config/api";
import apiFetch from "../utils/apiClient";

export async function generateAssistantThought(slug) {
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/log_thought/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  if (!res.ok) {
    throw new Error("Failed to generate thought.");
  }

  return res.json();
}

export async function mutateThought(id, style = "clarify") {
  const res = await apiFetch(`${ASSISTANTS_API}/thoughts/${id}/mutate/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ style }),
  });

  if (!res.ok) {
    throw new Error("Failed to mutate thought");
  }

  return res.json();
}
export async function planProjectFromMemory(slug, body) {
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/memory-to-project/`, {
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
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/suggest-delegation/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to get recommendation");
  }
  return res.json();
}

export async function suggestAssistant(body) {
  const res = await apiFetch(`${ASSISTANTS_API}/suggest/`, {
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
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/clarify_prompt/`, {
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
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/failure_log/`);
  if (!res.ok) {
    throw new Error("Failed to load failure log");
  }
  return res.json();
}

export async function runDriftCheck(slug) {
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/drift-check/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to run drift check");
  }
  return res.json();
}

export async function runSelfAssessment(slug) {
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/self-assess/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to run self assessment");
  }
  return res.json();
}

export async function recoverAssistant(slug) {
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/recover/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to run recovery");
  }
  return res.json();
}

export async function regeneratePlan(slug, body = {}) {
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/regenerate_plan/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to regenerate plan");
  }
  return res.json();
}

export async function summarizeDelegations(slug) {
  const res = await apiFetch(
    `${ASSISTANTS_API}/${slug}/summarize_delegations/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    },
  );
  if (!res.ok) {
    throw new Error("Failed to summarize delegations");
  }
  return res.json();
}

export async function suggestSwitch(sessionId) {
  const res = await apiFetch(`${ASSISTANTS_API}/suggest_switch/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
    credentials: "include",
  });
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
  const res = await apiFetch(`${ASSISTANTS_API}/switch/`, {
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
  const res = await apiFetch(
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
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/evaluate-continuity/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to evaluate continuity");
  }
  return res.json();
}

export async function fetchCollaborationLogs(projectId) {
  const res = await apiFetch(
    `${ASSISTANTS_API}/projects/${projectId}/collaboration_logs/`,
  );
  if (!res.ok) {
    throw new Error("Failed to load collaboration logs");
  }
  return res.json();
}

export async function fetchCollaborationProfile(slug) {
  const res = await apiFetch(
    `${ASSISTANTS_API}/${slug}/collaboration_profile/`,
  );
  if (!res.ok) {
    throw new Error("Failed to load collaboration profile");
  }
  return res.json();
}

export async function planFromThread(slug, body) {
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/plan-from-thread/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to generate plan");
  }
  return res.json();
}

export async function assignTrainingDocuments(slug, agentId, documentIds) {
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/assign-training/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ agent_id: agentId, document_ids: documentIds }),
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to assign training");
  }
  return res.json();
}

export async function evaluateAgentTraining(slug, agentId) {
  const res = await apiFetch(
    `${ASSISTANTS_API}/${slug}/evaluate-agent/${agentId}/`,
  );
  if (!res.ok) {
    throw new Error("Failed to evaluate agent training");
  }
  return res.json();
}

export function cleanRecentMemories(slug) {
  return apiFetch(`/assistants/${slug}/clean_memories/`, { method: "POST" });
}

export function cleanStaleProjects(slug) {
  return apiFetch(`/assistants/${slug}/clean_projects/`, { method: "POST" });
}

export async function fetchRecentReflections(slug) {
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/reflections/recent/`);
  if (!res.ok) {
    throw new Error("Failed to load recent reflections");
  }
  return res.json();
}

export async function fetchGroupedRecentReflections(slug) {
  const res = await apiFetch(`${ASSISTANTS_API}/${slug}/recent-reflections/`);
  if (!res.ok) {
    throw new Error("Failed to load grouped reflections");
  }
  return res.json();
}

export async function fetchReflections(slug) {
  return apiFetch(`/assistants/${slug}/reflections/`);
}

export async function fetchDemoReflections(slug) {
  return apiFetch(`/assistants/${slug}/reflections/?demo_reflection=true`);
}

export async function composeDemoReflection(slug, sessionId, save = false) {
  return apiFetch(`/assistants/${slug}/demo_reflection/compose/`, {
    method: "POST",
    body: { session_id: sessionId, save_note: save },
  });
}

export const fetchDeploymentReadiness = (id) =>
  apiFetch(`/assistants/${id}/deploy/`);

export const triggerDeployment = (id, body) =>
  apiFetch(`/assistants/${id}/deploy/`, { method: "POST", body });

export const fetchAssistantTools = (slug) =>
  apiFetch(`/assistants/${slug}/tools/`);

export const assignAssistantTools = (slug, body) =>
  apiFetch(`/assistants/${slug}/tools/assign/`, { method: "POST", body });

export const reflectOnTools = (slug) =>
  apiFetch(`/assistants/${slug}/tools/reflect/`, { method: "POST" });

export const fetchToolConfidence = (slug) =>
  apiFetch(`/assistants/${slug}/tools/confidence/`);

export const recommendToolChanges = (slug, body = {}) =>
  apiFetch(`/assistants/${slug}/tools/recommend/`, { method: "POST", body });

export const fetchAssistantToolReflections = (slug) =>
  apiFetch(`/assistants/${slug}/tool_reflections/`);

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

export const fetchAssistantOverview = (slug) =>
  apiFetch(`/assistants/${slug}/overview/`);

export async function retryBirthReflection(slug) {
  return apiFetch(`/assistants/${slug}/reflection/retry/`, { method: "POST" });
}

// Guarded creation to prevent unintended spawns. Only execute when
// `userInitiated` is explicitly true.
export async function createAssistantFromDocuments(body, opts = {}) {
  const { userInitiated = false } = opts;
  if (!userInitiated) {
    console.warn(
      "createAssistantFromDocuments ignored – call missing userInitiated flag",
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

export async function createAssistantFromDemo(
  demoSlug,
  transcript = [],
  sessionId,
  variant,
  feedbackText,
  rating,
  retainPrompt = true,
) {
  return apiFetch(`/assistants/from_demo/`, {
    method: "POST",
    body: {
      demo_slug: demoSlug,
      transcript,
      demo_session_id: sessionId,
      comparison_variant: variant,
      feedback_text: feedbackText,
      rating,
      retain_starter_prompt: retainPrompt,
    },
  });
}

export function prepareCreationFromDemo(slug, transcript = []) {
  return apiFetch(`/assistants/${slug}/prepare_creation_from_demo/`, {
    method: "POST",
    body: { transcript },
  });
}

export function previewAssistantFromDemo(demoSlug, transcript = []) {
  return apiFetch(`/assistants/from_demo/preview/`, {
    method: "POST",
    body: { demo_slug: demoSlug, transcript },
  });
}

export function getDemoPreview(demoSlug, transcript = []) {
  return apiFetch(`/assistants/${demoSlug}/demo_preview/`, {
    method: "POST",
    body: { transcript },
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
  if (!docId || docId === "undefined") {
    console.warn(
      `[ReviewIngest] Skipping review - invalid document ID: ${docId}`
    );
    return null;
  }
  try {
    return await apiFetch(`/assistants/${slug}/review-ingest/${docId}/`, {
      method: "POST",
    });
  } catch (err) {
    console.error("Failed to review ingest", err);
    return null;
  }
}

export async function fetchBootProfile(slug) {
  const res = await apiFetch(`/assistants/${slug}/boot_profile/`);
  return res;
}

export async function fetchBootStatus(slug) {
  const res = await apiFetch(`/assistants/${slug}/boot-status/`);
  return res;
}

export async function repairAssistant(slug) {
  const res = await apiFetch(`/assistants/${slug}/repair/`, { method: "POST" });
  return res;
}

export async function runSelfTest(slug) {
  const res = await apiFetch(`/assistants/${slug}/selftest/`, {
    method: "POST",
  });
  return res;
}

export async function runRagSelfTest(slug, params) {
  const res = await apiFetch(`/assistants/${slug}/rag_self_test/`, {
    method: "POST",
    body: params,
  });
  return res;
}

export async function runAllSelfTests() {
  const res = await apiFetch(`/assistants/self_tests/run_all/`, {
    method: "POST",
  });
  return res;
}

export async function runRagDiagnostics(slug, body) {
  const res = await apiFetch(`/assistants/${slug}/diagnostics/`, {
    method: "POST",
    body,
  });
  return res;
}

export async function fetchRagDiagnostics(slug) {
  const res = await apiFetch(`/assistants/${slug}/diagnostics/`);
  return res;
}

export async function fetchRagDiagnosticsSummary(slug) {
  const res = await apiFetch(`/assistants/${slug}/rag_diagnostics/`);
  return res;
}

export async function fetchDiagnosticReport(slug) {
  try {
    return await apiFetch(`/assistants/${slug}/diagnostic_report/`);
  } catch (err) {
    if (err.status === 404) {
      return null;
    }
    throw err;
  }
}

export async function fetchDriftSuggestions(slug, params) {
  const res = await apiFetch(`/assistants/${slug}/drift_suggestions/`, {
    params,
  });
  return res.results || res;
}

export async function reviewFirstMessageDrift(slug) {
  const res = await apiFetch(`/assistants/${slug}/drift_suggestions/`, {
    method: "POST",
  });
  return res;
}

export async function fetchDriftFixes(slug, params) {
  const res = await apiFetch(`/assistants/${slug}/drift_fixes/`, { params });
  return res.results || res;
}

export async function fetchDriftSummary(slug) {
  const res = await apiFetch(`/assistants/${slug}/drift/summary/`);
  return res.results || res;
}

export async function retryContextRepair(contextId) {
  return apiFetch(`/embedding/repair/context/${contextId}/`, { method: "POST" });
}

export async function resetDemoAssistant(slug) {
  return apiFetch(`/assistants/${slug}/reset_demo/`, {
    method: "POST",
    allowUnauthenticated: true,
  });
}

export async function sendDemoFeedback(sessionId, feedbackText, rating) {
  return apiFetch(`/assistants/demo_feedback/`, {
    method: "POST",
    allowUnauthenticated: true,
    body: { session_id: sessionId, feedback_text: feedbackText, rating },
  });
}

export async function resetDemoSession(sessionId, fullReset = false) {
  return apiFetch(`/assistants/demo_session/reset/`, {
    method: "POST",
    allowUnauthenticated: true,
    params: fullReset ? { full_reset: true } : undefined,
    body: { session_id: sessionId },
  });
}

export async function fetchAssistantInsights(slug) {
  return apiFetch(`/assistants/${slug}/insights/`);
}

export async function reflectOnChat(slug) {
  return apiFetch(`/assistants/${slug}/reflect_on_chat/`, { method: "POST" });
}

export async function acceptInsight(slug, id) {
  return apiFetch(`/assistants/${slug}/insights/${id}/accept/`, { method: "POST" });
}

export async function rejectInsight(slug, id) {
  return apiFetch(`/assistants/${slug}/insights/${id}/reject/`, { method: "POST" });
}

export async function fetchRagDiagnosticLogs(params) {
  return apiFetch(`/devtools/rag_debug/`, { params });
}

export async function fetchReplayLogs(slug) {
  return apiFetch(`/assistants/${slug}/replay/`);
}

export async function runSymbolicReplay(slug) {
  return apiFetch(`/assistants/${slug}/replay/run/`, { method: "POST" });
}

export async function fetchDriftAudit(id) {
  return apiFetch(`/api/drift_audit/${id}/`);
}
