import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import MemoryPalaceNavigator from "./MemoryPalaceNavigator";

const html = renderToStaticMarkup(<MemoryPalaceNavigator />);
if (!html.includes("Memory Palaces")) {
  throw new Error("MemoryPalaceNavigator render failed");
}
console.log("MemoryPalaceNavigator test passed");
