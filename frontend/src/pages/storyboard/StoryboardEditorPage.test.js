import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { NarrativeTimeline } from "./StoryboardEditorPage";

const mock = [{ id: 1, title: "Intro", description: "Start" }];
const html = renderToStaticMarkup(<NarrativeTimeline events={mock} />);
if (!html.includes("Intro")) {
  throw new Error("Render failed");
}
console.log("Storyboard test passed");
