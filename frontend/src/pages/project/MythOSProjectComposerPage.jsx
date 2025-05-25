import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythOSProjectComposerPage() {
  const [project, setProject] = useState(null);

  useEffect(() => {
    apiFetch("/project/composer/")
      .then(setProject)
      .catch((err) => console.error("Failed to load project composer", err));
  }, []);

  return (
    <div className="container my-4">
      <h3>Project Composer</h3>
      <pre>{JSON.stringify(project, null, 2)}</pre>
    </div>
  );
}
