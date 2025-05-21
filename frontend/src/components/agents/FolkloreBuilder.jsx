import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function FolkloreBuilder() {
  const [season, setSeason] = useState("");
  const [draft, setDraft] = useState("");
  const [result, setResult] = useState(null);

  const handleGenerate = async () => {
    try {
      const data = await apiFetch("/assistants/generate-folklore/", {
        method: "POST",
        body: { season },
      });
      setResult(data);
      setDraft(data.text);
    } catch (err) {
      console.error("Failed to generate", err);
    }
  };

  const handlePublish = async () => {
    try {
      await apiFetch("/story/lore/", {
        method: "POST",
        body: { text: draft, season },
      });
      setDraft("");
    } catch (err) {
      console.error("Failed to publish", err);
    }
  };

  return (
    <div className="my-3">
      <h5>Folklore Builder</h5>
      <div className="mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="Season"
          value={season}
          onChange={(e) => setSeason(e.target.value)}
        />
      </div>
      <button className="btn btn-sm btn-primary mb-2" onClick={handleGenerate}>
        Generate
      </button>
      {result && (
        <div>
          <textarea
            className="form-control mb-2"
            rows="6"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
          <button className="btn btn-sm btn-success" onClick={handlePublish}>
            Publish to Lore
          </button>
        </div>
      )}
    </div>
  );
}
