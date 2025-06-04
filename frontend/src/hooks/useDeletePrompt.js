import { toast } from "react-toastify";
import apiFetch from "../utils/apiClient";

export async function deletePromptWithFallback(slug) {
  try {
    await apiFetch(`/prompts/${slug}/delete/`, {
      method: "DELETE",
    });

    toast.success("Prompt deleted successfully");
    return { deleted: true };
  } catch (err) {
    console.error("Prompt deletion failed", err);
    const msg = err.message || "";
    if (msg.includes("Prompt in use")) {
      return { needsForce: true };
    }
    toast.error(msg || "Deletion error");
    return { error: msg };
  }
}

export async function forceDeletePrompt(slug) {
  try {
    await apiFetch(`/prompts/${slug}/delete/?force=true`, {
      method: "DELETE",
    });
    toast.warn("Prompt force-deleted");
    return { deleted: true };
  } catch (err) {
    const msg = err.message || "";
    toast.error(msg || "Force deletion failed");
    return { error: msg };
  }
}
