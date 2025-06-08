import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function DemoTipsSidebar({ slug, sessionId, onHelpful }) {
  const [tips, setTips] = useState([]);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    if (!slug) return;
    const params = sessionId ? `?session_id=${sessionId}` : "";
    apiFetch(`/assistants/${slug}/demo_tips/${params}`)
      .then((data) => {
        const list = data.tips || [];
        list.forEach((t) => {
          if (localStorage.getItem(`demo_tip_${slug}_${t.id}`) === "1") {
            t.dismissed = true;
          }
        });
        setTips(list);
      })
      .catch((err) => console.error("demo tips", err));
  }, [slug]);

  const dismiss = (id) => {
    localStorage.setItem(`demo_tip_${slug}_${id}`, "1");
    setTips((t) => t.map((x) => (x.id === id ? { ...x, dismissed: true } : x)));
  };

  const markHelpful = async (id) => {
    try {
      await apiFetch(`/assistants/${slug}/demo_tips/`, {
        method: "PATCH",
        body: { tip_id: id, helpful: true, session_id: sessionId },
      });
      if (onHelpful) onHelpful();
    } catch (err) {
      console.error("demo tip helpful", err);
    }
    dismiss(id);
  };

  const markAll = () => {
    tips.forEach((t) => localStorage.setItem(`demo_tip_${slug}_${t.id}`, "1"));
    setTips((t) => t.map((x) => ({ ...x, dismissed: true })));
  };

  const completed = tips.filter((t) => t.dismissed).length;
  const percent = tips.length ? Math.round((completed / tips.length) * 100) : 0;

  if (!tips.length) return null;

  return (
    <div
      className="position-fixed top-50 end-0 translate-middle-y bg-light border rounded shadow p-3"
      style={{ width: collapsed ? "40px" : "260px", zIndex: 1050 }}
    >
      <button
        className="btn btn-sm btn-outline-secondary mb-2"
        onClick={() => setCollapsed(!collapsed)}
      >
        {collapsed ? "▶" : "◀"}
      </button>
      {!collapsed && (
        <>
          <div className="d-flex justify-content-between align-items-center mb-2">
            <strong>Demo Tips</strong>
            <button
              className="btn btn-sm btn-outline-secondary"
              onClick={markAll}
            >
              Done
            </button>
          </div>
          <div className="progress mb-2" style={{ height: "4px" }}>
            <div className="progress-bar" style={{ width: `${percent}%` }} />
          </div>
          <ul
            className="list-unstyled small mb-0"
            style={{ maxHeight: "60vh", overflowY: "auto" }}
          >
            {tips.map((tip) =>
              tip.dismissed ? null : (
                <li key={tip.id} className="mb-3">
                  <strong>{tip.title}</strong>
                  <div className="text-muted">{tip.text}</div>
                  <button
                    className="btn btn-sm btn-outline-primary mt-1 me-1"
                    onClick={() => markHelpful(tip.id)}
                  >
                    Helpful
                  </button>
                  <button
                    className="btn btn-sm btn-outline-secondary mt-1"
                    onClick={() => dismiss(tip.id)}
                  >
                    Skip
                  </button>
                </li>
              ),
            )}
          </ul>
        </>
      )}
    </div>
  );
}
