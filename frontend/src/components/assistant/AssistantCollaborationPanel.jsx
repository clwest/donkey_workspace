import { useEffect, useState } from "react";
import {
  evaluateCollaboration,
  fetchCollaborationLogs,
  fetchCollaborationProfile,
} from "../../api/assistants";
import PropTypes from "prop-types";

export default function AssistantCollaborationPanel({
  assistantSlug,
  projectId,
}) {
  const [profile, setProfile] = useState(null);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const prof = await fetchCollaborationProfile(assistantSlug);
        setProfile(prof);
        if (projectId) {
          const data = await fetchCollaborationLogs(projectId);
          setLogs(data || []);
        }
      } catch (err) {
        console.error("Failed to load collaboration info", err);
      }
    }
    load();
  }, [assistantSlug, projectId]);

  if (!profile) return <div>Loading collaboration profile...</div>;

  return (
    <div className="card mb-3">
      <div className="card-header">Collaboration</div>
      <div className="card-body">
        <p>
          Style: <strong>{profile.collaboration_style}</strong>
        </p>
        <p>
          Conflict Resolution:{" "}
          <strong>{profile.preferred_conflict_resolution}</strong>
        </p>
        {logs.length > 0 && (
          <div>
            <h6>Recent Logs</h6>
            <ul>
              {logs.map((l) => (
                <li key={l.id}>
                  {l.mood_state} {l.style_conflict_detected && "⚠️"}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

AssistantCollaborationPanel.propTypes = {
  assistantSlug: PropTypes.string.isRequired,
  projectId: PropTypes.string,
};
