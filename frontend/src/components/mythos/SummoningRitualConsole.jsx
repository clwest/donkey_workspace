import { useLocation } from "react-router-dom";
import usePostSummonRouter from "../../onboarding/summon";
import apiFetch from "../../utils/apiClient";

export default function SummoningRitualConsole() {
  const location = useLocation();
  const postSummon = usePostSummonRouter();
  const toneParam = location.state?.tone || "";
  const tagParam = location.state?.tag || "";
  const path = location.state?.path || "";

  const defaults = {
    memory: { tone: "reflective", tag: "memory" },
    codex: { tone: "precise", tag: "codex" },
    ritual: { tone: "observant", tag: "ritual" },
  }[path] || { tone: "neutral", tag: "general" };

  const tone = toneParam || defaults.tone;
  const tag = tagParam || defaults.tag;

  const summon = async () => {
    try {
      const assistant = await apiFetch("/assistants/", {
        method: "POST",
        body: {
          name: tag || "Summoned Assistant",
          specialty: tag || "general",
          tone,
          path,
        },
      });
      postSummon(assistant);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container my-4">
      <h2>Summoning Ritual</h2>
      <p>
        Summoning <strong>{tag}</strong> with tone <em>{tone}</em> via path {path}
      </p>
      <button className="btn btn-success" onClick={summon}>
        Summon Assistant
      </button>
    </div>
  );
}
