import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AssistantNotificationPanel({ assistantId }) {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (!assistantId) return;
    async function load() {
      try {
        const res = await apiFetch(`/assistants/${assistantId}/notifications/`);
        setNotifications(res);
      } catch (err) {
        console.error("Failed to load notifications", err);
      }
    }
    load();
  }, [assistantId]);

  if (notifications.length === 0) {
    return <div className="notification-panel">No alerts</div>;
  }

  return (
    <div className="notification-panel">
      <h5>Alerts</h5>
      <ul>
        {notifications.map((n) => (
          <li key={n.id}>
            <strong>{n.alert_type}</strong>: {n.message}
          </li>
        ))}
      </ul>
    </div>
  );
}
