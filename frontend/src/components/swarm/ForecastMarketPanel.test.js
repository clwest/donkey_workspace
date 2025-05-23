import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import ForecastMarketPanel from "./ForecastMarketPanel";

const html = renderToStaticMarkup(<ForecastMarketPanel />);
if (!html.includes("Forecasting Market Ledgers")) {
  throw new Error("ForecastMarketPanel render failed");
}
console.log("ForecastMarketPanel test passed");
