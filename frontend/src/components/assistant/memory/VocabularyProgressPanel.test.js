import VocabularyProgressPanel from "./VocabularyProgressPanel";
import { renderToStaticMarkup } from "react-dom/server";

const html = renderToStaticMarkup(<VocabularyProgressPanel assistantSlug="a1" />);
if (!html.includes("Vocabulary Progress")) {
  throw new Error("VocabularyProgressPanel render failed");
}
console.log("VocabularyProgressPanel test passed");
