import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function PromptFeedbackPage() {
  const { id } = useParams();
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    if (!id) return;
    apiFetch(`/feedback/prompts/${id}/`)
      .then(setFeedback)
      .catch((err) => console.error("Failed to load prompt feedback", err));
  }, [id]);

  return (
    <div className="container my-4">
      <h3>Prompt Feedback</h3>
      <pre>{JSON.stringify(feedback, null, 2)}</pre>
    </div>
  );
}
