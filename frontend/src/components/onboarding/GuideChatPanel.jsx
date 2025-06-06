import { useState } from "react";
import apiFetch from "@/utils/apiClient";
import useUserInfo from "@/hooks/useUserInfo";
import useAssistantHints from "@/hooks/useAssistantHints";
import TourProgressBar from "./TourProgressBar";

const QUICK_PROMPTS = [
  "What's a MythPath?",
  "Why glossary terms matter",
  "How do assistants learn?",
  "What happens after I finish onboarding?",
];

export default function GuideChatPanel() {
  const userInfo = useUserInfo();
  const { triggerHint } = useAssistantHints(userInfo?.primary_assistant_slug);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Welcome to MythOS! I'm your guide. Ask me anything, or click below to explore…",
    },
  ]);
  const [input, setInput] = useState("");

  if (!userInfo?.show_guide) return null;

  const send = async (text) => {
    const msg = text || input;
    if (!msg) return;
    setMessages((m) => [...m, { role: "user", content: msg }]);
    setInput("");
    try {
      const res = await apiFetch("/onboarding/guide_chat/", {
        method: "POST",
        body: { message: msg },
      });
      if (res.reply) {
        setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
      }
      if (res.hint_suggestion) {
        triggerHint(res.hint_suggestion);
      }
      if (res.ui_action) {
        if (res.ui_action.startsWith("goto:")) {
          window.location.href = res.ui_action.replace("goto:", "");
        }
      }
    } catch (err) {
      console.error("guide chat", err);
    }
  };

  const dismiss = async () => {
    try {
      await apiFetch("/onboarding/guide_chat/", { method: "POST", body: { dismiss: true } });
    } catch {}
    window.location.reload();
  };

  return (
    <div
      className="position-fixed end-0 bottom-0 m-3"
      style={{ width: "280px", zIndex: 1050 }}
    >
      <div className="card shadow-sm">
        <div className="card-header d-flex justify-content-between align-items-center">
          <strong>MythOS Guide</strong>
          <button type="button" className="btn-close" onClick={dismiss}></button>
        </div>
        <div className="card-body" style={{ maxHeight: "260px", overflowY: "auto" }}>
          <TourProgressBar assistantSlug={userInfo?.primary_assistant_slug} />
          {messages.map((m, idx) => (
            <div key={idx} className="mb-2 small">
              {m.content}
            </div>
          ))}
          <div className="d-flex flex-wrap gap-1 mb-2">
            {QUICK_PROMPTS.map((q) => (
              <button
                key={q}
                className="btn btn-sm btn-outline-secondary"
                onClick={() => send(q)}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
        <div className="card-footer p-2">
          <input
            className="form-control form-control-sm"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask a question…"
          />
        </div>
      </div>
    </div>
  );
}
