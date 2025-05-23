import apiFetch from "../../../utils/apiClient";
import { toast } from "react-toastify";

export default function RitualQuickActionsLayer({ assistantId }) {
  const trigger = async (ritual) => {
    try {
      await apiFetch(`/assistants/${assistantId}/ritual/${ritual}/`, { method: "POST" });
      toast.success(`${ritual} ritual triggered`);
    } catch (err) {
      console.error("Failed to trigger ritual", err);
      toast.error("Ritual failed");
    }
  };

  return (
    <div className="fixed-bottom bg-light border-top p-2 d-flex justify-content-center gap-2">
      <button className="btn btn-outline-secondary btn-sm" onClick={() => trigger("reflect")}>Reflect</button>
      <button className="btn btn-outline-secondary btn-sm" onClick={() => trigger("recall")}>Recall</button>
      <button className="btn btn-outline-secondary btn-sm" onClick={() => trigger("rebirth")}>Rebirth</button>
      <button className="btn btn-outline-secondary btn-sm" onClick={() => trigger("anchor")}>Anchor</button>
    </div>
  );
}
