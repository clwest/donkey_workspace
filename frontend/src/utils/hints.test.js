import { recordHintSeen } from "./hints.js";

global.localStorage = {
  store: {},
  setItem(key, value) { this.store[key] = value; },
  getItem(key) { return this.store[key]; },
};

recordHintSeen("a", "rag_intro");
if (localStorage.getItem("hint_seen_a_rag_intro") !== "1") {
  throw new Error("recordHintSeen failed");
}
console.log("hints util test passed");
