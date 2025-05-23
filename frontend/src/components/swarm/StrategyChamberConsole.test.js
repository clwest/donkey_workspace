import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import StrategyChamberConsole from "./StrategyChamberConsole";

const html = renderToStaticMarkup(<StrategyChamberConsole />);
if (!html.includes("Strategy Chambers")) {
  throw new Error("StrategyChamberConsole render failed");
}
console.log("StrategyChamberConsole test passed");
