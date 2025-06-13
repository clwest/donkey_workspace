import { useState } from "react";
import PropTypes from "prop-types";
import AssistantCard from "./AssistantCard";
import apiFetch from "@/utils/apiClient";
import { fetchBootStatus, fetchDiagnosticReport, fetchBootProfile } from "@/api/assistants";
import TrustBadge from "./TrustBadge";

export default function AssistantDashboardCard({ assistant }) {
  const [profile, setProfile] = useState(null);
  const [bootStatus, setBootStatus] = useState(null);
  const [diagnostic, setDiagnostic] = useState(null);
  const [docStats, setDocStats] = useState(null);
  const [bootProfile, setBootProfile] = useState(null);

  async function load() {
    if (profile && bootStatus && diagnostic && bootProfile && docStats) return;
    try {
      const data = await apiFetch(`/assistants/${assistant.slug}/trust_profile/`);
      setProfile(data);
    } catch (err) {
      console.error(err);
    }
    try {
      const status = await fetchBootStatus(assistant.slug);
      setBootStatus(status);
    } catch (err) {
      console.error(err);
    }
    try {
      const prof = await fetchBootProfile(assistant.slug);
      setBootProfile(prof);
    } catch (err) {
      console.error(err);
    }
    try {
      const diag = await fetchDiagnosticReport(assistant.slug);
      setDiagnostic(diag);
    } catch (err) {
      console.error(err);
    }
    try {
      const docs = await apiFetch(`/assistants/${assistant.slug}/memory-documents/`);
      let total = 0;
      let embedded = 0;
      docs.forEach((d) => {
        total += d.total_chunks;
        embedded += d.embedded_chunks;
      });
      setDocStats({ total, embedded });
    } catch (err) {
      console.error(err);
    }
  }

  const badgeLabel = profile
    ? profile.trust_level === "ready"
      ? "trusted"
      : profile.trust_level === "needs_attention"
      ? "unreliable"
      : "neutral"
    : null;
  const bootWarning = bootStatus
    ? [
        bootStatus.has_context,
        bootStatus.has_intro_memory,
        bootStatus.has_origin_reflection,
        bootStatus.has_profile,
        bootStatus.has_narrative_thread,
      ].some((v) => v === false)
    : false;
  const borderColor =
    profile?.trust_level === "ready"
      ? "border-success"
      : profile?.trust_level === "needs_attention"
      ? "border-danger"
      : "border-warning";
  const ragOk = diagnostic && diagnostic.fallback_rate < 0.2;

  return (
    <div onMouseEnter={load} className={`p-1 rounded shadow-sm ${profile ? borderColor : ""}`}>
      <AssistantCard assistant={assistant} to={`/assistants/${assistant.slug}`} />
      {profile && (
        <div className="mt-1 small text-muted">
          <span>{profile.trust_score}/100</span>
          <TrustBadge label={badgeLabel} />
          {bootWarning && <span className="ms-2" title="Boot issues">⚠️</span>}
          {(assistant.certified_rag_ready || diagnostic?.certified_rag_ready) && (
            <>
              <span className="badge bg-success ms-2" title="RAG Certified">
                🎖
              </span>
              {assistant.rag_certification_date && (
                <span className="ms-1" title="RAG certification date">
                  {assistant.rag_certification_date.split("T")[0]}
                </span>
              )}
              <a
                href={`/static/certifications/${assistant.slug}_rag_cert.md`}
                className="ms-1"
                title="View certification"
              >
                📄
              </a>
            </>
          )}
          {diagnostic && (
            <span className="ms-2">
              {ragOk ? "✅" : "⚠️"} {Math.round(diagnostic.glossary_success_rate * 100)}% glossary • {Math.round(diagnostic.fallback_rate * 100)}% fallback
              <a
                href={`/assistants/${assistant.slug}/diagnostic_report/`}
                className="ms-1 text-decoration-underline"
              >
                View Diagnostic
              </a>
            </span>
          )}
          {bootStatus && bootProfile && (
            <span className="ms-2 d-block">
              Documents Linked: {bootStatus.linked_documents} | Chunks Available: {bootStatus.embedded_chunks}
              {" "}| Glossary Anchors: {bootProfile.glossary_anchors?.active}
              {" "}| Status:{" "}
              {assistant.rag_certified ? "Certified ✅" : "Needs Review ❗"}
            </span>
          )}
        </div>
      )}
      {docStats && docStats.embedded === 0 && (
        <div className="alert alert-warning mt-2">
          ⚠️ No embedded chunks. <a href={`/assistants/${assistant.slug}/rag_debug/`}>Recheck Documents</a>
        </div>
      )}
    </div>
  );
}

AssistantDashboardCard.propTypes = {
  assistant: PropTypes.object.isRequired,
};
