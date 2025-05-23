import { useLocation } from "react-router-dom";
import usePostSummonRouter from "../../onboarding/summon";

export default function SummoningRitualConsole() {
  const location = useLocation();
  const postSummon = usePostSummonRouter();
  const tone = location.state?.tone || "";
  const tag = location.state?.tag || "";

  const summon = () => {
    const assistant = { id: "new" };
    postSummon(assistant);
  };

  return (
    <div className="container my-4">
      <h2>Summoning Ritual</h2>
      <p>
        Summoning <strong>{tag}</strong> with tone <em>{tone}</em>
      </p>
      <button className="btn btn-success" onClick={summon}>
        Summon Assistant
      </button>
    </div>
  );
}
