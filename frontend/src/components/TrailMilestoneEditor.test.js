import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import TrailMilestoneEditor from "./TrailMilestoneEditor";

const marker = { id: "1" };
const html = renderToStaticMarkup(
  <TrailMilestoneEditor marker={marker} />
);
if (!html.includes("Save")) {
  throw new Error("TrailMilestoneEditor render failed");
}
console.log("TrailMilestoneEditor test passed");
