import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import IdentityCardEditor from "./IdentityCardEditor";

const html = renderToStaticMarkup(
  <IdentityCardEditor assistantId={1} show={false} onClose={() => {}} />
);
if (!html.includes("Edit Identity Card")) {
  throw new Error("IdentityCardEditor render failed");
}
console.log("IdentityCardEditor test passed");
