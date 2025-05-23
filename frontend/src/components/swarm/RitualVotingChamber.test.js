import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import RitualVotingChamber from "./RitualVotingChamber";

const html = renderToStaticMarkup(<RitualVotingChamber />);
if (!html.includes("Ritual Votes")) {
  throw new Error("RitualVotingChamber render failed");
}
console.log("RitualVotingChamber test passed");
