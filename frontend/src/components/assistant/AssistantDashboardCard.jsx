import { useState, useRef } from "react";
import PropTypes from "prop-types";
import AssistantCard from "./AssistantCard";
import apiFetch from "@/utils/apiClient";
import { fetchBootStatus, fetchBootProfile } from "@/api/assistants";
import TrustBadge from "./TrustBadge";
import useAssistantCardData from "../../hooks/useAssistantCardData";

export default function AssistantDashboardCard({ assistant }) {
  const [bootStatus, setBootStatus] = useState(null);
  const [docStats, setDocStats] = useState(null);
  const [bootProfile, setBootProfile] = useState(null);
  const [loadDeep, setLoadDeep] = useState(false);
  const hoverRef = useRef(null);

  const { profile, diagnostic, memoryStatus } = useAssistantCardData(
    assistant.slug,
    { enabled: loadDeep },
  );

  async function loadExtra() {
    if (bootStatus && bootProfile && docStats) return;
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
      const docs = await apiFetch(
        `/assistants/${assistant.slug}/memory-documents/`,
      );
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
  const ragBadge = diagnostic
    ? `\uD83E\uDDE0 RAG Health: Fallback ${(diagnostic.fallback_rate * 100).toFixed(1)}%, Drift ${profile?.score_components?.drift_fixes_recent ?? 0}`
    : null;

  const handleEnter = () => {
    if (hoverRef.current) return;
    hoverRef.current = setTimeout(() => {
      setLoadDeep(true);
      loadExtra();
    }, 300);
  };

  const handleLeave = () => {
    if (hoverRef.current) {
      clearTimeout(hoverRef.current);
      hoverRef.current = null;
    }
  };

  return (
    <div
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
      className={`p-1 rounded shadow-sm ${profile ? borderColor : ""}`}
    >
      <AssistantCard
        assistant={assistant}
        to={`/assistants/${assistant.slug}`}
      />
      {profile && (
        <div className="mt-1 small text-muted">
          <span>{profile.trust_score}/100</span>
          <TrustBadge label={badgeLabel} />
          {bootWarning && (
            <span className="ms-2" title="Boot issues">
              ⚠️
            </span>
          )}
          {(assistant.certified_rag_ready ||
            diagnostic?.certified_rag_ready) && (
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
              {ragOk ? "✅" : "⚠️"}{" "}
              {Math.round(diagnostic.glossary_success_rate * 100)}% glossary •{" "}
              {Math.round(diagnostic.fallback_rate * 100)}% fallback
              <a
                href={`/assistants/${assistant.slug}/diagnostic_report/`}
                className="ms-1 text-decoration-underline"
              >
                View Diagnostic
              </a>
            </span>
          )}
          {ragBadge && <span className="ms-2">{ragBadge}</span>}
          {profile.trusted_anchor_pct != null && (
            <span className="ms-2">
              🛡️ Trusted Anchors: {profile.trusted_anchor_pct}%
            </span>
          )}
          {memoryStatus && (
            <span className="ms-2">
              {memoryStatus === "hydrated" && (
                <span className="badge bg-success">Memory OK</span>
              )}
              {memoryStatus === "paused" && (
                <span className="badge bg-warning text-dark">
                  Memory Paused
                </span>
              )}
              {memoryStatus === "error" && (
                <span className="badge bg-danger">Memory Error</span>
              )}
            </span>
          )}
          {bootStatus && bootProfile && (
            <span className="ms-2 d-block">
              Documents Linked: {bootStatus.linked_documents} | Chunks
              Available: {bootStatus.embedded_chunks} | Glossary Anchors:{" "}
              {bootProfile.glossary_anchors?.active} | Status:{" "}
              {assistant.rag_certified ? "Certified ✅" : "Needs Review ❗"}
            </span>
          )}
        </div>
      )}
      {docStats && docStats.embedded === 0 && (
        <div className="alert alert-warning mt-2">
          ⚠️ No embedded chunks.{" "}
          <a href={`/assistants/${assistant.slug}/rag_debug/`}>
            Recheck Documents
          </a>
        </div>
      )}
    </div>
  );
}

AssistantDashboardCard.propTypes = {
  assistant: PropTypes.object.isRequired,
};
