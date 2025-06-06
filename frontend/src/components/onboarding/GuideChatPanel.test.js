import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import GuideChatPanel from "./GuideChatPanel";

// Mock hooks and api
jest.mock("@/hooks/useUserInfo", () => () => ({ show_guide: true }));

let triggered = null;
jest.mock("@/hooks/useAssistantHints", () => () => ({ triggerHint: (id) => (triggered = id) }));

jest.mock("@/utils/apiClient", () => async () => ({ reply: "hi", hint_suggestion: "glossary_tour", ui_action: "goto:/assistants/a" }));

renderToStaticMarkup(<GuideChatPanel />);
if (triggered !== "glossary_tour") {
  throw new Error("GuideChatPanel did not trigger hint");
}
console.log("GuideChatPanel test passed");
