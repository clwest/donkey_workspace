import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RitualSyncManager from "./RitualSyncManager";

const html = renderToStaticMarkup(<RitualSyncManager />);
if (!html.includes("Ritual Sync Pulses")) {
  throw new Error("RitualSyncManager render failed");
}
console.log("RitualSyncManager test passed");
