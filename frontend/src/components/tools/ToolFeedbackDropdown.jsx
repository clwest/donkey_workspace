import { useState } from "react";
import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";

export default function ToolFeedbackDropdown({ usageId }) {
  const [value, setValue] = useState("");

  const submit = async (fb) => {
    try {
      await apiFetch(`/tools/feedback/${usageId}/`, {
        method: "POST",
        body: { feedback: fb },
      });
      toast.success("Thanks! We'll learn from this.");
    } catch (err) {
      console.error("Feedback error", err);
      toast.error("Failed to submit feedback");
    }
  };

  return (
    <select
      className="form-select form-select-sm w-auto mt-1"
      value={value}
      onChange={(e) => {
        const fb = e.target.value;
        setValue(fb);
        if (fb) submit(fb);
      }}
    >
      <option value="">🛠️ Feedback</option>
      <option value="perfect">✅ Perfect</option>
      <option value="helpful">👍 Helpful</option>
      <option value="not_helpful">👎 Not Helpful</option>
      <option value="irrelevant">❌ Irrelevant</option>
      <option value="error">⚠️ Error</option>
    </select>
  );
}
