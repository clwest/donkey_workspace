import { useLocation, useNavigate } from "react-router-dom";

export default function SummoningRitualConsole() {
  const location = useLocation();
  const navigate = useNavigate();
  const tone = location.state?.tone || "";
  const tag = location.state?.tag || "";
  const path = location.state?.path || "custom";

  const proceed = () => {
    navigate("/assistants/create", {
      state: { tone, tag, mythpath: path },
    });
  };

  return (
    <div className="container my-4">
      <h2>Summoning Ritual</h2>
      <p>
        Summoning <strong>{tag}</strong> with tone <em>{tone}</em>
      </p>
      <button className="btn btn-success" onClick={proceed}>
        Continue to Creation
      </button>
    </div>
  );
}
