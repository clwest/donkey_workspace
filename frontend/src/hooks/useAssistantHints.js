import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";
import { recordHintSeen } from "@/utils/hints";

export default function useAssistantHints(slug) {
  const [hints, setHints] = useState([]);

  const load = async () => {
    if (!slug) return;
    try {
      const data = await apiFetch(`/assistants/${slug}/hints/`);
      const list = data?.hints || [];
      list.forEach((h) => {
        if (localStorage.getItem(`hint_dismiss_${slug}_${h.id}`) === "1") {
          h.dismissed = true;
        }
      });
      setHints(list);
    } catch (err) {
      console.error("hint fetch", err);
    }
  };

  const dismissHint = async (id) => {
    localStorage.setItem(`hint_dismiss_${slug}_${id}`, "1");
    setHints((h) => h.map((x) => (x.id === id ? { ...x, dismissed: true } : x)));
    try {
      await apiFetch(`/assistants/${slug}/hints/${id}/dismiss/`, { method: "POST" });
    } catch (err) {
      console.error("dismiss hint", err);
    }
  };

  const triggerHint = (id) => {
    if (!slug) return;
    recordHintSeen(slug, id);
  };

  useEffect(() => {
    load();
  }, [slug]);

  return { hints, dismissHint, refreshHints: load, triggerHint };
}
