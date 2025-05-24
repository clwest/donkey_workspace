import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ReflectionPlaybackTimeline from "./ReflectionPlaybackTimeline";

const html = renderToStaticMarkup(<ReflectionPlaybackTimeline />);
if (!html.includes("Reflection Playback")) {
  throw new Error("ReflectionPlaybackTimeline render failed");
}
console.log("ReflectionPlaybackTimeline test passed");
