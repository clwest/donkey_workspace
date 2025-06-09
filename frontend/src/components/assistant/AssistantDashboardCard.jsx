import { useState } from "react";
import PropTypes from "prop-types";
import AssistantCard from "./AssistantCard";
import apiFetch from "@/utils/apiClient";
import TrustBadge from "./TrustBadge";

export default function AssistantDashboardCard({ assistant }) {
  const [profile, setProfile] = useState(null);

  async function load() {
    if (profile) return;
    try {
      const data = await apiFetch(`/assistants/${assistant.slug}/trust_profile/`);
      setProfile(data);
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
        </div>
      )}
    </div>
  );
}

AssistantDashboardCard.propTypes = {
  assistant: PropTypes.object.isRequired,
};
