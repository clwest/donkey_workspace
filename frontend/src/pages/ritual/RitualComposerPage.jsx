import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualComposerPage() {
  const [drafts, setDrafts] = useState(null);

  useEffect(() => {
    apiFetch("/ritual/composer/")
      .then(setDrafts)
      .catch((err) => console.error("Failed to load composer", err));
  }, []);

  return (
    <div className="container my-4">
      <h3>Ritual Composer</h3>
      <pre>{JSON.stringify(drafts, null, 2)}</pre>
    </div>
  );
}
