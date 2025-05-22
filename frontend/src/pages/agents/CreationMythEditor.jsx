import { useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CreationMythEditor({ assistantId }) {
  const [story, setStory] = useState("");
  const [tags, setTags] = useState("");
  const [alignment, setAlignment] = useState("");

  const save = async () => {
    await apiFetch("/agents/creation-myths/", {
      method: "POST",
      body: JSON.stringify({
        assistant: assistantId,
        mythic_origin_story: story,
        symbolic_tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
        cosmological_alignment: alignment,
      }),
    });
    setStory("");
    setTags("");
    setAlignment("");
  };

  return (
    <div>
      <textarea
        className="form-control mb-2"
        placeholder="Origin story"
        value={story}
        onChange={(e) => setStory(e.target.value)}
      />
      <input
        className="form-control mb-2"
        placeholder="Tags comma separated"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
      />
      <input
        className="form-control mb-2"
        placeholder="Cosmological Alignment"
        value={alignment}
        onChange={(e) => setAlignment(e.target.value)}
      />
      <button className="btn btn-primary" onClick={save}>
        Save Myth
      </button>
    </div>
  );
}
