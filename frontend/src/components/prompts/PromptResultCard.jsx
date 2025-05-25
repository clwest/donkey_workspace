// frontend/components/PromptResultCard.jsx
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";

export default function PromptResultCard({ promptText, title = "Untitled Prompt" }) {
  const navigate = useNavigate();

  async function handleUsePrompt() {
    try {
      const res = await apiFetch(`/memory/save/`, {
        method: "POST",
        body: {
          event: "Prompt Created via Assistant",
          memory_type: "reflection",
          title,
          content: promptText,
        },
      });

      if (res.ok) {
        toast.success("🧠 Prompt saved to memory!");
        navigate("/prompts/create", { state: { title, content: promptText } });
      } else {
        toast.error("❌ Failed to save to memory");
      }
    } catch (err) {
      console.error(err);
      toast.error("❌ Error saving memory");
    }
  }

  return (
    <div className="card bg-light border rounded p-3 mt-4">
      <h5 className="mb-3">Generated Prompt</h5>
      <pre className="bg-white p-3 rounded" style={{ whiteSpace: "pre-wrap" }}>{promptText}</pre>
      <button className="btn btn-primary mt-3" onClick={handleUsePrompt}>
        ✍️ Use in New Prompt
      </button>
    </div>
  );
}
