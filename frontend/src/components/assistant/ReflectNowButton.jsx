import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";

export default function ReflectNowButton({ slug, memoryId, projectId, docId }) {
  const trigger = async () => {
    if (!window.confirm("Run reflection now?")) return;
    try {
      await apiFetch(`/assistants/${slug}/reflect_now/`, {
        method: "POST",
        body: { memory_id: memoryId, project_id: projectId, doc_id: docId },
      });
      toast.success("Reflection triggered!");
    } catch (err) {
      console.error(err);
      toast.error("Failed to trigger reflection");
    }
  };

  return (
    <button className="btn btn-sm btn-outline-secondary" onClick={trigger}>
      Reflect Now
    </button>
  );
}
