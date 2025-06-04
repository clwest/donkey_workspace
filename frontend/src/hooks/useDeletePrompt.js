import { toast } from "react-toastify";
import apiFetch from "../utils/apiClient";

export async function deletePromptWithFallback(slug) {
  try {
    const res = await apiFetch(`/prompts/${slug}/delete/`, {
      method: "DELETE",
    });

    if (!res.ok) {
      const data = await res.json();
      if (res.status === 400 && data?.error?.includes("in use")) {
        return { needsForce: true };
      }
      throw new Error(data?.error || "Failed to delete prompt.");
    }

    toast.success("Prompt deleted successfully");
    return { deleted: true };
  } catch (err) {
    console.error("Prompt deletion failed", err);
    toast.error(err.message || "Deletion error");
    return { error: err.message };
  }
}

export async function forceDeletePrompt(slug) {
  const res = await apiFetch(`/prompts/${slug}/delete/?force=true`, {
    method: "DELETE",
  });

  if (res.ok) {
    toast.warn("Prompt force-deleted");
    return { deleted: true };
  } else {
    const data = await res.json();
    toast.error(data?.error || "Force deletion failed");
    return { error: data?.error };
  }
}
