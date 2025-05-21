import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ThreadMoodSparkline from "./ThreadMoodSparkline";

const moods = [
  { mood: "neutral", created_at: new Date().toISOString() },
  { mood: "anxious", created_at: new Date().toISOString() },
];
const html = renderToStaticMarkup(<ThreadMoodSparkline moods={moods} />);
if (!html.includes("svg")) {
  throw new Error("Mood sparkline render failed");
}
console.log("ThreadMoodSparkline test passed");
