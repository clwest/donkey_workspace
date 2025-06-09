import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import apiFetch from "@/utils/apiClient";

export default function useDemoRecap(sessionId) {
  const [recap, setRecap] = useState(null);
  const [showRecap, setShowRecap] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  useEffect(() => {
    if (!sessionId) return;
    const recapKey = `recap_shown_${sessionId}`;
    if (localStorage.getItem(recapKey)) return;
    apiFetch(`/assistants/demo_recap/${sessionId}/`)
      .then((d) => {
        if (d && d.messages_sent > 0 && !d.converted) {
          setRecap(d);
          setShowRecap(true);
        }
      })
      .catch((err) => {
        if (!String(err).includes("404")) {
          console.error('Failed to fetch recap', err);
        }
      });
  }, [sessionId]);

  const closeRecap = (skip = false) => {
    localStorage.setItem(`recap_shown_${sessionId}`, "1");
    setShowRecap(false);
    if (skip) toast.info("Recap skipped");
  };

  const openRecap = () => setShowRecap(true);

  const triggerFeedback = () => {
    const key = `feedback_done_${sessionId}`;
    if (!localStorage.getItem(key)) {
      setShowFeedback(true);
    }
  };

  const closeFeedback = () => {
    localStorage.setItem(`feedback_done_${sessionId}`, "1");
    setShowFeedback(false);
  };

  const recapSkipped = !!localStorage.getItem(`recap_shown_${sessionId}`);

  return {
    recap,
    showRecap,
    openRecap,
    closeRecap,
    recapSkipped,
    showFeedback,
    triggerFeedback,
    closeFeedback,
  };
}
