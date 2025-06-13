import { useState } from "react";
import PropTypes from "prop-types";
import AssistantCard from "./AssistantCard";
import apiFetch from "@/utils/apiClient";
import { fetchBootStatus } from "@/api/assistants";
import TrustBadge from "./TrustBadge";

export default function AssistantDashboardCard({ assistant }) {
  const [profile, setProfile] = useState(null);
  const [bootStatus, setBootStatus] = useState(null);

  async function load() {
    if (profile && bootStatus) return;
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
  return (
    <div onMouseEnter={load} className={`p-1 rounded shadow-sm ${profile ? borderColor : ""}`}>
      <AssistantCard assistant={assistant} to={`/assistants/${assistant.slug}`} />
      {profile && (
        <div className="mt-1 small text-muted">
          <span>{profile.trust_score}/100</span>
          <TrustBadge label={badgeLabel} />
          {bootWarning && <span className="ms-2" title="Boot issues">⚠️</span>}
          {assistant.last_rag_certified_at && (
            <>
              <span className="ms-2" title="RAG certification date">
                {assistant.last_rag_certified_at.split("T")[0]}
              </span>
              <a
                href={`/static/certifications/${assistant.slug}_rag_cert.md`}
                className="ms-1"
                title="View certification"
              >
                📄
              </a>
            </>
          )}
        </div>
      )}
    </div>
  );
}

AssistantDashboardCard.propTypes = {
  assistant: PropTypes.object.isRequired,
};
